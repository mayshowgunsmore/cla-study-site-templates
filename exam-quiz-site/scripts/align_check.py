#!/usr/bin/env python3
"""發布前的對齊檢查：網站的模板程式與內嵌提示詞，是否和工具組 <kit> 完全一致。
用法：align_check.py <index.html> <kit 資料夾>
"""
import io, json, re, sys

page, kit = sys.argv[1], sys.argv[2]
SLOT = re.compile(r'/\*PROMPT\*/(.*?)/\*/PROMPT\*/', re.S)


def parts(html):
    base = re.search(r'<style id="base">(.*?)</style>', html, re.S).group(1)
    code = re.search(r'<script id="app-code">(.*?)</script>', html, re.S).group(1)
    m = SLOT.search(code)
    prompt = json.loads(m.group(1)) if m else None
    return base, SLOT.sub('/*PROMPT*//*/PROMPT*/', code), prompt


s = io.open(page, encoding='utf-8').read()
t = io.open(kit + '/assets/template.html', encoding='utf-8').read()
pb, pc, pp = parts(s)
tb, tc, _ = parts(t)
pr = io.open(kit + '/references/prompt.md', encoding='utf-8').read()
sc = io.open(kit + '/references/schema.md', encoding='utf-8').read().strip()
want = pr.replace('{{SCHEMA}}', sc)

ok = True
for name, good in (('模板樣式 base', pb == tb), ('模板程式 app-code', pc == tc), ('內嵌提示詞', pp == want)):
    print('  %-16s %s' % (name, '一致' if good else '不一致'))
    ok &= good
print('✅ 對齊' if ok else '❌ 沒對齊，不要發布')
sys.exit(0 if ok else 1)
