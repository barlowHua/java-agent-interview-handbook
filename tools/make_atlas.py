#!/usr/bin/env python3
"""Regenerate the SVG atlas; explanations and sources remain in the topic chapters."""
from pathlib import Path
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
parts=['# 机制图谱：先看、再讲、最后闭卷重画\n\n所有 SVG 都已放在对应讲义旁的 assets 目录，阅读器中可点击放大、缩放和下载。图是本项目原创教学示意；其前提、简化和官方来源写在对应章节，不是厂商生产架构声明。\n\n使用方法：先回正文读图说明，再沿箭头口述；合上图后重画，最后改变一个条件解释结果。不要只记节点颜色。本页由 `tools/make_atlas.py` 生成，内容解释请在对应章节维护。\n']
for folder in ('modules','guide'):
    for image in sorted((ROOT/folder/'assets').glob('*.svg')):
        tree=ET.fromstring(image.read_text())
        title=tree.find('{http://www.w3.org/2000/svg}title').text
        desc=tree.find('{http://www.w3.org/2000/svg}desc').text or title
        target=next((ROOT/folder).glob(image.name[:2]+'-*.md'))
        rel='../'+image.relative_to(ROOT).as_posix() if folder=='modules' else 'assets/'+image.name
        doc='../'+target.relative_to(ROOT).as_posix() if folder=='modules' else target.name
        parts.append(f'\n## {title}\n\n![{title}]({rel})\n\n{desc} [返回讲义]({doc})。\n')
(ROOT/'guide/05-diagram-atlas.md').write_text(''.join(parts))
print('Generated diagram atlas')
