#!/usr/bin/env python3
"""Check data.json against references/schema.md. usage: validate.py DATA.json
❌ 錯誤：網站會壞掉或違反規範，build.py 不輸出網站；⚠️ 提醒：建議修正，仍可輸出。"""
import sys,json,re,collections
D=json.load(open(sys.argv[1],encoding='utf-8')); E=[]; W=[]
def err(m): E.append(m)
def warn(m): W.append(m)
def done():
    for w in W[:40]: print('⚠️',w)
    if len(W)>40: print(f'⚠️ 另有 {len(W)-40} 則')
    if E: print('\n'.join('❌ '+e for e in E)); sys.exit(1)
    print('✅ 驗證通過')
DATE=re.compile(r'^\d{4}-\d{2}-\d{2}$')
if not isinstance(D,dict): err('data.json 最上層要是物件'); done()
if D.get('schema')!='exam-quiz-site/1': warn(f'schema 應為 exam-quiz-site/1（目前 {D.get("schema")}）')
for k,t in (('site',dict),('units',list),('exams',list),('yearGroups',list),('yearLabels',dict),('papers',dict),('answerSources',dict),('qs',list)):
    if k not in D: err('缺少欄位 '+k)
    elif not isinstance(D[k],t): err(f'{k} 要是{"物件" if t is dict else "陣列"}')
for k,t in (('info',list),('lectures',list),('excluded',dict),('alias',dict),('coverageExtra',list),('topics',dict)):
    if k in D and not isinstance(D[k],t): err(f'{k} 要是{"物件" if t is dict else "陣列"}')
if E: done()
# site
S=D['site']
for k in ('title','h1','version','band','storageKey','dbDoc'):
    if k not in S: err('site 缺少 '+k)
if 'band' in S and (not isinstance(S['band'],list) or len(S['band'])>2 or any(not isinstance(x,str) for x in S['band'])): err('site.band 要是最多兩段文字的陣列')
if S.get('deco') not in (None,'pill','tissue','none'): err(f'site.deco 只能是 pill、tissue、none（目前 {S.get("deco")}）')
if 'storageKey' in S and not re.match(r'^[a-z0-9-]+$',str(S['storageKey'])): warn('site.storageKey 建議只用英數小寫與連字號（已發布的網站不要改）')
for k in ('title','h1','version','storageKey','dbDoc'):
    if k in S and (not isinstance(S[k],str) or not S[k].strip()): err(f'site.{k} 要是非空文字')
# answerSources
for k,a in D['answerSources'].items():
    if not isinstance(a,dict) or not a.get('label'): err(f'answerSources {k} 缺少 label')
    elif a.get('cls') not in (None,'ok','multi','chk'): warn(f'answerSources {k} 的 cls 只能是 ok、multi、chk（目前 {a.get("cls")}）')
# units
uids=[]
for u in D['units']:
    if not isinstance(u,dict): err('units 每一筆要是物件'); continue
    if not isinstance(u.get('id'),int) or isinstance(u.get('id'),bool): err(f'單元 {u.get("id")} 的 id 要是整數')
    for f in ('code','name'):
        if not u.get(f): err(f'單元 {u.get("id")} 缺少 {f}')
    uids.append(u.get('id'))
if len(set(uids))!=len(uids): err('units 的 id 重複')
uids=set(uids)
# exams
if not D['exams']: err('exams 至少要有一次考試（倒數與記憶曲線靠它）')
ekeys=set(); last=''
for e in D['exams']:
    if not isinstance(e,dict): err('exams 每一筆要是物件'); continue
    for f in ('key','name','date'):
        if not e.get(f): err(f'exams {e.get("key")} 缺少 {f}')
    if e.get('key') in ekeys: err(f'exams 的 key {e.get("key")} 重複')
    ekeys.add(e.get('key'))
    if e.get('date') and not DATE.match(str(e['date'])): err(f'exams {e.get("key")} 的 date 要寫成 YYYY-MM-DD')
    elif e.get('date'):
        if e['date']<last: warn('exams 要依考試日期由早到晚排')
        last=e['date']
    if 'units' in e:
        if not isinstance(e['units'],list): err(f'exams {e.get("key")} 的 units 要是陣列')
        else:
            for u in e['units']:
                if u not in uids: err(f'exams {e.get("key")} 的單元 {u} 不存在')
if len(D['exams'])>1 and sum('units' in e for e in D['exams'] if isinstance(e,dict))<len(D['exams']): warn('有兩次以上考試時，每次都要寫 units（沒寫的那次會包含全部單元）')
# years & papers
years=[]
for g in D['yearGroups']:
    if not isinstance(g,dict) or 'label' not in g or not isinstance(g.get('years'),list): err('yearGroups 每一組要有 label 與 years 陣列'); continue
    years+=g['years']
if len(set(years))!=len(years): err('yearGroups 有年份重複')
for y in years:
    if y not in D['yearLabels']: err('yearLabels 缺少 '+str(y))
for k,p in D['papers'].items():
    if not isinstance(p,dict) or 'year' not in p: err(f'papers {k} 缺少 year'); continue
    if '-' in k: err(f'papers 的考卷代碼 {k} 不能含「-」（出處用「-」分隔代碼與題號）')
    if p['year'] not in D['yearLabels']: err(f'papers {k} 的 year {p["year"]} 沒有標籤')
    if p.get('raw') is not None and (not isinstance(p['raw'],int) or isinstance(p['raw'],bool)): err(f'papers {k} 的 raw 要是整數或 null')
for k in D.get('excluded',{}):
    if k.split('-')[0] not in D['papers']: warn(f'excluded {k} 的考卷代碼不在 papers')
