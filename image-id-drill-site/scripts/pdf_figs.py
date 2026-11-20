#!/usr/bin/env python3
"""從 PDF 取出圖片：能用原始圖檔就用原始圖檔，圖上有疊加標註或多張拼在一起時，
依圖在頁面上的位置、以原圖解析度渲染那一區（位置取自 PDF 本身，不會截歪）。

用法：python3 pdf_figs.py 檔案.pdf 輸出資料夾 [--prefix n01] [--pages 3-12]
        [--max-width 1300] [--quality 85] [--both]
  --both：圖上有疊加標註時，另存一張沒有標註的原始圖檔（<名稱>-raw.jpg），
          認圖片網站可直接拿來當練習用的 img。
輸出：每張圖一個 JPEG，加上 figs.json（頁碼、位置、取法、圖上方最近一行字，方便對題號／段落）。
需要 PyMuPDF：pip install pymupdf --break-system-packages
"""
import sys, os, json, argparse, collections
import pymupdf

ap = argparse.ArgumentParser()
ap.add_argument("pdf"); ap.add_argument("out")
ap.add_argument("--prefix", default="p"); ap.add_argument("--pages")
ap.add_argument("--max-width", type=int, default=1300)
ap.add_argument("--quality", type=int, default=85)
ap.add_argument("--both", action="store_true")
ap.add_argument("--gap", type=float, default=10, help="相鄰幾 pt 內的圖合併成一張")
a = ap.parse_args()
os.makedirs(a.out, exist_ok=True)
doc = pymupdf.open(a.pdf)
N = len(doc)
if a.pages:
    s, _, e = a.pages.partition("-"); pages = range(int(s) - 1, int(e or s))
else:
    pages = range(N)

# 投影片背景、校徽等：同一張圖出現在很多頁就略過
cnt = collections.Counter()
for p in doc:
    for x in {i["xref"] for i in p.get_image_info(xrefs=True) if i["xref"]}:
        cnt[x] += 1
bg = {x for x, n in cnt.items() if n >= max(3, N * 0.3)}

def to_rgb(pix):
    if pix.alpha or pix.n - pix.alpha != 3:
        pix = pymupdf.Pixmap(pymupdf.csRGB, pix) if pix.n - pix.alpha != 3 else pix
        if pix.alpha: pix = pymupdf.Pixmap(pix, 0)
    return pix

def save(pix, path, rot=0):
    from PIL import Image
    im = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    if rot: im = im.rotate(-rot, expand=True)
    if im.width > a.max_width:
        im = im.resize((a.max_width, round(im.height * a.max_width / im.width)), Image.LANCZOS)
    im.save(path, "JPEG", quality=a.quality, optimize=True)
    return im.size

index, notes = [], []
for pno in pages:
    page = doc[pno]; rot = page.rotation
    if rot: page.set_rotation(0)  # 旋轉頁：圖框、文字、線條與渲染一律用未旋轉的座標，存檔時再轉回來
    prect = page.rect; parea = prect.width * prect.height
    infos = []
    for i in page.get_image_info(xrefs=True):
        r = pymupdf.Rect(i["bbox"]) & prect
        if r.is_empty or r.width < 45 or r.height < 30: continue
        if i["xref"] in bg: continue
        if r.width * r.height > parea * 0.9:
            notes.append({"page": pno + 1, "note": "整頁是一張圖（多半是掃描檔）：要的圖得用渲染裁切，請看頁面決定範圍"}); continue
        infos.append((r, i))
    if not infos and len(page.get_drawings()) > 40:
        notes.append({"page": pno + 1, "note": "這頁沒有圖檔但有很多向量線條，可能是向量繪圖，要的話用渲染裁切"})
    # 相鄰 gap 內的圖合併
    groups = [[x] for x in infos]
    merged = True
    while merged:
        merged = False
        for g in range(len(groups)):
            for h in range(g + 1, len(groups)):
                R1 = pymupdf.Rect(groups[g][0][0]); [R1.include_rect(x[0]) for x in groups[g]]
                R2 = pymupdf.Rect(groups[h][0][0]); [R2.include_rect(x[0]) for x in groups[h]]
                if (R1 + (-a.gap, -a.gap, a.gap, a.gap)).intersects(R2):
                    groups[g] += groups.pop(h); merged = True; break
            if merged: break
    words = page.get_text("words")
    draws = [d["rect"] for d in page.get_drawings()]
    groups.sort(key=lambda g: (min(x[0].y0 for x in g), min(x[0].x0 for x in g)))
    for k, g in enumerate(groups, 1):
        R0 = pymupdf.Rect(g[0][0]); [R0.include_rect(x[0]) for x in g]
        # 疊加的標註（文字框、箭頭、引線）常常超出圖的邊界：把貼著圖的標註一起框進來
        R = pymupdf.Rect(R0); ow, od = [], []
        for _ in range(4):
            near = R + (-a.gap, -a.gap, a.gap, a.gap)
            od = [d for d in draws if d.intersects(near) and not (d.width >= R.width * 0.95 and d.height >= R.height * 0.95)
                  and d.width * d.height < parea * 0.5]
            ow = [w for w in words if pymupdf.Rect(w[:4]).intersects(near)]
            R2 = pymupdf.Rect(R0)
            for d in od: R2.include_rect(d & prect)
            for w in ow: R2.include_rect(pymupdf.Rect(w[:4]))
            if R2 == R: break
            R = R2
        ow = [w[4] for w in ow]
        above = [w for w in words if w[3] <= R.y0 + 2 and w[3] > R.y0 - 80]
        above_line = " ".join(w[4] for w in sorted(above, key=lambda w: (-w[3], w[0]))[:12])
        name = f"{a.prefix}{pno + 1}-{k}"
        rec = {"file": name + ".jpg", "page": pno + 1, "bbox": [round(v, 1) for v in R], "image_bbox": [round(v, 1) for v in R0],
               "images": len(g), "overlay_words": len(ow), "overlay_drawings": len(od),
               "text_above": above_line, "overlay_text": " ".join(ow[:30])}
        if len(g) == 1 and not ow and not od and R == R0 and not rot:
            pix = to_rgb(pymupdf.Pixmap(doc, g[0][1]["xref"]))
            rec["mode"] = "原始圖檔"
        else:
            native = max(x[1]["width"] / (x[0].width / 72) for x in g)
            dpi = int(min(400, max(200, native)))
            pix = page.get_pixmap(clip=(R + (-3, -3, 3, 3)) & prect, dpi=dpi)
            rec["mode"] = f"依位置渲染 {dpi} dpi（" + ("多張合併" if len(g) > 1 else "圖上有疊加標註") + "）"
            if a.both and len(g) == 1:
                raw = to_rgb(pymupdf.Pixmap(doc, g[0][1]["xref"]))
                rec["raw_file"] = name + "-raw.jpg"; save(raw, os.path.join(a.out, rec["raw_file"]), rot)
        rec["size"] = save(pix, os.path.join(a.out, rec["file"]), rot)
        index.append(rec)
json.dump({"source": os.path.basename(a.pdf), "skipped_backgrounds": len(bg), "figs": index, "notes": notes},
          open(os.path.join(a.out, "figs.json"), "w"), ensure_ascii=False, indent=1)
modes = collections.Counter(r["mode"].split("（")[0] for r in index)
print(f"{len(index)} 張圖，略過背景圖 {len(bg)} 種；" + "、".join(f"{m} {n}" for m, n in modes.items()) + (f"；需注意的頁 {len(notes)}" if notes else ""))
