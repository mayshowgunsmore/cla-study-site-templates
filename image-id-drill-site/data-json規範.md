## data.json 規範（image-id-drill-site/1）

網站＝模板（固定程式與版面）＋ data.json（這一科的內容與設定）＋ theme.css（風格）＋ fig/ 資料夾（圖片，檔名＝圖片代號.jpg）。只寫 data.json、theme.css 與圖片，不改模板。全站台灣繁體中文，英文專有名詞寫成「英文(中文)」。

文字裡用 `==關鍵字==` 標出遮重點時要蓋住的字（功能、特徵、口訣解開、選擇題詳解都可以用）；`info`、`howto`、`heroLine`、`keyNote` 可放簡單 HTML，其餘欄位一律純文字。

### 最上層
```json
{"schema":"image-id-drill-site/1","site":{},"features":{},"labels":{},"info":[],"howto":[],"keyNote":"",
 "items":{},"groups":{},"chapters":[],"mnemonics":[],"cmp":[],"doubt":[],"quiz":{},"dims":{},"diagrams":{}}
```

### site（網站設定）
| 欄位 | 說明 |
|---|---|
| pageTitle | 網頁名稱，例 `學校_病理實驗期中跑考_學期_作者_v1.0`，空著的項目省略 |
| h1 / topTitle | 首頁大標、頂列短標題 |
| version | 例 `v1.0`，改版時和 pageTitle 一起改 |
| band | 標籤帶左右兩段：`["學校・科目・系級・學期・by 作者","範圍"]`，空著的項目省略 |
| heroLine | 大標下一行說明，可用 `{items}`、`{groups}`、`{mn}`、`{diag}`、`{cmp}`、`{chapters}` |
| examDefault | 預設考試日 `YYYY-MM-DD` |
| storageKey / dbDoc | 存檔名稱（英數小寫加連字號，例 `school-patho-lab-mid-v1`、`progress`）。**發布後永遠不可改** |

### features（開工前問答的結果）
`{"atlas":true,"drill":true,"modes":["choice","flash"]}`
- `atlas`：圖譜（各章卡片、只看圖、目錄、放大）。
- `drill`：跑考練習（含錯題本、收藏本、記憶曲線）。
- `modes`：作答模式，`choice` 選擇題、`flash` 單字卡；兩個都放時設定頁最上方出現切換，第一個是預設。兩種模式的作答紀錄、排程、錯題本分開（選擇題的紀錄 key 是 `C:`＋項目代號），收藏共用。

### labels（用詞）
| 欄位 | 器械例 | 玻片例 |
|---|---|---|
| item | 器械 | 玻片 |
| f / c | 功能／特徵 | 看片重點／鑑別 |
| nameOrder | `en`（英文在前） | `zh`（中文在前） |
| question | 這是什麼器械？功能是什麼？ | 這張玻片的診斷是什麼？ |
| source | 器械講義 | 講義 |
| group / groupsTitle / groupsEn | 托盤／托盤擺設／Tray Set-Ups | （沒有組合圖可省略） |
| searchHint | 搜尋框提示 | |

### 首頁文字
- `info`：「網頁說明」每一條（可用上面的代換）。要寫範圍與依據、譯名說明、原圖數量、必考標記來源、哪些是自編與沒有老師審閱、遮標註的方式、進度存在哪裡。
- `howto`：「怎麼用」每一條。
- `keyNote`：必考頁上方的提醒（例如標記來源、沒標到的一樣可能考）。