for x in D.get('coverageExtra',[]):
    if not isinstance(x,dict) or not x.get('name') or not x.get('prefix'): err('coverageExtra 每一列要有 name 與 prefix')
for x in D.get('info',[]):
    if not isinstance(x,dict) or 'h' not in x or 't' not in x: err('info 每一段要有 h 與 t')
# questions
ids=collections.Counter(q.get('id') for q in D['qs'] if isinstance(q,dict))
for i,n in ids.items():
    if n>1: err('題目 id 重複：'+str(i))
for o,n in D.get('alias',{}).items():
    if n not in ids: warn(f'alias {o} → {n}：新 id 不存在')
topics=D.get('topics',{})
nw=0
IMG=lambda v:isinstance(v,list) and all(str(s).startswith('data:image/') for s in v)
for q in D['qs']:
    if not isinstance(q,dict): err('qs 每一題要是物件'); continue
    i=q.get('id','?')
    if q.get('w') not in (None,0,1): err(f'{i} 的 w 只能是 1（非選題）或不給')
    isw=bool(q.get('w'))
    if isw: nw+=1
    req=('id','u','ys','src','q','ans','as') if isw else ('id','u','ys','src','q','o','a','e','as')
    miss=[k for k in req if k not in q]
    for k in miss: err(f'{i} 缺少 {k}')
    if miss: continue
    if not isinstance(q['ys'],list) or not q['ys']: err(f'{i} 的 ys 要是非空陣列'); continue
    if not isinstance(q['src'],list) or not q['src']: err(f'{i} 的 src 要是非空陣列'); continue
    if q['u'] not in uids: err(f'{i} 的單元 {q["u"]} 不存在')
    if not isinstance(q['q'],str) or not q['q'].strip(): err(f'{i} 的題幹 q 是空的')
    if isw:
        if not isinstance(q['ans'],list) or not q['ans']: err(f'{i} 非選題的 ans 要是「非空」的要點陣列')
        elif any(not isinstance(x,str) or not x.strip() for x in q['ans']): err(f'{i} 非選題的 ans 每個要點要是非空字串')
        for f,why in (('o','沒有選項'),('a','自評決定對錯'),('m','不能標多選')):
            if f in q: err(f'{i} 非選題不要給 {f}（{why}）')
        for f in ('e','kw'):
            if f in q and not isinstance(q[f],list): err(f'{i} 非選題的 {f} 要是陣列')
        if not any(re.match(r'^[^-]+-E\d+$',s) for s in q['src'][:1]): warn(f'{i} 非選題的出處題號建議用 E 開頭（例 11401M-E1）')
    else:
        if not isinstance(q['o'],list) or not isinstance(q['a'],list) or not isinstance(q['e'],list): err(f'{i} 的 o、a、e 都要是陣列'); continue
        n=len(q['o'])
        if not 2<=n<=5: err(f'{i} 選項數 {n}（要 2～5 個）')
        if len(set(map(str,q['o'])))!=n: warn(f'{i} 有相同的選項文字')
        if len(q['e'])!=n: err(f'{i} 詳解數 {len(q["e"])} ≠ 選項數 {n}')
        L="ABCDE"[:n]
        if not q['a'] or any(x not in L for x in q['a']): err(f'{i} 答案 {q["a"]} 不在選項內')
        elif len(q['e'])==n and not all(str(q['e'][L.index(x)]).startswith('正確') for x in q['a']): warn(f'{i} 正解的詳解沒有以「正確：」開頭')
        if q.get('m') not in (None,0,1): err(f'{i} 的 m 只能是 0 或 1')
        if q.get('m') and len(q['a'])<2: warn(f'{i} 標多選但只有一個答案')
        for f in ('ans','kw','ansImg'):
            if f in q: err(f'{i} 的 {f} 只能用在非選題（w:1）')
    for y in q['ys']:
        if y not in years: err(f'{i} 年份 {y} 不在 yearGroups')
    if q['src'][0]!=i: err(f'{i} 的 id 必須等於第一個出處 src[0]')
    for s in q['src']:
        if not isinstance(s,str) or s.count('-')!=1: err(f'{i} 出處 {s} 要寫成「考卷代碼-題號」（剛好一個「-」）')
        elif s.split('-')[0] not in D['papers']: err(f'{i} 出處 {s} 的考卷代碼不在 papers')
    if q['as'] not in D['answerSources']: err(f'{i} 答案來源 {q["as"]} 不在 answerSources')
    if 't' in q and not isinstance(q['t'],list): err(f'{i} 的 t 要是陣列')
    for t in (q.get('t') or []):
        if t not in topics: err(f'{i} 觀念卡 {t} 不存在')
    for f in ('img','ansImg'):
        if f in q and not IMG(q[f]): err(f'{i} 的 {f} 要是 data:image/… 字串陣列')
    k=q.get('k',{})
    if not isinstance(k,dict): err(f'{i} 的 k 要是物件')
    elif set(k)-{'白','專','錯'}: warn(f'{i} 的 k 只認 白、專、錯，其他會被忽略：{"、".join(set(k)-{"白","專","錯"})}')
    if 'n' in q and not isinstance(q['n'],str): err(f'{i} 的 n 要是文字')
for k,T in topics.items():
    for f in ('t','s','k','c'):
        if f not in T: err(f'觀念卡 {k} 缺少 {f}')
    for f in ('k','c'):
        if f in T and not isinstance(T[f],list): err(f'觀念卡 {k} 的 {f} 要是陣列')
print(f'題目 {len(D["qs"])}（選擇 {len(D["qs"])-nw}・非選 {nw}）・單元 {len(uids)}・觀念卡 {len(topics)}・考卷 {len(D["papers"])}')
done()
