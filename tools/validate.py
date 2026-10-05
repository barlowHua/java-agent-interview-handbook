#!/usr/bin/env python3
"""Local structure/link checks; does not claim to verify external references."""
import json
import base64
import re
import sys
from pathlib import Path
from urllib.parse import unquote
ROOT = Path(__file__).resolve().parents[1]
errors = []
paths = [ROOT / 'README.md', ROOT / 'VALIDATION.md', ROOT / 'REVIEW.md']
for folder in ('guide', 'modules', 'labs', 'practice'):
    paths += sorted((ROOT / folder).glob('*.md'))
links = 0
for path in paths:
    if not path.exists():
        errors.append(f'missing: {path.name}')
        continue
    raw = path.read_text(encoding='utf-8')
    for target in re.findall(r'\[[^\]\n]*\]\(([^)\n]+)\)', raw):
        if re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*:', target) or target.startswith('#'):
            continue
        relative = unquote(target.split('#')[0].strip('<>'))
        if not (path.parent / relative).resolve().exists():
            errors.append(f'{path.relative_to(ROOT)}: broken link {target}')
        links += 1
    if path.parent.name == 'modules':
        for level in ('L1', 'L2', 'L3', 'L4'):
            if not re.search(r'\b' + level + r'\b', raw):
                errors.append(f'{path.name}: missing {level}')
        if '![' not in raw:
            errors.append(f'{path.name}: missing mechanism diagram')
        if not re.search('过关|闭卷验收|通过标准', raw) or '追问' not in raw:
            errors.append(f'{path.name}: missing assessment')
catalog = json.loads((ROOT / 'catalog.json').read_text(encoding='utf-8'))
modules = [d for d in catalog['documents'] if d['id'].startswith('modules/')]
if {int(Path(d["id"]).name[:2]) for d in modules} != set(range(1, 35)):
    errors.append("expected module numbers 01 through 34")
if any(d['questions'] < 6 for d in modules):
    errors.append('each module must contain at least six answer cards')
if sum(d['questions'] for d in modules) != catalog['cardCount']:
    errors.append('card total mismatch')
html = (ROOT / 'index.html').read_text(encoding='utf-8')
payload_match = re.search(r'<script>const DB = (.*?);</script>', html, re.S)
if not payload_match:
    errors.append('missing reader payload')
else:
    payload = json.loads(payload_match.group(1))
    source_paths = {p.relative_to(ROOT).as_posix(): p for folder in ('guide','modules','labs','practice') for p in (ROOT/folder).glob('*.md')}
    bundled_docs = {doc['id']: doc for doc in payload['docs']}
    if set(source_paths) != set(bundled_docs):
        errors.append('reader document set is stale; rebuild required')
    for doc_id, source in source_paths.items():
        if doc_id in bundled_docs and bundled_docs[doc_id]['text'] != source.read_text(encoding='utf-8'):
            errors.append('stale bundled Markdown: ' + doc_id)
    expected_html = (ROOT/'web/template.html').read_text().replace('__STYLE__', (ROOT/'web/style.css').read_text()).replace('__PAYLOAD__', payload_match.group(1)).replace('__APP__', (ROOT/'web/app.js').read_text())
    if expected_html != html:
        errors.append('reader template/style/script is stale; rebuild required')
    if catalog['cardCount'] != len(payload['cards']):
        errors.append('catalog and reader card count differ')
    if catalog.get('diagramCount') != len(list(ROOT.glob('modules/assets/*.svg'))) + len(list(ROOT.glob('guide/assets/*.svg'))):
        errors.append('catalog diagram count is stale')
    actual_ids = [card['id'] for card in payload['cards']]
    if len(actual_ids) != len(set(actual_ids)):
        errors.append('duplicate review card IDs')
    baseline_cards = json.loads((ROOT / 'tools/baseline-cards.json').read_text())
    baseline_ids = [card['id'] for card in baseline_cards]
    if not set(baseline_ids).issubset(actual_ids):
        errors.append('original card IDs changed; progress migration required')
    current_questions = {card['id']: card['question'] for card in payload['cards']}
    for card in baseline_cards:
        if current_questions.get(card['id']) != card['question']:
            errors.append('original card now points to a different question: ' + card['id'])
    for doc in payload['docs']:
        for asset, encoded in re.findall(r'data-asset="([^"]+)"[^>]*><img[^>]+src="data:image/svg\+xml;base64,([^"]+)"', doc['html']):
            source = (ROOT/asset).resolve()
            if not source.is_relative_to(ROOT) or not source.exists() or base64.b64decode(encoded) != source.read_bytes():
                errors.append('stale embedded SVG: ' + asset)
        if re.search(r'<img[^>]+src="(?!data:image/svg\+xml;base64,)', doc['html']):
            errors.append('non-embedded image: ' + doc['id'])
if any(token in html for token in ('__STYLE__', '__PAYLOAD__', '__APP__')):
    errors.append('unsubstituted template placeholder')
if re.search(r'<script[^>]+src=|<link[^>]+href="https?://', html):
    errors.append('reader has remote runtime dependency')
if errors:
    print('\n'.join(errors)); sys.exit(1)
print(f'PASS: {len(paths)} Markdown files, {links} local links, {len(modules)} layered modules, {catalog["cardCount"]} review cards, offline bundle')