### items（每一張圖＝一題）
```json
"appy":{"n":"Acute appendicitis","z":"急性闌尾炎","img":"s2_1m","orig":"s2_1","p":3,"pp":5,
 "f":["看片重點或功能，可用 ==關鍵字=="],"c":["特徵或鑑別"],"ef":"英文原文（可省略）","ec":"",
 "hw":"講義手寫（可省略）","warn":"留意（可省略）","must":"考肌層浸潤",
 "mc":{"o":["選項A","選項B","選項C","選項D"],"a":0,"e":["正確：…（頁碼）","…和這張圖的差別",…],"leak":false,"q":"題幹（洩題原題才需要）"}}
```
- 代號是作答紀錄的 key，發布後不可改。
- `img`：練習用的圖（玻片要遮掉標註）；`orig`：有標註的原圖（圖譜與答完後顯示）。沒有兩版時只寫 `img`。
- `p`：講義 PDF 頁碼；`pp`：印刷頁碼（可省略）。
- `must`：教材明寫的必考標記，`true` 或一段說明（例如「考白色箭頭」）。有任何項目標了 `must` 時，跑考練習的「題數與順序」會多一排「全部／★ 只出必考」篩選，可以和出題順序一起用。
- `mc`：選擇題模式才需要。4 選 1，正解位置分散。
  - 自編題目：題幹（`labels.question`、要另外寫 `q` 的題目、每章測驗 `quiz` 的 `q`）其餘用中文，但裡面的器官、構造、病名、器械名只寫英文、不加中文。
  - 自編題目：`o` 的四個選項**只寫英文專有名詞**（例如 `Clear cell renal cell carcinoma`），不加中文；干擾選項取同章、盡量同節或同部位的相關項目。`e` 的每一條都以「英文(中文)」開頭再接說明，正解那條寫「正確：英文(中文)。…（出處頁碼）」。
  - 洩題或考古原題：`leak:true`，`q` 放原題幹，`o` 的文字與順序完全照原樣（原本中英夾雜就照舊），`e` 一樣逐選項寫。

### chapters
`[{"id":"s2","t":"發炎","en":"Inflammation","pg":"p.3–5","plain":"白話說","items":["appy","gran"],"trays":[]}]`
每個項目只能屬於一章。只有組合圖、沒有單項的章（例如托盤擺設）會成為獨立分頁。

### groups（組合圖，可省略）
`{"t_basic":{"n":"Basic Tray Set-Up","z":"基本托盤","img":"t_basic","p":19,"pp":36,"lp":19,"lpp":36,"note":"",
 "list":[[1,"英文名","中文名",0或1(螢光筆),"手寫字","對應的項目代號","通用拼法"],…]}}`

### 其他
- `mnemonics`：`[{"id":"mn1","ch":"s2","after":"項目代號","topic":"考點","mn":"口訣","ans":"解開（==關鍵字==）"}]`
- `cmp`：`[{"id":"cmp1","t":"標題","head":["項目","…"],"rows":[["項目代號","格",…]]}]`
- `doubt`：講義疑誤 `[["位置","講義原文","說明","依據"]]`
- `quiz`：每章測驗（可省略）`{"s2":[{"s":"出處","q":"題幹","o":[…],"a":0,"e":[…],"img":"可省略"}]}`（每章測驗在網頁上整章標「自編」，不必逐題標記）
- `dims`：每張圖的寬高 `{"s2_1":[寬,高]}`，所有用到的圖都要有（「下載離線版」也靠它找出要打包的圖）
- `diagrams`：自繪示意圖 `{"d1":{"after":"項目代號","cmp":false,"html":"<figure class=\"card diag\">…</figure>"}}`；`cmp:true` 也放進對照頁

### theme.css（風格）
只放 CSS 變數；淺色寫在 `:root{}`，深色寫兩次：`@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){…}}` 與 `:root[data-theme="dark"]{…}`。
| 變數 | 用途 |
|---|---|
| --paper、--grid | 頁面底色、背景格線 |
| --surface、--surface2、--line | 卡片底、次要底、框線 |
| --ink、--muted | 主文字、次要文字 |
| --blue、--blue-soft、--on-blue | 連結、進度、選取色與其上的字色 |
| --main、--on-main | 主要按鈕與其上的字色 |
| --red/-soft、--green/-soft | 答錯與必考框、答對 |
| --hi、--hi-soft、--hi-ink、--on-hi | 螢光筆強調、標記、遮重點按鈕 |
| --tape、--mask、--photo | 紙膠帶、遮重點色塊、圖片底色 |
| --good、--bad | 答對、答錯文字 |
| --sans、--hand、--mono | 內文、標題、數字字型 |
