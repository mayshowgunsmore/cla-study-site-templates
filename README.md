# 讀書網站通用模板

用 Claude 把自己科目的講義、考古題做成讀書網站的通用模板與提示詞。三種網站都能離線使用、存個人進度。

| 資料夾 | 網站 | 用途 |
|---|---|---|
| `exam-quiz-site/` | 刷題網站 | 考古題逐選項詳解、非選題單字卡、錯題本、記憶曲線 |
| `interactive-review-site/` | 複習網站 | 白話說明、原圖穿插、口訣、遮重點、每節測驗 |
| `image-id-drill-site/` | 跑考認圖網站 | 玻片／器械圖譜、認圖選擇題與單字卡、A4 列印 |

## 怎麼用（讓 Claude 組裝，推薦）

1. 進到想做的網站資料夾，下載 `template.html`。
2. 打開 `提示詞.md`，整段複製。**最後一行是 `{{SCHEMA}}`，那是佔位字，一定要處理**：把那一行整行換成 `data-json規範.md` 的全部內容，再貼給 Claude。
   不想手動貼的話，也可以把 `提示詞.md` 和 `data-json規範.md` 兩個檔案一起附給 Claude，並告訴它「提示詞最後的 `{{SCHEMA}}` 就是指 `data-json規範.md`」。
   **沒處理這一行的話**，Claude 看不到資料格式規範，`data.json` 會寫錯、網站可能打不開。
3. 要在能執行程式、上傳檔案的 Claude 環境使用。依提示詞的問題附上 `template.html`、講義與考古題，回答科目、風格等問題。
4. Claude 只會寫 `data.json` 與配色，填進模板組成單一 HTML 網站。

## 自己用程式組裝

已經有 `data.json` 和配色檔時，可以不經過 Claude 直接組裝：

```bash
cd exam-quiz-site
python3 scripts/build.py template.html data.json themes/clean.css out.html \
    --prompt 提示詞.md
```

- **`--prompt` 一定要加。** 少了它，做出來的網站「網頁提示詞」區會是空白，「下載網站模板」也會給出空提示詞的模板。
- `--prompt` 會自動把提示詞裡的 `{{SCHEMA}}` 換成 `data-json規範.md` 的全文，所以這條路不用手動處理第 2 步那一行。
- 規範檔不在預設位置時，可以用 `--schema 路徑` 明指。
- `build.py` 會先跑 `validate.py` 檢查 `data.json`，有錯就不輸出。

先看格式再寫資料：

```bash
python3 scripts/validate.py data.json          # 單獨檢查 data.json
python3 scripts/build.py template.html example-data.json themes/clean.css \
    demo.html --prompt 提示詞.md                # 用範例資料做一個 demo 看看
```

## 每個資料夾裡有什麼

- `提示詞.md`：通用提示詞。結尾的 `{{SCHEMA}}` 是規範全文的佔位字（見上面第 2 步）
- `template.html`：網站模板（全部功能與版面，不需修改）。提示詞欄位是空的，由 `build.py --prompt` 或 Claude 填入
- `themes/`：配色範例
- `data-json規範.md`：資料格式規範，寫 `data.json` 前必讀
- `example-data.json`：可直接組裝的範例資料
- `scripts/`：`build.py` 組裝、`validate.py` 檢查、`align_check.py` 發布前對齊檢查、`pdf_figs.py` 從 PDF 取圖

這裡只有模板，不含任何課程內容；講義與考古題請用自己的。

by D45菜菜撈撈
