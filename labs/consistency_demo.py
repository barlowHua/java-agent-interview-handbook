#!/usr/bin/env python3
"""Deterministic Outbox crash lab; Python standard library only.

Three SQLite files represent independent producer, broker, and consumer stores.
Workers really exit inside transactions using os._exit; this is NOT a Kafka,
RabbitMQ, replication, network-partition, or power-loss test.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile


CRASH_EXIT = 97


def connect(directory: Path, name: str) -> sqlite3.Connection:
    db = sqlite3.connect(directory / f"{name}.sqlite", isolation_level=None)
    db.execute("PRAGMA synchronous=FULL")
    db.execute("PRAGMA journal_mode=DELETE")
    return db


def initialize(directory: Path) -> None:
    schemas = {
        "producer": """
            CREATE TABLE orders (
                order_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL UNIQUE,
                points INTEGER NOT NULL CHECK(points > 0)
            );
            CREATE TABLE outbox (
                event_id TEXT PRIMARY KEY,
                order_id TEXT NOT NULL,
                points INTEGER NOT NULL,
                sent INTEGER NOT NULL DEFAULT 0
            );
        """,
        "broker": """
            CREATE TABLE messages (
                delivery_id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id TEXT NOT NULL,
                order_id TEXT NOT NULL,
                points INTEGER NOT NULL,
                acked INTEGER NOT NULL DEFAULT 0
            );
        """,
        "consumer": """
            CREATE TABLE inbox (
                consumer_name TEXT NOT NULL,
                event_id TEXT NOT NULL,
                PRIMARY KEY(consumer_name, event_id)
            );
            CREATE TABLE points_ledger (
                event_id TEXT PRIMARY KEY,
                order_id TEXT NOT NULL,
                points INTEGER NOT NULL
            );
            CREATE TABLE account (id INTEGER PRIMARY KEY, total INTEGER NOT NULL);
            INSERT INTO account VALUES (1, 0);
        """,
    }
    for name, schema in schemas.items():
        db = connect(directory, name)
        try:
            db.executescript(schema)
        finally:
            db.close()


def create_order(directory: Path, crash: str | None) -> None:
    db = connect(directory, "producer")
    try:
        db.execute("BEGIN IMMEDIATE")
        db.execute("INSERT INTO orders VALUES (?, ?, ?)", ("order-1", "req-1", 100))
        db.execute(
            "INSERT INTO outbox(event_id, order_id, points) VALUES (?, ?, ?)",
            ("event-1", "order-1", 100),
        )
        if crash == "producer_before_commit":
            os._exit(CRASH_EXIT)
        db.commit()
        if crash == "producer_after_commit":
            os._exit(CRASH_EXIT)
    finally:
        db.close()


def relay(directory: Path, crash: str | None = None) -> None:
    producer = connect(directory, "producer")
    broker = connect(directory, "broker")
    try:
        for row in producer.execute(
            "SELECT event_id, order_id, points FROM outbox WHERE sent=0 ORDER BY event_id"
        ).fetchall():
            broker.execute("BEGIN IMMEDIATE")
            broker.execute(
                "INSERT INTO messages(event_id, order_id, points) VALUES (?, ?, ?)", row
            )
            broker.commit()
            if crash == "relay_after_publish":
                os._exit(CRASH_EXIT)
            producer.execute("UPDATE outbox SET sent=1 WHERE event_id=?", (row[0],))
    finally:
        broker.close()
        producer.close()


def consume(directory: Path, crash: str | None = None) -> None:
    consumer = connect(directory, "consumer")
    broker = connect(directory, "broker")
    try:
        for delivery_id, event_id, order_id, points in broker.execute(
            "SELECT delivery_id,event_id,order_id,points FROM messages "
            "WHERE acked=0 ORDER BY delivery_id"
        ).fetchall():
            consumer.execute("BEGIN IMMEDIATE")
            inserted = consumer.execute(
                "INSERT INTO inbox(consumer_name,event_id) VALUES (?, ?) "
                "ON CONFLICT(consumer_name,event_id) DO NOTHING",
                ("points-service", event_id),
            ).rowcount
            if inserted == 1:
                consumer.execute(
                    "INSERT INTO points_ledger VALUES (?, ?, ?)",
                    (event_id, order_id, points),
                )
                consumer.execute("UPDATE account SET total=total+? WHERE id=1", (points,))
            if crash == "consumer_before_commit":
                os._exit(CRASH_EXIT)
            consumer.commit()
            if crash == "consumer_after_commit":
                os._exit(CRASH_EXIT)
            broker.execute("UPDATE messages SET acked=1 WHERE delivery_id=?", (delivery_id,))
    finally:
        broker.close()
        consumer.close()


def scalar(directory: Path, database: str, sql: str) -> int:
    db = connect(directory, database)
    try:
        return int(db.execute(sql).fetchone()[0])
    finally:
        db.close()


def check(actual: int, expected: int, message: str) -> None:
    if actual != expected:
        raise AssertionError(f"{message}: expected={expected}, actual={actual}")


def crash_worker(directory: Path, stage: str) -> None:
    result = subprocess.run(
        [sys.executable, str(Path(__file__).resolve()), "--worker", stage, "--directory", str(directory)],
        check=False,
        capture_output=True,
        text=True,
        timeout=10,
    )
    check(result.returncode, CRASH_EXIT, f"worker did not crash at {stage}; {result.stderr}")


def demo(directory: Path) -> None:
    initialize(directory)
    crash_worker(directory, "producer_before_commit")
    check(scalar(directory, "producer", "SELECT count(*) FROM orders"), 0, "uncommitted order")
    check(scalar(directory, "producer", "SELECT count(*) FROM outbox"), 0, "uncommitted event")
    print("PASS 1: producer crashed before commit; both order and outbox rolled back")

    crash_worker(directory, "producer_after_commit")
    check(scalar(directory, "producer", "SELECT count(*) FROM orders"), 1, "committed order")
    check(scalar(directory, "producer", "SELECT count(*) FROM outbox WHERE sent=0"), 1, "recoverable event")
    check(scalar(directory, "broker", "SELECT count(*) FROM messages"), 0, "not yet published")
    print("PASS 2: producer crashed after commit; pending event survives for relay")

    crash_worker(directory, "relay_after_publish")
    check(scalar(directory, "broker", "SELECT count(*) FROM messages"), 1, "first delivery")
    check(scalar(directory, "producer", "SELECT sent FROM outbox"), 0, "not marked sent")
    relay(directory)
    check(scalar(directory, "broker", "SELECT count(*) FROM messages"), 2, "duplicate publication")
    check(scalar(directory, "producer", "SELECT sent FROM outbox"), 1, "relay completed")
    print("PASS 3: relay crashed after publication; retry creates two deliveries of one event")

    crash_worker(directory, "consumer_before_commit")
    check(scalar(directory, "consumer", "SELECT count(*) FROM inbox"), 0, "inbox rolled back")
    check(scalar(directory, "consumer", "SELECT count(*) FROM points_ledger"), 0, "ledger rolled back")
    check(scalar(directory, "consumer", "SELECT total FROM account"), 0, "points rolled back")
    print("PASS 4: consumer crashed before commit; inbox, ledger, and points rolled back")

    crash_worker(directory, "consumer_after_commit")
    check(scalar(directory, "consumer", "SELECT total FROM account"), 100, "committed points")
    check(scalar(directory, "broker", "SELECT count(*) FROM messages WHERE acked=0"), 2, "ack lost")
    consume(directory)
    check(scalar(directory, "consumer", "SELECT count(*) FROM inbox"), 1, "one processed event")
    check(scalar(directory, "consumer", "SELECT count(*) FROM points_ledger"), 1, "one business entry")
    check(scalar(directory, "consumer", "SELECT total FROM account"), 100, "one business effect")
    check(scalar(directory, "broker", "SELECT count(*) FROM messages WHERE acked=0"), 0, "all acked")
    relay(directory)
    consume(directory)
    check(scalar(directory, "consumer", "SELECT total FROM account"), 100, "stable after another retry")
    print("PASS 5: consumer crashed after commit; redelivery is deduplicated, then acknowledged")
    print("RESULT: orders=1, outbox=1, broker_deliveries=2, ledger=1, points=100")
    print("All invariants passed. This verifies local protocol windows, not real middleware guarantees.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--worker", choices=[
        "producer_before_commit", "producer_after_commit", "relay_after_publish",
        "consumer_before_commit", "consumer_after_commit",
    ], help=argparse.SUPPRESS)
    parser.add_argument("--directory", type=Path, help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.worker:
        if args.directory is None:
            parser.error("worker requires --directory")
        if args.worker.startswith("producer_"):
            create_order(args.directory, args.worker)
        elif args.worker.startswith("relay_"):
            relay(args.directory, args.worker)
        else:
            consume(args.directory, args.worker)
    else:
        with tempfile.TemporaryDirectory(prefix="outbox-interview-lab-") as temporary:
            demo(Path(temporary))


if __name__ == "__main__":
    main()
