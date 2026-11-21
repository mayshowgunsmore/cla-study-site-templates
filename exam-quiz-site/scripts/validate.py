#!/usr/bin/env python3
"""Check data.json against references/schema.md. usage: validate.py DATA.json"""
import sys,json,collections
D=json.load(open(sys.argv[1],encoding='utf-8')); E=[]; W=[]
def err(m): E.append(m)
for k in ('site','units','exams','yearGroups','yearLabels','papers','answerSources','qs'):
    if k not in D: err('缺少欄位 '+k)
if E: print('\n'.join(E)); sys.exit(1)
S=D['site']
for k in ('title','h1','version','band','storageKey','dbDoc'):
    if k not in S: err('site 缺少 '+k)
uids={u['id'] for u in D['units']}
if len(uids)!=len(D['units']): err('units 的 id 重複')
for e in D['exams']:
    for u in e.get('units',[]) :
        if u not in uids: err(f'exams {e.get("key")} 的單元 {u} 不存在')
years=[y for g in D['yearGroups'] for y in g['years']]
if len(set(years))!=len(years): err('yearGroups 有年份重複')
for y in years:
    if y not in D['yearLabels']: err('yearLabels 缺少 '+y)
for k,p in D['papers'].items():
    if p['year'] not in D['yearLabels']: err(f'papers {k} 的 year {p["year"]} 沒有標籤')
ids=collections.Counter(q.get('id') for q in D['qs'])
for i,n in ids.items():
    if n>1: err('題目 id 重複：'+str(i))
topics=D.get('topics',{})
nw=0
for q in D['qs']:
    i=q.get('id','?')
    isw=bool(q.get('w'))
    if isw: nw+=1
    req=('id','u','ys','src','q','ans','as') if isw else ('id','u','ys','src','q','o','a','e','as')
    for k in req:
        if k not in q: err(f'{i} 缺少 {k}')
    need=('u','ans','ys','src') if isw else ('u','o','a','e','ys','src')
    if any(k not in q for k in need): continue
    if q['u'] not in uids: err(f'{i} 的單元 {q["u"]} 不存在')
    if isw:
        if not isinstance(q['ans'],list) or not q['ans']: err(f'{i} 非選題的 ans 要是「非空」的要點陣列')
        elif any(not isinstance(x,str) or not x.strip() for x in q['ans']): err(f'{i} 非選題的 ans 每個要點要是非空字串')
        if q.get('o'): err(f'{i} 非選題不要給 o（沒有選項）')
        if q.get('a'): err(f'{i} 非選題不要給 a（自評決定對錯）')
        if q.get('m'): err(f'{i} 非選題不能標多選')
        for f in ('e','kw'):
            if f in q and not isinstance(q[f],list): err(f'{i} 非選題的 {f} 要是陣列')
    else:
        n=len(q['o'])
        if not 2<=n<=5: err(f'{i} 選項數 {n}')
        if len(set(q['o']))!=n: W.append(f'{i} 有相同的選項文字')
        if len(q['e'])!=n: err(f'{i} 詳解數 {len(q["e"])} ≠ 選項數 {n}')
        L="ABCDE"[:n]
        if not q['a'] or any(x not in L for x in q['a']): err(f'{i} 答案 {q["a"]} 不在選項內')
        if q.get('m') and len(q['a'])<2: W.append(f'{i} 標多選但只有一個答案')
    for y in q['ys']:
        if y not in years: err(f'{i} 年份 {y} 不在 yearGroups')
    if q['src'][0]!=i: err(f'{i} 的 id 必須等於第一個出處 src[0]')
    for s in q['src']:
        if s.split('-')[0] not in D['papers']: err(f'{i} 出處 {s} 的考卷代碼不在 papers')
    if q['as'] not in D['answerSources']: err(f'{i} 答案來源 {q["as"]} 不在 answerSources')
    for t in q.get('t',[]):
        if t not in topics: err(f'{i} 觀念卡 {t} 不存在')
    if 'img' in q and (not isinstance(q['img'],list) or any(not str(s).startswith('data:image/') for s in q['img'])): err(f'{i} 的 img 要是 data:image/… 字串陣列')
    if 'ansImg' in q and (not isinstance(q['ansImg'],list) or any(not str(s).startswith('data:image/') for s in q['ansImg'])): err(f'{i} 的 ansImg 要是 data:image/… 字串陣列')
    if 'ansImg' in q and not q.get('w'): err(f'{i} 的 ansImg 只能用在非選題（w:1）')
    k=q.get('k',{})
    if not isinstance(k,dict): err(f'{i} 的 k 要是物件')
for k,T in topics.items():
    for f in ('t','s','k','c'):
        if f not in T: err(f'觀念卡 {k} 缺少 {f}')
print(f'題目 {len(D["qs"])}（選擇 {len(D["qs"])-nw}・非選 {nw}）・單元 {len(uids)}・觀念卡 {len(topics)}・考卷 {len(D["papers"])}')
for w in W: print('⚠️',w)
if E: print('\n'.join('❌ '+e for e in E)); sys.exit(1)
print('✅ 驗證通過')
