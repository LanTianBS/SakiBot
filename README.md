# 送報小祥 Discord Bot

本專案為針對 **MyGO** 與 **Ave Mujica** 截圖所開發的 Discord 搜尋機器人，支援使用台詞或角色進行過濾查詢。

本工具僅供粉絲學習、交流與非商業用途，請勿用於任何可能侵害原作權益之行為。

也請大家在玩梗、創作二創時保持尊重與謹慎，避免誤解或不當使用。

如有任何侵權疑慮，歡迎聯繫作者，我們將儘速協助下架或進行修正。

---

## 指令功能

- **/搜尋文字**：輸入關鍵字，搜尋最相近的動畫台詞。
- **/搜尋角色**：指定角色與關鍵字，搜尋該角色的相關台詞。
- **/回報**：表單回報圖片或資料問題，訊息會自動傳送給開發者。
- **/info**：查詢機器人目前狀態。
- **/help**：查詢所有可用指令與說明。
- **/leave**、**/sync**：伺服器管理與指令同步（僅限開發者使用）。

## 安裝與部署

1. **安裝依賴套件**

   ```shell
   pip install -r requirements.txt
   ```
2. **設定環境變數**

   - 建立 `.env` 檔案，內容範例：
     ```
     # 你的Discord ID(替換掉0000000000)
     user_discord_id=0000000000
     # 你的DiscordBotToken
     BT="TOKEN"
     # 搜尋指令冷卻時間（秒），預設 5 秒
     SEARCH_COOLDOWN=5
     ```
3. **準備資料檔案**

   - 於專案根目錄建立 `data.json`，內容範例格式如下：

```json
[
   {
      "子資料夾名稱": "1",
      "圖片名稱": "1-113.png",
      "掃描結果": "太好了,妳終於來了",
      "時間": "00:32",
      "角色": "爽世",
      "連結": "https://youtu.be/WOrYBIYIwyk?si=_Dyz_XBZ4dnqd6Y-&t=32s",
      "圖片連結": "https://i.postimg.cc/029HCPLr/1-113.png"
   },
   {
      "子資料夾名稱": "1",
      "圖片名稱": "1-123.png",
      "掃描結果": "妳全身都濕透了,沒事吧?",
      "時間": "00:35",
      "角色": "燈",
      "連結": "https://youtu.be/WOrYBIYIwyk?si=_Dyz_XBZ4dnqd6Y-&t=35s",
      "圖片連結": "https://i.postimg.cc/rwmnvgyk/1-123.png"
   }
   // ...可繼續新增更多資料
]
```

4. **啟動機器人**

   ```shell
   python main.py
   ```

## 使用教學與指令演示

### `/搜尋文字 <關鍵字>`

搜尋最相近的動畫台詞，支援自動補全。

![](https://i.postimg.cc/cLvv6f57/image.png)

### `/搜尋角色 <角色> <關鍵字>`

指定角色與關鍵字搜尋台詞，支援角色與台詞自動補全。

![](https://i.postimg.cc/0yhbSrLT/image.png)

### 搜尋結果展示

搜尋後會顯示出處、角色、圖片等資訊。

![](https://i.postimg.cc/2676gGVY/image.png)

### `/回報`

用於回報圖片或資料問題。

![img](https://i.postimg.cc/3wpWFYhd/image.png)

---

如需協助或有任何問題，請聯絡開發者。

開發者 Discord：**[blueskylt](https://discordapp.com/users/421650254992113666)**
