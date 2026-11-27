#!/usr/bin/env python3
"""Check data.json against references/schema.md. usage: validate.py DATA.json
❌ 錯誤：網站會壞掉或違反規範，build.py 不輸出網站；⚠️ 提醒：建議修正，仍可輸出。"""
import sys,json,re,collections
D=json.load(open(sys.argv[1],encoding='utf-8')); E=[]; W=[]
def done():
    for w in W[:30]: print('⚠️',w)
    if len(W)>30: print(f'⚠️ 另有 {len(W)-30} 則')
    if E: print('\n'.join('❌ '+e for e in E)); sys.exit(1)
    print('✅ 驗證通過')
if not isinstance(D,dict): E.append('data.json 最上層要是物件'); done()
if D.get('schema')!='image-id-drill-site/1': W.append(f'schema 應為 image-id-drill-site/1（目前 {D.get("schema")}）')
for k,t in (('site',dict),('features',dict),('labels',dict),('items',dict),('chapters',list)):
    if k not in D: E.append('缺少欄位 '+k)
    elif not isinstance(D[k],t): E.append(f'{k} 要是{"物件" if t is dict else "陣列"}')
for k,t in (('groups',dict),('mnemonics',list),('cmp',list),('doubt',list),('quiz',dict),('dims',dict),('diagrams',dict),('info',list),('howto',list)):
    if k in D and not isinstance(D[k],t): E.append(f'{k} 要是{"物件" if t is dict else "陣列"}')
if E: done()
S=D['site']
for k in ('pageTitle','h1','version','examDefault','storageKey','dbDoc'):
    if k not in S: E.append('site 缺少 '+k)
if S.get('examDefault') and not re.match(r'^\d{4}-\d{2}-\d{2}$',str(S['examDefault'])): E.append('site.examDefault 要寫成 YYYY-MM-DD')
if 'band' in S and (not isinstance(S['band'],list) or len(S['band'])>2 or any(not isinstance(x,str) for x in S['band'])): E.append('site.band 要是最多兩段文字的陣列')
if 'storageKey' in S and not re.match(r'^[a-z0-9-]+$',str(S['storageKey'])): W.append('site.storageKey 建議只用英數小寫與連字號（已發布的網站不要改）')
F=D['features']; modes=F.get('modes',[])
if not F.get('atlas') and not F.get('drill'): E.append('features 的 atlas 和 drill 至少要開一個')
if F.get('drill') and (not isinstance(modes,list) or not modes or any(m not in ('flash','choice') for m in modes)): E.append('features.modes 只能是 flash、choice（至少一個）')
I=D['items']; G=D.get('groups',{}); dims=D.get('dims',{})
LB=D['labels']
for k in ('item','f','c','nameOrder'):
    if k not in LB: E.append('labels 缺少 '+k)
if LB.get('nameOrder') not in (None,'en','zh'): E.append('labels.nameOrder 只能是 en 或 zh')
for k,v in dims.items():
    if not isinstance(v,list) or len(v)!=2 or not all(isinstance(x,(int,float)) for x in v): E.append(f'dims {k} 要是 [寬,高]')
def mccheck(tag,mc,need4):
    o=mc.get('o',[])
    if not isinstance(o,list) or len(o)<2 or len(set(map(str,o)))!=len(o): E.append(f'{tag} 選項不足或重複'); return
    if need4 and len(o)!=4: W.append(f'{tag} 有 {len(o)} 個選項（規範是 4 選 1）')
    a=mc.get('a')
    if not isinstance(a,int) or isinstance(a,bool) or not 0<=a<len(o): E.append(f'{tag} 答案索引超出選項'); return
    e=mc.get('e',[])
    if not isinstance(e,list) or len(e)!=len(o): E.append(f'{tag} 詳解數 ≠ 選項數')
    elif not str(e[a]).startswith('正確'): W.append(f'{tag} 的正解詳解沒有以「正確」開頭')
for id,it in I.items():
    if not isinstance(it,dict): E.append(f'{id} 要是物件'); continue
    for f in ('n','z','img','f','c','p'):
        if f not in it: E.append(f'{id} 缺少 {f}')
    for f in ('f','c'):
        if f in it and not isinstance(it[f],list): E.append(f'{id} 的 {f} 要是陣列（一點一句）')
    for im in (it.get('img'),it.get('orig')):
        if im and im not in dims: E.append(f'{id} 的圖 {im} 沒有 dims（寬高）')
    if 'must' in it and not (it['must'] is True or isinstance(it['must'],str)): W.append(f'{id} 的 must 要是 true 或一段說明文字')
    mc=it.get('mc')
    if mc is not None and not isinstance(mc,dict): E.append(f'{id} 的 mc 要是物件')
    elif mc: mccheck(f'{id} 的 mc',mc,True)
    elif 'choice' in modes and F.get('drill'): W.append(f'{id} 沒有 mc，選擇題模式不會出這題')
