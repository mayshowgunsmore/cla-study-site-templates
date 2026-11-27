#!/usr/bin/env python3
"""Check data.json against references/schema.md. usage: validate.py DATA.json
❌ 錯誤：網站會壞掉或違反規範，build.py 不輸出網站；⚠️ 提醒：建議修正，仍可輸出。"""
import sys,json,re,collections
D=json.load(open(sys.argv[1],encoding='utf-8')); E=[]; W=[]
def done():
    for w in W[:40]: print('⚠️',w)
    if len(W)>40: print(f'⚠️ 另有 {len(W)-40} 則')
    if E: print('\n'.join('❌ '+e for e in E)); sys.exit(1)
    print('✅ 驗證通過')
if not isinstance(D,dict): E.append('data.json 最上層要是物件'); done()
if D.get('schema')!='interactive-review-site/1': W.append(f'schema 應為 interactive-review-site/1（目前 {D.get("schema")}）')
for k in ('site','chapters'):
    if k not in D: E.append('缺少欄位 '+k)
if E: done()
for k,t in (('site',dict),('chapters',list),('labels',dict),('tagDefs',dict),('info',list),('howto',list),('sprint',dict),('figCaptions',dict),('figSize',dict),('mnemonics',dict),('diagrams',dict),('widgets',dict),('place',dict),('key',list),('fix',list),('extra',list),('hot',list),('doubt',list),('cmp',list),('num',list),('gloss',dict),('quiz',dict),('features',dict),('verdictPatterns',list)):
    if k in D and not isinstance(D[k],t): E.append(f'{k} 要是{"物件" if t is dict else "陣列"}')
if E: done()
S=D['site']
for k in ('pageTitle','name','version','title','sub','h1','examName','examDefault','storageKey','dbDoc'):
    if k not in S: E.append('site 缺少 '+k)
if not re.match(r'^\d{4}-\d{2}-\d{2}$',str(S.get('examDefault',''))): E.append('site.examDefault 要寫成 YYYY-MM-DD')
if 'storageKey' in S and not re.match(r'^[a-z0-9-]+$',str(S['storageKey'])): W.append('site.storageKey 建議只用英數小寫與連字號（已發布的網站不要改）')
TABS=('home','key','sprint','cmp','num','mn','wrong','fav')
if 'tabs' in S:
    if not isinstance(S['tabs'],list): E.append('site.tabs 要是陣列')
    else:
        for t in S['tabs']:
            if t not in TABS: E.append(f'site.tabs 的 {t} 不是可用的分頁（{"、".join(TABS)}）')
TAGDEF=D.get('tagDefs') or {}
for k,v in TAGDEF.items():
    if not re.match(r'^[a-z0-9]+$',k): W.append(f'tagDefs 代號 {k} 建議只用英數小寫')
    if k in ('must','freq','past','nat','imp','teach','skip'): E.append(f'tagDefs 代號 {k} 和內建標籤重複')
    if not isinstance(v,dict) or not v.get('name'): E.append(f'tagDefs {k} 缺少 name'); continue
    if v.get('tone') not in (None,'blue','green','red','gold','gray'): W.append(f'tagDefs {k} 的 tone 只能是 blue、green、red、gold、gray')
LBLK={'must','keySub','sprintSub','mnSub','freq','freqTip'}
for k in (D.get('labels') or {}):
    if k not in LBLK: W.append(f'labels 的 {k} 模板不會用到')
for k in (D.get('features') or {}):
    if k not in ('wrong','fav','quizSource'): W.append(f'features 的 {k} 模板不會用到')
if (D.get('features') or {}).get('quizSource') not in (None,'section','question'): W.append('features.quizSource 只能是 section 或 question')
for x in D.get('verdictPatterns',[]):
    if not isinstance(x,list) or len(x)!=2: E.append('verdictPatterns 每一筆要是 ["正規表示式","標籤或 null"]'); continue
    try: re.compile(x[0])
    except re.error: W.append(f'verdictPatterns 的 {x[0]} 可能不是有效的正規表示式（請在瀏覽器確認）')
