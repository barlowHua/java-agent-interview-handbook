"""Small SVG helpers for this handbook. Follows svg-diagram skill conventions."""
from html import escape
from pathlib import Path

PALETTE = {
    'blue':('#dbeafe','#3b82f6','#1e40af'),
    'orange':('#fef3c7','#f59e0b','#b45309'),
    'green':('#d1fae5','#22c55e','#166534'),
    'purple':('#f3e8ff','#a855f7','#6b21a8'),
    'pink':('#fce7f3','#ec4899','#9d174d'),
    'gray':('#f8fafc','#94a3b8','#1e293b'),
}
class Diagram:
    def __init__(self, title, width=780, height=420, desc='', subtitle=''):
        self.width,self.height,self.title=width,height,title
        self.background=[];self.connectors=[];self.foreground=[]
        self.boxes={}
        self.desc=desc
        self.text(width/2,32,title,16, '#1e293b', weight='600')
        if subtitle:self.text(width/2,55,subtitle,10,'#64748b')
    def text(self,x,y,text,size=12,color='#1e293b',anchor='middle',weight='400',owner=None):
        attr=f' data-owner="{escape(owner)}"' if owner else ''
        self.foreground.append(f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" text-anchor="{anchor}" font-weight="{weight}"{attr}>{escape(str(text))}</text>')
    def node(self,key,x,y,w,h,lines,color='blue'):
        if isinstance(lines,str):lines=[lines]
        assert h>=36+(len(lines)-1)*18, f'{key}: insufficient height'
        fill,stroke,ink=PALETTE[color]
        self.boxes[key]=(x,y,w,h)
        self.foreground.append(f'<!-- {escape(key)}: x={x}, y={y}, w={w}, h={h}, right={x+w}, bottom={y+h} -->')
        self.foreground.append(f'<rect data-node="{escape(key)}" x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{fill}" stroke="{stroke}" stroke-width="1.2"/>')
        baseline=y+h/2+12*.35-(len(lines)-1)*9
        for i,line in enumerate(lines):self.text(x+w/2,round(baseline+i*18,1),line,12,ink,owner=key)
    def group(self,key,x,y,w,h,label):
        self.background.append(f'<rect data-group="{escape(key)}" x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="#f8fafc" stroke="#94a3b8" stroke-width="1.2" stroke-dasharray="6,4"/>')
        self.background.append(f'<text x="{x+10}" y="{y+14}" font-size="11" text-anchor="start" fill="#64748b">{escape(label)}</text>')
    def path(self,d,color='gray',dashed=False):
        dash=' stroke-dasharray="6,4"' if dashed else ''
        self.connectors.append(f'<path data-connector="true" d="{d}" fill="none" stroke="{PALETTE[color][1] if color!="gray" else "#64748b"}" stroke-width="1.3"{dash} marker-end="url(#arrow-{color})"/>')
    def edge(self,source,target,side='right',target_side=None,color='gray',dashed=False):
        # Cardinal endpoints; a C curve is used whenever the route changes direction.
        target_side=target_side or {'right':'left','left':'right','bottom':'top','top':'bottom'}[side]
        x,y,w,h=self.boxes[source];tx,ty,tw,th=self.boxes[target]
        starts={'right':(x+w+5,y+h/2),'left':(x-5,y+h/2),'bottom':(x+w/2,y+h+5),'top':(x+w/2,y-5)}
        ends={'left':(tx-11,ty+th/2),'right':(tx+tw+11,ty+th/2),'top':(tx+tw/2,ty-11),'bottom':(tx+tw/2,ty+th+11)}
        sx,sy=starts[side];ex,ey=ends[target_side]
        if (sy==ey and side in ['left','right'] and target_side in ['left','right']) or (sx==ex and side in ['top','bottom'] and target_side in ['top','bottom']):
            d=f'M {sx},{sy} L {ex},{ey}'
        else:
            delta=max(12,min(35,(abs(ex-sx)+abs(ey-sy))/3))
            v={'right':(1,0),'left':(-1,0),'bottom':(0,1),'top':(0,-1)}
            vx,vy=v[side];ux,uy=v[target_side]
            d=f'M {sx},{sy} C {sx+vx*delta},{sy+vy*delta} {ex+ux*delta},{ey+uy*delta} {ex},{ey}'
        self.path(d,color,dashed)
    def footer(self,lines,y=None):
        if isinstance(lines,str):lines=[lines]
        y=y if y is not None else self.height-25-(len(lines)-1)*16
        for i,line in enumerate(lines):self.text(self.width/2,y+i*16,line,10,'#64748b')
    def save(self,path):
        defs=[]
        for name,(_,stroke,_) in PALETTE.items():
            color='#64748b' if name=='gray' else stroke
            defs.append(f'<marker id="arrow-{name}" markerWidth="8" markerHeight="8" refX="2" refY="4" orient="auto" markerUnits="userSpaceOnUse"><path d="M0,0 L8,4 L0,8 L2,4 z" fill="{color}"/></marker>')
        svg=f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.width} {self.height}" width="{self.width}" height="{self.height}" role="img" aria-labelledby="diagram-title diagram-desc">
<title id="diagram-title">{escape(self.title)}</title><desc id="diagram-desc">{escape(self.desc)}</desc>
<style>text {{ font-family: 'PingFang SC', 'Microsoft YaHei', 'Noto Sans CJK SC', system-ui, sans-serif; }}</style>
<defs>{''.join(defs)}</defs>
<rect width="{self.width}" height="{self.height}" fill="#ffffff"/>
{''.join(self.background)}
{''.join(self.connectors)}
{''.join(self.foreground)}
</svg>'''
        p=Path(path);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(svg,encoding='utf-8')
