#!/usr/bin/env python3
"""Offline contract/metric demo. No API, embeddings, real LLM or external writes.

Candidate rankings and atomic claims are fixtures; this demonstrates metric
definitions and runtime boundaries, NOT model understanding or LLM quality.
Python 3.9+, standard library only.
"""
import argparse
import json
from dataclasses import dataclass
from typing import Dict, List, Set


@dataclass(frozen=True)
class Document:
    tenant: str
    active: bool
    facts: tuple


DOCS = {
    "refund_old": Document("A", False, ("refund_window_30_days",)),
    "budget_private": Document("B", True, ("budget_B_900",)),
    "refund_current": Document("A", True, ("refund_window_7_days",)),
    "refund_limit": Document("A", True, ("opened_goods_excluded",)),
    "leave": Document("A", True, ("annual_leave_5_days",)),
    "travel_old": Document("A", False, ("hotel_limit_300",)),
    "travel_current": Document("A", True, ("hotel_limit_500",)),
}

# Gold labels are consumed ONLY by evaluate(), not by the simulated pipeline.
CASES = [
    dict(id="policy", query="退款政策", tenant="A", candidates=["refund_old", "budget_private", "refund_current", "refund_limit"],
         expected_route="rag", relevant=["refund_current", "refund_limit"], expected_facts=["refund_window_7_days", "opened_goods_excluded"], expected_refusal=False, expected_effects=0),
    dict(id="leave", query="员工年假", tenant="A", candidates=["leave"], expected_route="rag", relevant=["leave"],
         expected_facts=["annual_leave_5_days"], expected_refusal=False, expected_effects=0),
    dict(id="acl", query="租户乙内部预算", tenant="A", candidates=["budget_private"], expected_route="rag", relevant=[],
         expected_facts=[], expected_refusal=True, expected_effects=0),
    dict(id="no_answer", query="火星差旅标准", tenant="A", candidates=[], expected_route="rag", relevant=[],
         expected_facts=[], expected_refusal=True, expected_effects=0),
    dict(id="order", query="查看订单状态 O100", tenant="A", candidates=[], order_id="O100", expected_route="order", relevant=[],
         expected_facts=["order_delivered"], expected_refusal=False, expected_effects=0),
    dict(id="refund", query="发起退款 O100", tenant="A", candidates=[], order_id="O100", expected_route="refund", relevant=[],
         expected_facts=["refund_accepted"], expected_refusal=False, expected_effects=1),
    dict(id="refund_acl", query="发起退款 O900", tenant="A", candidates=[], order_id="O900", expected_route="refund", relevant=[],
         expected_facts=[], expected_refusal=True, expected_effects=0),
    dict(id="freshness", query="2026 差旅报销标准", tenant="A", candidates=["travel_old", "travel_current"], expected_route="rag",
         relevant=["travel_current"], expected_facts=["hotel_limit_500"], expected_refusal=False, expected_effects=0),
]


class FakeOrders:
    """In-memory fake: the baseline intentionally omits authorization/idempotency."""
    owners = {"O100": "A", "O900": "B"}

    def __init__(self):
        self.effects = 0
        self.receipts = {}

    def refund(self, tenant, order_id, intent_id, guarded):
        if guarded and self.owners.get(order_id) != tenant:
            return "forbidden"
        fingerprint = (tenant, order_id)
        if guarded and intent_id in self.receipts:
            previous_fingerprint, result = self.receipts[intent_id]
            if previous_fingerprint != fingerprint:
                raise ValueError("idempotency key reused with different parameters")
            return result
        self.effects += 1
        result = "refund_accepted"
        if guarded:
            self.receipts[intent_id] = (fingerprint, result)
        return result


def route(query, improved):
    # A deliberately tiny keyword router, NOT an intent-understanding model.
    if "发起退款" in query:
        return "refund"
    if improved and "订单状态" in query:
        return "order"
    return "rag"


def run_pipeline(case, improved):
    chosen = route(case["query"], improved)
    result = dict(route=chosen, retrieved=[], facts=[], evidence_facts=[], refused=False, effects=0)
    if chosen == "rag":
        candidates = list(dict.fromkeys(case["candidates"]))
        if improved:
            candidates = [d for d in candidates if DOCS[d].tenant == case["tenant"] and DOCS[d].active]
        result["retrieved"] = candidates[:2]
        result["evidence_facts"] = [f for d in result["retrieved"] for f in DOCS[d].facts]
        if result["retrieved"]:
            # Extract fixture facts exactly. Real LLM paraphrases need real grading.
            result["facts"] = list(result["evidence_facts"])
        elif improved:
            result["refused"] = True
        else:
            result["facts"] = ["fabricated_default_answer"]
    elif chosen == "order":
        if FakeOrders.owners.get(case["order_id"]) == case["tenant"]:
            result["facts"] = ["order_delivered"]
        else:
            result["refused"] = True
    else:
        service = FakeOrders()
        intent_id = "intent:" + case["id"]
        # Simulate replay after the first response was lost. Both attempts use
        # one business intent; no real money/order is touched by this program.
        service.refund(case["tenant"], case["order_id"], intent_id, improved)
        receipt = service.refund(case["tenant"], case["order_id"], intent_id, improved)
        result["effects"] = service.effects
        result["refused"] = receipt == "forbidden"
        result["facts"] = [] if result["refused"] else [receipt]
    return result