SECS={}; cids=set()
for c in D['chapters']:
    if not isinstance(c,dict): E.append('chapters 每一章要是物件'); continue
    for f in ('id','no','t','secs'):
        if f not in c: E.append(f'章節 {c.get("id")} 缺少 {f}')
    if c.get('id') in cids: E.append('章節 id 重複 '+str(c.get('id')))
    cids.add(c.get('id'))
    if not isinstance(c.get('secs',[]),list): E.append(f'章節 {c.get("id")} 的 secs 要是陣列'); continue
    for s in c.get('secs',[]):
        if s.get('id') in SECS: E.append('節 id 重複 '+str(s.get('id')))
        for f in ('id','t','src','html'):
            if f not in s: E.append(f'節 {s.get("id")} 缺少 {f}')
        SECS[s.get('id')]=s
        if '{{' in s.get('html',''): E.append(f'節 {s.get("id")} 內文殘留 {{{{')
        if not isinstance(s.get('tags',[]),list): E.append(f'節 {s.get("id")} 的 tags 要是陣列'); continue
        for t in s.get('tags',[]):
            if t not in ('must','freq','past','nat','imp') and t not in TAGDEF: W.append(f'節 {s.get("id")} 標籤 {t} 不是 must/freq/past/nat/imp 或 tagDefs 定義的標籤')
if 'secMap' in S:
    if not isinstance(S['secMap'],dict): E.append('site.secMap 要是物件')
    else:
        if not S.get('contentVersion'): W.append('site.secMap 要搭配 site.contentVersion 才會生效')
        for o,n in S['secMap'].items():
            if n not in SECS: E.append(f'site.secMap {o} → {n}：新節 id 不存在')
figs=D.get('figCaptions',{}); fsz=D.get('figSize',{}); mn=D.get('mnemonics',{}); dg=D.get('diagrams',{}); wg=D.get('widgets',{})
for k,v in figs.items():
    if not isinstance(v,list) or len(v)!=2: E.append(f'原圖 {k} 的 figCaptions 要是 ["圖說","出處"]')
    if k not in fsz: E.append(f'原圖 {k} 沒有 figSize')
for k,v in fsz.items():
    if not isinstance(v,list) or len(v)!=3 or not all(isinstance(x,(int,float)) for x in v[1:]): E.append(f'figSize {k} 要是 ["檔名",寬,高]')
ids=list(figs)+list(mn)+list(dg)+list(wg)
dup=[k for k,n in collections.Counter(ids).items() if n>1]
if dup: E.append('原圖／口訣／示意圖／互動圖代號重複：'+'、'.join(dup))
for nm,obj in (('口訣',mn),('示意圖',dg),('互動圖',wg)):
    for k,v in obj.items():
        if not isinstance(v,dict): E.append(f'{nm} {k} 要是物件'); continue
        if v.get('sec') not in SECS: E.append(f'{nm} {k} 的節 {v.get("sec")} 不存在')
for k,v in mn.items():
    for f in ('p','m','e'):
        if f not in v: E.append(f'口訣 {k} 缺少 {f}')
for k,v in dg.items():
    if 'svg' not in v or 'cap' not in v: E.append(f'示意圖 {k} 缺少 svg 或 cap')
for k,v in wg.items():
    if not v.get('t'): E.append(f'互動圖 {k} 缺少 t')
    if not v.get('opts'): E.append(f'互動圖 {k} 沒有 opts'); continue
    for o in v['opts']:
        if not isinstance(o,list) or len(o)!=3: E.append(f'互動圖 {k} 的 opts 每一項要是 ["代號","按鈕文字","說明"]'); continue
        if f'data-k="{o[0]}"' not in v.get('svg',''): W.append(f'互動圖 {k} 的選項 {o[0]} 在圖上沒有對應的 data-k（只能用按鈕切換）')
used=collections.Counter()
for sid,lst in D.get('place',{}).items():
    if sid not in SECS: E.append(f'place 的節 {sid} 不存在'); continue
    html=SECS[sid].get('html','')
    for x in lst:
        if not isinstance(x,list) or len(x)!=2: E.append(f'place {sid} 每一項要是 ["錨點文字","代號"]'); continue
        a,i=x
        used[i]+=1
        if i not in figs and i not in mn and i not in dg and i not in wg and i!='@skip': E.append(f'place {sid} 的項目 {i} 不存在')
        if a!='@end' and i!='@skip':
            n=html.count(a)
            if n!=1: E.append(f'place {sid} 的錨點出現 {n} 次（要剛好 1 次）：{a[:30]}')
