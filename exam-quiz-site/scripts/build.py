#!/usr/bin/env python3
"""Assemble a quiz site: template + data.json + theme.css (+ prompt.md) -> single HTML.
usage: build.py TEMPLATE DATA.json THEME.css OUT.html [--prompt PROMPT.md] [--schema SCHEMA.md]
--schema 只在提示詞含 {{SCHEMA}}、而規範檔不在預設位置時才需要指定。
TEMPLATE can be assets/template.html or a template.html exported from any site ("下載網站模板")."""
import sys,re,json,subprocess,os
a=sys.argv[1:]; pr=None; sch=None
if '--prompt' in a: i=a.index('--prompt'); pr=a[i+1]; del a[i:i+2]
if '--schema' in a: i=a.index('--schema'); sch=a[i+1]; del a[i:i+2]
tpl,dp,tp,out=a
t=open(tpl,encoding='utf-8').read(); D=json.load(open(dp,encoding='utf-8')); theme=open(tp,encoding='utf-8').read()
here=os.path.dirname(os.path.abspath(__file__))
r=subprocess.run([sys.executable,os.path.join(here,'validate.py'),dp],capture_output=True,text=True)
print(r.stdout.strip())
if r.returncode: print(r.stderr); sys.exit('validate.py 有錯誤，未輸出網站')
js=json.dumps(D,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c')
def sub(pat,new,s):
    s2,n=re.subn(pat,lambda m:new,s,count=1,flags=re.S); assert n==1,'模板缺少：'+pat; return s2
t=sub(r'(?<=<script id="site-data" type="application/json">).*?(?=</script>)',js,t)
t=sub(r'(?<=<style id="theme">).*?(?=</style>)','\n'+theme.replace('</','<\\/')+'\n',t)
title=D['site']['title'].replace('&','&amp;').replace('<','&lt;')
t=sub(r'(?<=<title>).*?(?=</title>)',title,t)
if pr:
    txt=open(pr,encoding='utf-8').read()
    if '{{SCHEMA}}' in txt:
        # 規範檔的位置依發布處而異：技能／正本 repo 用 references/schema.md，
        # 公開通用版用上一層的 data-json規範.md；都找不到時可用 --schema 明指。
        cands=[sch] if sch else [os.path.join(here,'..','references','schema.md'),
                                 os.path.join(here,'..','data-json規範.md'),
                                 os.path.join(here,'..','schema.md')]
        sp=next((c for c in cands if c and os.path.exists(c)),None)
        if not sp: sys.exit('找不到規範檔（references/schema.md 或 data-json規範.md），請用 --schema 指定路徑')
        txt=txt.replace('{{SCHEMA}}',open(sp,encoding='utf-8').read().strip())
    p=json.dumps(txt,ensure_ascii=False).replace('</','<\\/')
    t=sub(r'(?<=/\*PROMPT\*/).*?(?=/\*/PROMPT\*/)',p,t)
open(out,'w',encoding='utf-8').write(t)
print(f'輸出 {out}：{len(t.encode())/1024:.0f} KB，題目 {len(D["qs"])} 題')
