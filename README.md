# 讀書網站通用模板

用 Claude 把自己科目的講義、考古題做成讀書網站的通用模板與提示詞。三種網站都能離線使用、存個人進度。

| 資料夾 | 網站 | 用途 |
|---|---|---|
| `exam-quiz-site/` | 刷題網站 | 考古題逐選項詳解、非選題單字卡、錯題本、記憶曲線 |
| `interactive-review-site/` | 複習網站 | 白話說明、原圖穿插、口訣、遮重點、每節測驗 |
| `image-id-drill-site/` | 跑考認圖網站 | 玻片／器械圖譜、認圖選擇題與單字卡、A4 列印 |

## 怎麼用

1. 進到想做的網站資料夾，下載 `template.html`。
2. 打開 `提示詞.md`，**整段複製**。
3. 在能執行程式、上傳檔案的 Claude 環境開一個新對話，貼上提示詞，附上 `template.html` 和你自己的講義、考古題、共筆。
4. Claude 會先一次問完需要的資訊（科目、考試、風格、標題區），回答後就會做好網站。

就這樣，不需要其他檔案。`提示詞.md` 已經包含資料格式規範，`template.html` 也已經內嵌提示詞，做出來的網站首頁「網頁提示詞」可以直接分享給下一個人。

## 自己用程式組裝（進階）

已經有 `data.json` 和配色檔時，可以不經過 Claude 直接組裝：

```bash
cd exam-quiz-site
python3 scripts/build.py template.html data.json themes/clean.css out.html
```

- `build.py` 會先跑 `validate.py` 檢查 `data.json`，有錯就不輸出。
- 想換成自己改過的提示詞時加 `--prompt 你的提示詞.md`。

先看格式再寫資料：

```bash
python3 scripts/validate.py data.json          # 單獨檢查 data.json
python3 scripts/build.py template.html example-data.json themes/clean.css demo.html   # 用範例資料做 demo
```

## 每個資料夾裡有什麼

- `template.html`：網站模板（全部功能與版面，已內嵌提示詞，不需修改）
- `提示詞.md`：給 Claude 的完整提示詞（已含資料格式規範）
- `themes/`：配色範例
- `data-json規範.md`：資料格式規範（已經包含在提示詞裡，這份是方便單獨查閱）
- `example-data.json`：可直接組裝的範例資料
- `scripts/`：`build.py` 組裝、`validate.py` 檢查、`align_check.py` 發布前對齊檢查、`pdf_figs.py` 從 PDF 取圖

這裡只有模板，不含任何課程內容；講義與考古題請用自己的。這個 repo 的檔案由私人正本自動產生，請不要直接在這裡修改。

by D45菜菜撈撈