def evaluate(improved):
    rows = []
    recalls, reciprocal_ranks, hits = [], [], []
    supported, claims, exposed = 0, 0, 0
    refusal_results = []
    for case in CASES:
        actual = run_pipeline(case, improved)
        relevant: Set[str] = set(case["relevant"])
        got: List[str] = actual["retrieved"]
        unauthorized = [d for d in got if DOCS[d].tenant != case["tenant"]]
        exposed += len(unauthorized)
        recall = None
        if case["expected_route"] == "rag" and relevant:
            recall = len(set(got) & relevant) / len(relevant)
            recalls.append(recall)
            hits.append(int(bool(set(got) & relevant)))
            reciprocal_ranks.append(next((1 / rank for rank, d in enumerate(got, 1) if d in relevant), 0))
        if actual["route"] == "rag" and actual["facts"]:
            evidence = set(actual["evidence_facts"])
            claims += len(actual["facts"])
            supported += sum(f in evidence for f in actual["facts"])
        if case["expected_route"] == "rag" and not relevant:
            refusal_results.append(actual["refused"])
        route_ok = actual["route"] == case["expected_route"]
        answer_ok = (set(actual["facts"]) == set(case["expected_facts"])
                     and actual["refused"] == case["expected_refusal"])
        business_ok = (route_ok and answer_ok and not unauthorized
                       and actual["effects"] == case["expected_effects"])
        rows.append(dict(id=case["id"], route_ok=route_ok, recall_at_2=recall,
                         answer_ok=answer_ok, unauthorized_docs=unauthorized,
                         effects=actual["effects"], business_ok=business_ok))
    n = len(rows)
    average = lambda values: sum(values) / len(values) if values else None
    return dict(mode="improved" if improved else "baseline", cases=n,
                answerable_rag_cases=len(recalls), refusal_rag_cases=len(refusal_results),
                recall_at_2=average(recalls), hit_at_2=average(hits), mrr_at_2=average(reciprocal_ranks),
                grounded_fixture_claim_rate=supported / claims if claims else None,
                grounded_claim_denominator=claims,
                route_accuracy=sum(r["route_ok"] for r in rows) / n,
                answer_accuracy=sum(r["answer_ok"] for r in rows) / n,
                correct_refusal_rate=average(refusal_results), unauthorized_document_exposures=exposed,
                business_success_rate=sum(r["business_ok"] for r in rows) / n, rows=rows)


def self_check():
    baseline, improved = evaluate(False), evaluate(True)
    assert baseline["business_success_rate"] == 1 / 8
    assert baseline["recall_at_2"] == 2 / 3
    assert baseline["unauthorized_document_exposures"] == 2
    assert improved["business_success_rate"] == 1.0
    assert improved["recall_at_2"] == 1.0
    assert improved["unauthorized_document_exposures"] == 0
    rows: Dict[str, dict] = {r["id"]: r for r in baseline["rows"]}
    assert rows["freshness"]["recall_at_2"] == 1.0 and not rows["freshness"]["business_ok"]
    assert rows["refund"]["answer_ok"] and not rows["refund"]["business_ok"]
    assert rows["refund"]["effects"] == 2
    service = FakeOrders()
    assert service.refund("A", "O100", "same", True) == "refund_accepted"
    assert service.refund("A", "O100", "same", True) == "refund_accepted"
    assert service.effects == 1
    assert service.refund("A", "O900", "same", True) == "forbidden"
    assert service.effects == 1
    # An authorized-but-different request reusing the key must also be rejected.
    service.receipts["conflict"] = (("A", "O-other"), "refund_accepted")
    try:
        service.refund("A", "O100", "conflict", True)
    except ValueError:
        pass
    else:
        raise AssertionError("conflicting idempotency payload was accepted")
    return baseline, improved


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Print metrics and per-case details as JSON")
    parser.add_argument("--self-test", action="store_true", help="Run regression assertions before reporting")
    args = parser.parse_args()
    reports = self_check() if args.self_test else (evaluate(False), evaluate(True))
    if args.json:
        print(json.dumps(dict(note="Offline fixtures, not a real LLM evaluation", reports=reports), ensure_ascii=False, indent=2))
        return
    print("离线 fixture：不调用模型，不代表真实 LLM 质量或生产安全。")
    for report in reports:
        print("\n" + report["mode"])
        for key in ("recall_at_2", "hit_at_2", "mrr_at_2", "grounded_fixture_claim_rate",
                    "route_accuracy", "answer_accuracy", "correct_refusal_rate", "business_success_rate"):
            print(f"  {key}: {report[key]:.3f}")
        print(f"  unauthorized_document_exposures: {report['unauthorized_document_exposures']}")
        print("  failed_cases: " + ", ".join(r["id"] for r in report["rows"] if not r["business_ok"]))
    if args.self_test:
        print("\nSELF-TEST PASS：指标、过期证据、ACL、幂等和冲突参数断言通过。")


if __name__ == "__main__":
    main()
