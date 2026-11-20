#!/usr/bin/env python3
"""Check data.json against references/schema.md. usage: validate.py DATA.json"""
import sys,json,re,collections
D=json.load(open(sys.argv[1],encoding='utf-8')); E=[]; W=[]
for k in ('site','features','labels','items','chapters'):
    if k not in D: E.append('缺少欄位 '+k)
if E: print('\n'.join(E)); sys.exit(1)
S=D['site']
for k in ('pageTitle','h1','version','examDefault','storageKey','dbDoc'):
    if k not in S: E.append('site 缺少 '+k)
if S.get('examDefault') and not re.match(r'^\d{4}-\d{2}-\d{2}$',S['examDefault']): E.append('site.examDefault 要寫成 YYYY-MM-DD')
F=D['features']; modes=F.get('modes',[])
if not F.get('atlas') and not F.get('drill'): E.append('features 的 atlas 和 drill 至少要開一個')
if F.get('drill') and (not modes or any(m not in ('flash','choice') for m in modes)): E.append('features.modes 只能是 flash、choice（至少一個）')
I=D['items']; G=D.get('groups',{}); dims=D.get('dims',{})
for k in ('item','f','c','nameOrder'):
    if k not in D['labels']: E.append('labels 缺少 '+k)
for id,it in I.items():
    for f in ('n','z','img','f','c','p'):
        if f not in it: E.append(f'{id} 缺少 {f}')
    for im in (it.get('img'),it.get('orig')):
        if im and im not in dims: E.append(f'{id} 的圖 {im} 沒有 dims（寬高）')
    if 'choice' in modes and F.get('drill'):
        mc=it.get('mc')
        if not mc: W.append(f'{id} 沒有 mc，選擇題模式不會出這題')
        else:
            o=mc.get('o',[])
            if len(o)<2 or len(set(o))!=len(o): E.append(f'{id} 的 mc 選項不足或重複')
            if not isinstance(mc.get('a'),int) or not 0<=mc['a']<len(o): E.append(f'{id} 的 mc 答案索引超出選項')
            if len(mc.get('e',[]))!=len(o): E.append(f'{id} 的 mc 詳解數 ≠ 選項數')
            elif not str(mc['e'][mc['a']]).startswith('正確'): W.append(f'{id} 的正解詳解沒有以「正確」開頭')
seen=collections.Counter()
for c in D['chapters']:
    for f in ('id','t'):
        if f not in c: E.append(f'章節缺少 {f}')
    for i in c.get('items',[]):
        seen[i]+=1
        if i not in I: E.append(f'章節 {c.get("id")} 的項目 {i} 不存在')
    for t in c.get('trays',[]):
        if t not in G: E.append(f'章節 {c.get("id")} 的組合圖 {t} 不存在')
for i in I:
    if seen[i]==0: E.append(f'項目 {i} 沒有放進任何章節')
    elif seen[i]>1: E.append(f'項目 {i} 在 {seen[i]} 個章節重複')
for tid,t in G.items():
    if t.get('img') and t['img'] not in dims: E.append(f'組合圖 {tid} 的圖沒有 dims')
    for r in t.get('list',[]):
        if len(r)!=7: E.append(f'組合圖 {tid} 的清單列要有 7 欄：{r}')
        elif r[5] and r[5] not in I: W.append(f'組合圖 {tid} 第 {r[0]} 號連到不存在的項目 {r[5]}')
cids={c['id'] for c in D['chapters']}
for m in D.get('mnemonics',[]):
    if m.get('ch') not in cids: E.append(f'口訣 {m.get("id")} 的章節不存在')
for k,v in D.get('diagrams',{}).items():
    if v.get('after') and v['after'] not in I: E.append(f'示意圖 {k} 的 after 項目不存在')
for x in D.get('cmp',[]):
    for r in x.get('rows',[]):
        if r[0] not in I: E.append(f'對照表 {x.get("id")} 的項目 {r[0]} 不存在')
nq=0
for cid,qs in D.get('quiz',{}).items():
    if cid not in cids: E.append(f'測驗的章節 {cid} 不存在')
    for i,q in enumerate(qs):
        nq+=1
        if not 0<=q.get('a',-1)<len(q.get('o',[])): E.append(f'{cid} 測驗第 {i+1} 題答案超出選項')
        if len(q.get('e',[]))!=len(q.get('o',[])): E.append(f'{cid} 測驗第 {i+1} 題詳解數 ≠ 選項數')
        if q.get('img') and q['img'] not in dims: E.append(f'{cid} 測驗第 {i+1} 題圖片沒有 dims')
nmc=sum(1 for it in I.values() if it.get('mc')); nmust=sum(1 for it in I.values() if it.get('must'))
print(f'項目 {len(I)}・章節 {len(cids)}・組合圖 {len(G)}・選擇題 {nmc}・必考 {nmust}・章節測驗 {nq} 題・口訣 {len(D.get("mnemonics",[]))}・示意圖 {len(D.get("diagrams",{}))}')
for w in W[:30]: print('⚠️',w)
if len(W)>30: print(f'⚠️ 另有 {len(W)-30} 則')
if E: print('\n'.join('❌ '+e for e in E)); sys.exit(1)
print('✅ 驗證通過')
