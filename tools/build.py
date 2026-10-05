#!/usr/bin/env python3
"""Build a self-contained offline reader from the Markdown source."""
import html
import base64
import json
import posixpath
import re
from pathlib import Path
import mistune

ROOT = Path(__file__).resolve().parents[1]
GROUPS = {
    "01": "Java 核心", "02": "Java 核心", "03": "Java 核心", "04": "Java 核心", "05": "Java 核心",
    "06": "数据与分布式", "07": "数据与分布式", "08": "数据与分布式", "09": "数据与分布式",
    "10": "系统工程", "11": "系统工程", "12": "系统工程", "13": "系统工程",
    "14": "编码与面试", "15": "Agent 工程", "16": "Agent 工程", "17": "Agent 工程", "18": "Agent 工程",
    "19": "编码与面试",
    "20": "Java 核心", "21": "Java 核心", "22": "Java 核心",
    "23": "数据与分布式", "24": "数据与分布式", "25": "数据与分布式",
    "26": "Agent 工程", "27": "Agent 工程", "28": "Agent 工程",
    "29": "系统工程", "30": "系统工程", "31": "系统工程",
    "32": "编码与面试", "33": "系统工程", "34": "编码与面试",
}
paths = sorted((ROOT / "guide").glob("*.md")) + sorted((ROOT / "modules").glob("*.md")) + sorted((ROOT / "labs").glob("*.md")) + sorted((ROOT / "practice").glob("*.md"))
known = {p.relative_to(ROOT).as_posix() for p in paths}
known.add("README.md")

class Renderer(mistune.HTMLRenderer):
    current = ""
    def image(self, text, url, title=None):
        resolved = (ROOT / self.current).parent.joinpath(url).resolve()
        if not resolved.is_relative_to(ROOT) or resolved.suffix != '.svg' or not resolved.exists():
            raise ValueError(f'Image must be a local SVG inside project: {self.current}: {url}')
        source = resolved.read_bytes()
        encoded = base64.b64encode(source).decode('ascii')
        data_url = 'data:image/svg+xml;base64,' + encoded
        label = re.sub('<[^>]+>', '', text)
        return ('<a class="diagram-link" href="' + data_url + '" data-asset="' +
                html.escape(resolved.relative_to(ROOT).as_posix(), quote=True) +
                '" aria-label="放大图：' + html.escape(label, quote=True) + '">' +
                '<img class="diagram" src="' + data_url + '" alt="' + html.escape(label, quote=True) +
                '" loading="lazy" decoding="async"/></a>')

    def link(self, text, url, title=None):
        if not re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", url) and not url.startswith("#"):
            target, _, fragment = url.partition("#")
            resolved = posixpath.normpath(posixpath.join(posixpath.dirname(self.current), target))
            if resolved in known:
                if resolved == "README.md":
                    resolved = "guide/00-start.md"
                return '<a href="#' + html.escape(resolved, quote=True) + '">' + text + '</a>'
            url = resolved + ("#" + fragment if fragment else "")
        return super().link(text, url, title)

renderer = Renderer(escape=True)
markdown = mistune.create_markdown(renderer=renderer, plugins=["table", "strikethrough"])
docs, cards = [], []
for path in paths:
    raw = path.read_text(encoding="utf-8")
    doc_id = path.relative_to(ROOT).as_posix()
    title = re.search(r"^# (.+)$", raw, re.M).group(1)
    number = path.name[:2]
    group = GROUPS.get(number, "学习导航") if doc_id.startswith("modules/") else ("动手实验" if doc_id.startswith("labs/") else "学习导航")
    renderer.current = doc_id
    rendered = markdown(raw)
    priority = "P1" if number in {"13", "15", "16", "17", "18", "25", "26", "27", "28", "30", "31"} else "P0"
    if not doc_id.startswith("modules/"):
        priority = "导学" if not doc_id.startswith("labs/") else "实践"
    headings = list(re.finditer(r"^### (.+)$", raw, re.M))
    card_count = 0
    if doc_id.startswith("modules/"):
        for i, heading in enumerate(headings):
            label = heading.group(1)
            if not re.match(r"(?:Q\d+|\d+\.)", label):
                continue
            end = headings[i + 1].start() if i + 1 < len(headings) else len(raw)
            block = raw[heading.end():end]
            block = re.split(r"^## ", block, maxsplit=1, flags=re.M)[0].strip()
            if not re.search(r"\*\*[^*\n]*参考(?:回答|答案)(?:结构)?[：:]?\*\*", block):
                continue
            # Keep answer and follow-up; same source as the chapter avoids drift.
            card_count += 1
            question = re.sub(r"^(?:Q\d+[：:｜·.\s]*|\d+\.\s*)", "", label)
            cards.append({"id": path.stem + "-q" + str(card_count), "docId": doc_id, "group": group, "question": question, "answer": markdown(block), "search": question + " " + block})
    docs.append({"id": doc_id, "title": title, "group": group, "priority": priority, "html": rendered, "text": raw, "questions": card_count})

payload = {"version": "2026-10-04-expanded", "diagramCount": len(list(ROOT.glob("modules/assets/*.svg"))) + len(list(ROOT.glob("guide/assets/*.svg"))), "docs": docs, "cards": cards}
serialized = json.dumps(payload, ensure_ascii=False).replace("<", "\\u003c").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")
template = (ROOT / "web/template.html").read_text(encoding="utf-8")
output = template.replace("__STYLE__", (ROOT / "web/style.css").read_text(encoding="utf-8")).replace("__PAYLOAD__", serialized).replace("__APP__", (ROOT / "web/app.js").read_text(encoding="utf-8"))
(ROOT / "index.html").write_text(output, encoding="utf-8")
(ROOT / "catalog.json").write_text(json.dumps({"version": payload["version"], "diagramCount": payload["diagramCount"], "documents": [{k:v for k,v in d.items() if k not in {"html", "text"}} for d in docs], "cardCount": len(cards)}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"Built index.html: {len(docs)} documents, {len(cards)} review cards")
