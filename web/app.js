'use strict';
const $ = id => document.getElementById(id);
const KEY = 'java-agent-handbook-progress-v1';
const statusNames = ['未开始', '已读', '能口述', '已实践', '通过模拟'];
const docMap = new Map(DB.docs.map(d => [d.id, d]));
const cardMap = new Map(DB.cards.map(c => [c.id, c]));
const modules = DB.docs.filter(d => d.id.startsWith('modules/'));
const escapeHTML = x => String(x).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
let state = {version:1, chapters:{}, cards:{}, lastDoc:'guide/00-start.md'};
let storageOK = true, loadFailure = false, rawProgress = null, mode = 'read', currentDoc = state.lastDoc, cursor = 0, dueOnly = false;
function cleanState(input) {
  const record = value => value && typeof value === 'object' && !Array.isArray(value);
  const time = value => Number.isFinite(value) && value >= 0 && value <= 8640000000000000;
  if (!record(input) || input.version !== 1 || !record(input.chapters) || !record(input.cards)) throw Error('不是本手册支持的进度格式');
  const clean = {version:1, chapters:{}, cards:{}, lastDoc:docMap.has(input.lastDoc) ? input.lastDoc : 'guide/00-start.md'};
  for (const [id, value] of Object.entries(input.chapters)) {
    if (!docMap.has(id)) continue;
    if (!record(value) || !Number.isInteger(value.status) || value.status < 0 || value.status > 4 || typeof value.note !== 'string' || value.note.length > 100000 || !time(value.updated)) throw Error('章节记录格式无效：' + id);
    clean.chapters[id] = {status:value.status, note:value.note, updated:value.updated};
  }
  for (const [id, value] of Object.entries(input.cards)) {
    if (!cardMap.has(id)) continue;
    if (!record(value) || !Number.isInteger(value.step) || value.step < 0 || value.step > 4 || !time(value.due) || !time(value.reviewed)) throw Error('卡片记录格式无效：' + id);
    clean.cards[id] = {step:value.step, due:value.due, reviewed:value.reviewed};
  }
  return clean;
}
try { rawProgress = localStorage.getItem(KEY); if (rawProgress) state = cleanState(JSON.parse(rawProgress)); }
catch (error) { storageOK = false; loadFailure = true; $('notice').textContent = '无法读取原有进度，已保留原始数据并暂停本地覆盖。可继续学习，导出文件将同时保留原始记录。'; }
function save() {
  if (loadFailure) return false;
  try { localStorage.setItem(KEY, JSON.stringify(state)); storageOK = true; return true; }
  catch (error) { storageOK = false; $('notice').textContent = '本地保存失败，请导出进度备份。'; }
}
function notice(text) { $('notice').textContent = text; }
function chapter(id) { return state.chapters[id] || {status:0, note:'', updated:0}; }
const groups = [...new Set(DB.docs.map(d => d.group))];
for (const group of groups) { const option = new Option(group, group); $('group').add(option); }
function query() { return $('search').value.trim().toLocaleLowerCase(); }
function filteredDocs() { const q=query(), g=$('group').value; return DB.docs.filter(d => (!g || d.group===g) && (!q || (d.title+' '+d.text).toLocaleLowerCase().includes(q))); }
function renderNav() {
  const filtered = filteredDocs(), docs = groups.flatMap(group => filtered.filter(d => d.group===group)); let html='', last='';
  for (const d of docs) {
    if (d.group!==last) { html+='<div class="nav-group">'+escapeHTML(d.group)+'</div>'; last=d.group; }
    const done=chapter(d.id).status===4;
    html+='<a class="nav-item '+(d.id===currentDoc && mode==='read' ? 'active' : '')+'" href="#'+escapeHTML(d.id)+'"'+(d.id===currentDoc ? ' aria-current="page"' : '')+'><span class="nav-dot '+(done?'done':'')+'">'+(done?'●':'○')+'</span><span class="nav-text">'+escapeHTML(d.title)+'</span></a>';
  }
  $('nav').innerHTML=html || '<p class="side-foot">没有匹配章节</p>';
  const passed=modules.filter(d=>chapter(d.id).status===4).length;
  $('progress-count').textContent=passed+' / '+modules.length;
  $('progress-label').textContent='已通过模拟的章节';
  $('progress').max=modules.length; $('progress').value=passed;
}
function setMode(next) {
  mode=next;
  $('read-tab').classList.toggle('active',mode==='read'); $('cards-tab').classList.toggle('active',mode==='cards');
  $('read-tab').setAttribute('aria-pressed', String(mode==='read')); $('cards-tab').setAttribute('aria-pressed',String(mode==='cards'));
}
function wrapTables(root) { root.querySelectorAll('table').forEach(t=>{ const wrap=document.createElement('div');wrap.className='table-wrap'; t.before(wrap);wrap.append(t); }); }
function renderDoc(id) {
  const d=docMap.get(id) || docMap.get('guide/00-start.md'); currentDoc=d.id; state.lastDoc=d.id; save();
  let hero='';
  if (d.id==='guide/00-start.md') hero='<section class="hero"><div class="eyebrow">THE SENIOR ENGINEER PLAYBOOK · 01</div><h2>把十年经验，整理成<br>经得起追问的技术判断。</h2><p>从 Java 的执行机制，到分布式系统的失败边界，再到 Agent 的任务闭环。用分层讲义、口述追问与动手实验，把知识变成可验证的能力。</p><div class="stats"><div><strong>'+modules.length+'</strong><span>模块专题</span></div><div><strong>4</strong><span>学习深度</span></div><div><strong>'+DB.cards.length+'</strong><span>核心复习卡</span></div><div><strong>'+DB.diagramCount+'</strong><span>机制图解</span></div></div></section>';
  const s=chapter(d.id), index=DB.docs.findIndex(x=>x.id===d.id);
  $('view').innerHTML=hero+'<div class="doc-meta"><span class="pill green">'+escapeHTML(d.group)+'</span><span class="pill">'+d.priority+'</span>'+(d.questions?'<span class="pill">'+d.questions+' 组核心问答</span>':'')+'<div class="study-controls"><label for="chapter-status">本章状态</label><select id="chapter-status">'+statusNames.map((name,i)=>'<option value="'+i+'"'+(s.status===i?' selected':'')+'>'+name+'</option>').join('')+'</select></div></div><details class="outline"><summary>本章导航</summary><ul id="outline-list"></ul></details><article class="article" id="article">'+d.html+'</article><section class="notes"><label for="note">我的理解与待补证据</label><textarea id="note" maxlength="100000" placeholder="记录：我原来误解了什么？怎样验证？下次还要追问什么？"></textarea><p id="note-status">笔记保存在当前浏览器，建议每周导出备份。</p></section><div class="pager">'+(index>0?'<a href="#'+DB.docs[index-1].id+'">← '+escapeHTML(DB.docs[index-1].title)+'</a>':'<span></span>')+(index<DB.docs.length-1?'<a href="#'+DB.docs[index+1].id+'">'+escapeHTML(DB.docs[index+1].title)+' →</a>':'')+'</div><p class="reader-bottom">2026-10-04 扩充审校版 · 参考回答用于理解与表达训练。具体面试要求以岗位为准。<br>原始讲义：<a href="'+escapeHTML(d.id)+'" target="_blank" rel="noopener">'+escapeHTML(d.id)+'</a></p>';
  $('note').value=s.note;
  $('note').addEventListener('input',()=>{ state.chapters[d.id]={...chapter(d.id),note:$('note').value,updated:Date.now()};save();$('note-status').textContent=storageOK?'已保存到当前浏览器。':'尚未持久保存，请导出进度。'; });
  $('chapter-status').addEventListener('change',()=>{ state.chapters[d.id]={...chapter(d.id),status:Number($('chapter-status').value),updated:Date.now()};save();renderNav(); });
  const outline=$('outline-list');
  $('article').querySelectorAll('h2').forEach((h,i)=>{h.id='section-'+i;const li=document.createElement('li'),a=document.createElement('a');a.href='#section-'+i;a.textContent=h.textContent;a.addEventListener('click',e=>{e.preventDefault();h.scrollIntoView({behavior:'smooth',block:'start'});});li.append(a);outline.append(li);});
  wrapTables($('article')); renderNav();
}
function renderSearch() {
  const docs=filteredDocs(), q=query();
  $('view').innerHTML='<div class="eyebrow">FIND YOUR NEXT QUESTION</div><h2>搜索与专题筛选</h2><p class="card-hint">找到 '+docs.length+' 篇讲义。搜索涵盖正文、参考回答与追问。</p>'+docs.map(d=>{
    const at=q?d.text.toLocaleLowerCase().indexOf(q):0,start=Math.max(0,at-50), snippet=d.text.slice(start,start+190).replace(/[#*`|]/g,'');
    return '<a class="result-card" href="#'+d.id+'"><span class="pill green">'+escapeHTML(d.group)+'</span><h3>'+escapeHTML(d.title)+'</h3><p>'+escapeHTML(snippet)+'…</p></a>';
  }).join('')+(docs.length?'':'<div class="empty">没有匹配结果。试试更短的关键词，或选择全部专题。</div>');renderNav();
}
function filteredCards() {
  const q=query(),g=$('group').value,now=Date.now();
  return DB.cards.filter(c=>(!g||c.group===g)&&(!q||c.search.toLocaleLowerCase().includes(q))&&(!dueOnly||!state.cards[c.id]||state.cards[c.id].due<=now));
}
function renderCards() {
  const cards=filteredCards(); if(cursor>=cards.length)cursor=0;
  const due=DB.cards.filter(c=>!state.cards[c.id]||state.cards[c.id].due<=Date.now()).length;
  $('view').innerHTML='<section class="hero"><div class="eyebrow">RECALL → EXPLAIN → APPLY</div><h2>先合上答案，<br>给自己 90 秒。</h2><p>说清结论、机制、边界和例子。答案展示后再接一轮追问；能记住一句话，并不等于理解整个系统。</p></section><div class="card-toolbar"><span>全部 '+DB.cards.length+' 张 · 待复习 '+due+' 张 · 当前筛选 '+cards.length+' 张</span><label><input type="checkbox" id="due-only" '+(dueOnly?'checked':'')+'>只看待复习</label></div><div id="card-slot"></div>';
  $('due-only').addEventListener('change',()=>{dueOnly=$('due-only').checked;cursor=0;renderCards();});
  if(!cards.length){$('card-slot').innerHTML='<div class="empty">当前没有匹配卡片。可更改专题或关键词，或取消“只看待复习”。</div>';renderNav();return;}
  const c=cards[cursor], saved=state.cards[c.id], d=docMap.get(c.docId);
  $('card-slot').innerHTML='<section class="review-card"><div class="eyebrow">'+escapeHTML(c.group)+' · '+(cursor+1)+' / '+cards.length+'</div><h2>'+escapeHTML(c.question)+'</h2><p class="card-hint">先口述，再判断：我是否讲清了适用条件？如果失败，我会怎样验证？</p><button class="primary" id="reveal">查看参考回答与追问</button><div class="article" id="answer" hidden>'+c.answer+'</div><div class="card-actions" id="grade" hidden><button id="again">还需练习 · 1 天后</button><button class="primary" id="known">能解释 · 安排复习</button></div><div class="card-actions"><button id="prev-card">← 上一题</button><button id="next-card">下一题 →</button></div><p class="card-source"><a href="#'+c.docId+'">回到讲义：'+escapeHTML(d.title)+'</a></p><p class="status-small">'+(saved?'下次复习：'+new Date(saved.due).toLocaleDateString('zh-CN'):'尚未复习 · 请先口述')+'</p></section>';
  $('reveal').addEventListener('click',()=>{$('answer').hidden=false;$('grade').hidden=false;$('reveal').hidden=true;wrapTables($('answer'));});
  $('prev-card').addEventListener('click',()=>{cursor=(cursor-1+cards.length)%cards.length;renderCards();});
  $('next-card').addEventListener('click',()=>{cursor=(cursor+1)%cards.length;renderCards();});
  const grade=known=>{const old=state.cards[c.id],intervals=[1,3,7,14,30],step=known?(old?Math.min(old.step+1,4):0):0;state.cards[c.id]={step,due:Date.now()+intervals[step]*86400000,reviewed:Date.now()};save();if(!dueOnly)cursor=(cursor+1)%cards.length;renderCards();};
  $('again').addEventListener('click',()=>grade(false));$('known').addEventListener('click',()=>grade(true));renderNav();
}
function render() { if(mode==='cards')renderCards();else if(query()||$('group').value)renderSearch();else renderDoc(currentDoc); }
function navigateHash() {
  let id;try{id=decodeURIComponent(location.hash.slice(1));}catch(e){id='';}
  if(id==='main'){if(!$('view').children.length)renderDoc(state.lastDoc);return;}
  if(id==='cards'){setMode('cards');renderCards();return;}
  if(docMap.has(id)){setMode('read');$('search').value='';$('group').value='';renderDoc(id);window.scrollTo(0,0);}
  else {setMode('read');renderDoc(state.lastDoc);}
}
$('search').addEventListener('input',()=>{cursor=0;render();});$('group').addEventListener('change',()=>{cursor=0;render();});
$('read-tab').addEventListener('click',()=>{setMode('read');if(location.hash==='#cards')history.replaceState(null,'','#'+currentDoc);render();});
$('cards-tab').addEventListener('click',()=>{setMode('cards');history.replaceState(null,'','#cards');cursor=0;renderCards();});
// Handle an already-selected hash as well as navigation from search results.
document.addEventListener('click',e=>{const a=e.target.closest('a[href^="#"]');if(!a)return;const id=a.getAttribute('href').slice(1);if(docMap.has(id)&&location.hash.slice(1)===id){e.preventDefault();setMode('read');$('search').value='';$('group').value='';renderDoc(id);window.scrollTo(0,0);}});
window.addEventListener('hashchange',navigateHash);
$('export').addEventListener('click',()=>{const blob=new Blob([JSON.stringify({...state,exportedAt:new Date().toISOString(),...(loadFailure?{recoveryRaw:rawProgress}: {})},null,2)],{type:'application/json'}),url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download='progress-'+new Date().toISOString().slice(0,10)+'.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);notice('进度已导出；文件包含章节状态、笔记与卡片复习时间。');});
$('import').addEventListener('click',()=>$('import-file').click());
$('import-file').addEventListener('change',async e=>{const file=e.target.files[0];if(!file)return;try{if(file.size>10_000_000)throw Error('文件过大');const incoming=cleanState(JSON.parse(await file.text()));for(const [id,value]of Object.entries(incoming.chapters)){if(!state.chapters[id]||value.updated>state.chapters[id].updated)state.chapters[id]=value;}for(const[id,value]of Object.entries(incoming.cards)){if(!state.cards[id]||value.reviewed>state.cards[id].reviewed)state.cards[id]=value;}const persisted=save();render();notice(persisted?'已合并并保存导入进度，同一条记录保留更新时间较新的内容。':'已仅在内存中合并，尚未持久保存。请立即导出进度备份。');}catch(error){notice('导入失败：'+error.message+'。现有进度未被覆盖。');}finally{e.target.value='';}});
currentDoc=state.lastDoc;
if(location.hash)navigateHash();else renderDoc(currentDoc);

// SVG assets stay embedded in the offline HTML. Original Markdown keeps relative files.
let diagramNaturalWidth=780, diagramScale=1, lastDiagramTrigger=null;
function sizeDiagram(fit=false) {
  if(fit)diagramScale=Math.min(1,($('diagram-stage').clientWidth-36)/diagramNaturalWidth);
  diagramScale=Math.max(0.2,Math.min(4,diagramScale));
  $('diagram-large').style.width=Math.round(diagramNaturalWidth*diagramScale)+'px';
  $('diagram-scale').textContent=Math.round(diagramScale*100)+'%';
}
document.addEventListener('click',e=>{
  const trigger=e.target.closest('.diagram-link');if(!trigger)return;
  e.preventDefault();lastDiagramTrigger=trigger;
  const image=trigger.querySelector('img');
  $('diagram-title-label').textContent=image.alt;
  $('diagram-large').alt=image.alt;
  $('diagram-large').onload=()=>{diagramNaturalWidth=$('diagram-large').naturalWidth||780;sizeDiagram(true);};
  $('diagram-large').src=image.src;
  $('diagram-download').href=image.src;
  $('diagram-download').download=(trigger.dataset.asset||'diagram.svg').split('/').pop();
  $('diagram-dialog').showModal();
  if($('diagram-large').complete){diagramNaturalWidth=$('diagram-large').naturalWidth||780;sizeDiagram(true);}
});
$('diagram-close').addEventListener('click',()=>$('diagram-dialog').close());
$('diagram-dialog').addEventListener('close',()=>{lastDiagramTrigger?.focus();});
$('diagram-fit').addEventListener('click',()=>sizeDiagram(true));
$('diagram-in').addEventListener('click',()=>{diagramScale*=1.25;sizeDiagram();});
$('diagram-out').addEventListener('click',()=>{diagramScale/=1.25;sizeDiagram();});
