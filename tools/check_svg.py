#!/usr/bin/env python3
"""Check generated SVG structure and create a local visual-QA gallery on request."""
import argparse
import html
import re
import xml.etree.ElementTree as ET
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
SVG = '{http://www.w3.org/2000/svg}'
files = sorted(ROOT.glob('modules/assets/*.svg')) + sorted(ROOT.glob('guide/assets/*.svg'))
errors = []
for path in files:
    try:
        tree = ET.fromstring(path.read_text())
    except ET.ParseError as error:
        errors.append(f'{path.name}: {error}'); continue
    vb = [float(x) for x in tree.attrib['viewBox'].split()]
    if tree.find(SVG+'title') is None or tree.find(SVG+'desc') is None:
        errors.append(f'{path.name}: missing accessible title/description')
    raw = path.read_text()
    if 'PingFang SC' not in raw or 'Microsoft YaHei' not in raw:
        errors.append(f'{path.name}: missing CJK font fallback')
    if re.search(r'<(?:script|foreignObject|image)\b', raw):
        errors.append(f'{path.name}: unexpected executable/external content')
    nodes = []
    for node in tree.iter(SVG+'rect'):
        if 'data-node' not in node.attrib: continue
        x,y,w,h=(float(node.get(k,'0')) for k in ('x','y','width','height'))
        if min(x,y)<0 or x+w>vb[2] or y+h>vb[3]: errors.append(f'{path.name}: node outside viewBox')
        nodes.append((node.get('data-node'),x,y,w,h))
    for i,(name,x,y,w,h) in enumerate(nodes):
        for other,a,b,c,d in nodes[i+1:]:
            if min(x+w,a+c)>max(x,a) and min(y+h,b+d)>max(y,b):
                errors.append(f'{path.name}: intersecting nodes {name}/{other}')
    for marker in tree.iter(SVG+'marker'):
        if marker.get('markerUnits')!='userSpaceOnUse' or marker.get('refX')!='2':
            errors.append(f'{path.name}: unexpected marker convention')
parser=argparse.ArgumentParser()
parser.add_argument('--gallery', type=Path)
args=parser.parse_args()
if args.gallery:
    parts=['<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>SVG visual QA</title><style>body{margin:0;background:#e2e8f0;font-family:system-ui}section{background:white;margin:12px;padding:12px;width:780px;break-inside:avoid}h2{font-size:12px}#gallery{display:grid;grid-template-columns:repeat(2,828px)}</style><div id="gallery">']
    for i,p in enumerate(files):
        # Unique fragment IDs keep markers correct when many SVGs share one DOM.
        raw=p.read_text()
        ids=re.findall(r'\bid="([^"]+)"',raw)
        for old in ids:
            new=f'd{i}-{old}'
            raw=raw.replace(f'id="{old}"',f'id="{new}"').replace(f'url(#{old})',f'url(#{new})')
        raw=raw.replace('aria-labelledby="diagram-title diagram-desc"',f'aria-labelledby="d{i}-diagram-title d{i}-diagram-desc"')
        parts.append(f'<section data-file="{html.escape(p.relative_to(ROOT).as_posix())}"><h2>{html.escape(p.name)}</h2>{raw}</section>')
    args.gallery.write_text(''.join(parts)+'</div></html>')
if errors: raise SystemExit('\n'.join(errors))
print(f'PASS SVG structure: {len(files)} images; actual font bounds and visual layout require browser QA')