seen=collections.Counter(); cids=[]
for c in D['chapters']:
    if not isinstance(c,dict): E.append('chapters 每一章要是物件'); continue
    for f in ('id','t'):
        if f not in c: E.append(f'章節缺少 {f}')
    for f in ('en','pg','plain'):
        if f not in c: W.append(f'章節 {c.get("id")} 缺少 {f}（網頁會顯示 undefined）')
    cids.append(c.get('id'))
    for i in c.get('items',[]):
        seen[i]+=1
        if i not in I: E.append(f'章節 {c.get("id")} 的項目 {i} 不存在')
    for t in c.get('trays',[]):
        if t not in G: E.append(f'章節 {c.get("id")} 的組合圖 {t} 不存在')
if len(set(cids))!=len(cids): E.append('章節 id 重複')
cids=set(cids)
for i in I:
    if seen[i]==0: E.append(f'項目 {i} 沒有放進任何章節')
    elif seen[i]>1: E.append(f'項目 {i} 在 {seen[i]} 個章節重複')
for tid,t in G.items():
    for f in ('n','z','img','list'):
        if f not in t: E.append(f'組合圖 {tid} 缺少 {f}')
    if t.get('img') and t['img'] not in dims: E.append(f'組合圖 {tid} 的圖沒有 dims')
    for r in t.get('list',[]):
        if not isinstance(r,list) or len(r)!=7: E.append(f'組合圖 {tid} 的清單列要有 7 欄：{r}')
        elif r[5] and r[5] not in I: W.append(f'組合圖 {tid} 第 {r[0]} 號連到不存在的項目 {r[5]}')
mids=collections.Counter()
for m in D.get('mnemonics',[]):
    mids[m.get('id')]+=1
    for f in ('id','ch','topic','mn','ans'):
        if f not in m: E.append(f'口訣 {m.get("id")} 缺少 {f}')
    if m.get('ch') not in cids: E.append(f'口訣 {m.get("id")} 的章節不存在')
    if m.get('after') and m['after'] not in I: E.append(f'口訣 {m.get("id")} 的 after 項目不存在')
for k,n in mids.items():
    if n>1: E.append(f'口訣 id {k} 重複')
for k,v in D.get('diagrams',{}).items():
    if not isinstance(v,dict) or not v.get('html'): E.append(f'示意圖 {k} 缺少 html'); continue
    if v.get('after') and v['after'] not in I: E.append(f'示意圖 {k} 的 after 項目不存在')
for x in D.get('cmp',[]):
    for f in ('id','t','head','rows'):
        if f not in x: E.append(f'對照表 {x.get("id")} 缺少 {f}')
    for r in x.get('rows',[]):
        if not isinstance(r,list) or not r: E.append(f'對照表 {x.get("id")} 有空的列'); continue
        if r[0] not in I: E.append(f'對照表 {x.get("id")} 的項目 {r[0]} 不存在')
        if 'head' in x and len(r)!=len(x['head']): W.append(f'對照表 {x.get("id")} 有一列格數 ≠ 表頭數 {len(x["head"])}')
for d in D.get('doubt',[]):
    if not isinstance(d,list): E.append('doubt 每一筆要是 [位置,講義原文,說明,依據] 陣列'); break
    if len(d)!=4: W.append('doubt 每一筆要是 [位置,講義原文,說明,依據] 四格'); break
nq=0
for cid,qs in D.get('quiz',{}).items():
    if cid not in cids: E.append(f'測驗的章節 {cid} 不存在')
    for i,q in enumerate(qs):
        nq+=1; tag=f'{cid} 測驗第 {i+1} 題'
        for f in ('s','q','o','a','e'):
            if f not in q: E.append(f'{tag} 缺少 {f}')
        mccheck(tag,q,False)
        if q.get('img') and q['img'] not in dims: E.append(f'{tag} 圖片沒有 dims')
nmc=sum(1 for it in I.values() if isinstance(it,dict) and it.get('mc')); nmust=sum(1 for it in I.values() if isinstance(it,dict) and it.get('must'))
print(f'項目 {len(I)}・章節 {len(cids)}・組合圖 {len(G)}・選擇題 {nmc}・必考 {nmust}・章節測驗 {nq} 題・口訣 {len(D.get("mnemonics",[]))}・示意圖 {len(D.get("diagrams",{}))}')
done()