for k in figs:
    if used[k]==0: E.append(f'原圖 {k} 沒有放進任何一節')
    elif used[k]>1: E.append(f'原圖 {k} 放了 {used[k]} 次')
for nm,obj in (('口訣',mn),('示意圖',dg),('互動圖',wg)):
    for k in obj:
        if used[k]==0: W.append(f'{nm} {k} 沒有放進內文（只出現在總表）' if nm=='口訣' else f'{nm} {k} 沒有放進內文')
# 列表：sec 必填的（網頁靠它找章節編號）
REQ={'key':('t','sec','q','p'),'fix':('sec','t','n','h','r'),'extra':('sec','t','s','d'),'hot':('sec','t','n'),'num':('g','v','d')}
for nm,fs in REQ.items():
    for j,x in enumerate(D.get(nm,[])):
        if not isinstance(x,dict): E.append(f'{nm} 第 {j+1} 筆要是物件'); continue
        for f in fs:
            if f not in x: E.append(f'{nm} 第 {j+1} 筆缺少 {f}')
        if x.get('sec') and x['sec'] not in SECS: E.append(f'{nm} 的節 {x["sec"]} 不存在')
for x in D.get('key',[]):
    if isinstance(x,dict) and x.get('t') not in ('must','freq','imp','nat','teach','skip') and x.get('t') not in TAGDEF: E.append(f'必考標記類型 {x.get("t")} 不對')
for j,c in enumerate(D.get('cmp',[])):
    if not isinstance(c,dict) or any(f not in c for f in ('g','t','h','rows')): E.append(f'cmp 第 {j+1} 張缺少 g、t、h 或 rows'); continue
    for r in c['rows']:
        if not isinstance(r,list) or len(r)!=len(c['h']): W.append(f'對照表「{c["t"]}」有一列格數 ≠ 表頭數 {len(c["h"])}')
if 'sprint' in D and 'fixHead' in D['sprint'] and (not isinstance(D['sprint']['fixHead'],list) or len(D['sprint']['fixHead'])!=3): E.append('sprint.fixHead 要是三格表頭')
for x in D.get('doubt',[]):
    if not isinstance(x,str): E.append('doubt 每一筆要是文字'); break
for k,v in D.get('gloss',{}).items():
    if not isinstance(v,str): E.append(f'gloss {k} 的中文要是文字')
nq=0;ns=0
for sid,qs in D.get('quiz',{}).items():
    if sid not in SECS: E.append(f'測驗的節 {sid} 不存在'); continue
    if not isinstance(qs,list): E.append(f'{sid} 的測驗要是陣列'); continue
    if not 3<=len(qs)<=8: W.append(f'{sid} 測驗 {len(qs)} 題（建議 3～8 題）')
    for i,q in enumerate(qs):
        nq+=1; ns+=bool(q.get('self'))
        tag=f'{sid} 第 {i+1} 題'
        for f in ('s','q','o','a','e','k'):
            if f not in q: E.append(f'{tag} 缺少 {f}')
        if 'o' not in q or 'a' not in q or 'e' not in q: continue
        if not isinstance(q['o'],list) or len(q['o'])<2: E.append(f'{tag} 至少要有 2 個選項'); continue
        if not isinstance(q['a'],int) or isinstance(q['a'],bool) or not 0<=q['a']<len(q['o']): E.append(f'{tag} 答案索引 {q["a"]} 超出選項'); continue
        if not isinstance(q['e'],list) or len(q['e'])!=len(q['o']): E.append(f'{tag} 詳解數 ≠ 選項數'); continue
        if not D.get('verdictPatterns') and not str(q['e'][q['a']]).startswith('正確'): W.append(f'{tag} 正解的詳解沒有以「正確」開頭')
        if len(set(map(str,q['o'])))!=len(q['o']): W.append(f'{tag} 有相同的選項文字')
print(f'章節 {len(D["chapters"])}・節 {len(SECS)}・原圖 {len(figs)}・口訣 {len(mn)}・示意圖 {len(dg)}・互動圖 {len(wg)}・測驗 {nq} 題（自編 {ns}）・註解 {len(D.get("gloss",{}))}')
done()
