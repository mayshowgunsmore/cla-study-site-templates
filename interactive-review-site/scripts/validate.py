#!/usr/bin/env python3
"""Check data.json against references/schema.md. usage: validate.py DATA.json"""
import sys,json,re,collections
D=json.load(open(sys.argv[1],encoding='utf-8')); E=[]; W=[]
for k in ('site','chapters'):
    if k not in D: E.append('缺少欄位 '+k)
if E: print('\n'.join(E)); sys.exit(1)
for k in ('pageTitle','name','version','title','sub','h1','examName','examDefault','storageKey','dbDoc'):
    if k not in D['site']: E.append('site 缺少 '+k)
if not re.match(r'^\d{4}-\d{2}-\d{2}$',D['site'].get('examDefault','')): E.append('site.examDefault 要寫成 YYYY-MM-DD')
SECS={}; cids=set()
for c in D['chapters']:
    for f in ('id','no','t','secs'):
        if f not in c: E.append(f'章節 {c.get("id")} 缺少 {f}')
    if c.get('id') in cids: E.append('章節 id 重複 '+str(c.get('id')))
    cids.add(c.get('id'))
    for s in c.get('secs',[]):
        if s.get('id') in SECS: E.append('節 id 重複 '+str(s.get('id')))
        for f in ('id','t','src','html'):
            if f not in s: E.append(f'節 {s.get("id")} 缺少 {f}')
        SECS[s.get('id')]=s
        if '{{' in s.get('html',''): E.append(f'節 {s["id"]} 內文殘留 {{{{')
        for t in s.get('tags',[]):
            if t not in ('must','freq','past','nat','imp') and t not in (D.get('tagDefs') or {}): W.append(f'節 {s["id"]} 標籤 {t} 不是 must/freq/past/nat/imp 或 tagDefs 定義的標籤')
figs=D.get('figCaptions',{}); fsz=D.get('figSize',{}); mn=D.get('mnemonics',{}); dg=D.get('diagrams',{}); wg=D.get('widgets',{})
for k in figs:
    if k not in fsz: E.append(f'原圖 {k} 沒有 figSize')
ids=list(figs)+list(mn)+list(dg)+list(wg)
dup=[k for k,n in collections.Counter(ids).items() if n>1]
if dup: E.append('原圖／口訣／示意圖／互動圖代號重複：'+'、'.join(dup))
for nm,obj in (('口訣',mn),('示意圖',dg),('互動圖',wg)):
    for k,v in obj.items():
        if v.get('sec') not in SECS: E.append(f'{nm} {k} 的節 {v.get("sec")} 不存在')
for k,v in mn.items():
    for f in ('p','m','e'):
        if f not in v: E.append(f'口訣 {k} 缺少 {f}')
for k,v in dg.items():
    if 'svg' not in v or 'cap' not in v: E.append(f'示意圖 {k} 缺少 svg 或 cap')
for k,v in wg.items():
    if not v.get('opts'): E.append(f'互動圖 {k} 沒有 opts')
    for o in v.get('opts',[]):
        if f'data-k="{o[0]}"' not in v.get('svg','') : W.append(f'互動圖 {k} 的選項 {o[0]} 在圖上沒有對應的 data-k（只能用按鈕切換）')
used=collections.Counter()
for sid,lst in D.get('place',{}).items():
    if sid not in SECS: E.append(f'place 的節 {sid} 不存在'); continue
    html=SECS[sid]['html']
    for a,i in lst:
        used[i]+=1
        if i not in figs and i not in mn and i not in dg and i not in wg and i!='@skip': E.append(f'place {sid} 的項目 {i} 不存在')
        if a not in ('@end',) and i!='@skip':
            n=html.count(a)
            if n!=1: E.append(f'place {sid} 的錨點出現 {n} 次（要剛好 1 次）：{a[:30]}')
for k in figs:
    if used[k]==0: E.append(f'原圖 {k} 沒有放進任何一節')
    elif used[k]>1: E.append(f'原圖 {k} 放了 {used[k]} 次')
for nm,obj in (('口訣',mn),('示意圖',dg),('互動圖',wg)):
    for k in obj:
        if used[k]==0: W.append(f'{nm} {k} 沒有放進內文（只出現在總表）' if nm=='口訣' else f'{nm} {k} 沒有放進內文')
for nm in ('key','fix','extra','hot','num'):
    for x in D.get(nm,[]):
        if x.get('sec') and x['sec'] not in SECS: E.append(f'{nm} 的節 {x["sec"]} 不存在')
for x in D.get('key',[]):
    if x.get('t') not in ('must','freq','imp','nat','teach','skip'): E.append(f'必考標記類型 {x.get("t")} 不對')
nq=0;ns=0
for sid,qs in D.get('quiz',{}).items():
    if sid not in SECS: E.append(f'測驗的節 {sid} 不存在'); continue
    if not 3<=len(qs)<=8: W.append(f'{sid} 測驗 {len(qs)} 題（建議 3～8 題）')
    for i,q in enumerate(qs):
        nq+=1; ns+=bool(q.get('self'))
        tag=f'{sid} 第 {i+1} 題'
        for f in ('s','q','o','a','e','k'):
            if f not in q: E.append(f'{tag} 缺少 {f}')
        if 'o' not in q or 'a' not in q or 'e' not in q: continue
        if not isinstance(q['a'],int) or not 0<=q['a']<len(q['o']): E.append(f'{tag} 答案索引 {q["a"]} 超出選項')
        if len(q['e'])!=len(q['o']): E.append(f'{tag} 詳解數 ≠ 選項數')
        if len(set(q['o']))!=len(q['o']): W.append(f'{tag} 有相同的選項文字')
print(f'章節 {len(D["chapters"])}・節 {len(SECS)}・原圖 {len(figs)}・口訣 {len(mn)}・示意圖 {len(dg)}・互動圖 {len(wg)}・測驗 {nq} 題（自編 {ns}）・註解 {len(D.get("gloss",{}))}')
for w in W: print('⚠️',w)
if E: print('\n'.join('❌ '+e for e in E)); sys.exit(1)
print('✅ 驗證通過')
