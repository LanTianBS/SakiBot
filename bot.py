import discord
from discord import app_commands,ui
import logging
import sys
from dotenv import load_dotenv
import os
import json
import difflib
load_dotenv()
# 基本設定
BT=os.getenv("BT")
user_discord_id = int(os.getenv("user_discord_id"))
SEARCH_COOLDOWN = int(os.getenv("SEARCH_COOLDOWN", 7))
async def isAdmin(id):
    if str(id) == str(user_discord_id):
        return True
    else:
        return False
# 啟動機器人
def run_discord_bot():
    try:
        # 多伺服器處理
        class MyClient(discord.Client):
            def __init__(self, *, intents: discord.Intents):
                super().__init__(intents=intents)
                self.tree = app_commands.CommandTree(self)
            async def setup_hook(self):
                guilds = self.guilds
                for guild in guilds:
                    self.tree.copy_global_to(guild=guild)
                    await self.tree.sync(guild=guild)
        # 實體建構         
        intents = discord.Intents.all()
        intents.message_content = True
        client = MyClient(intents=intents)
        # 日誌
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s %(levelname)s %(message)s',
            handlers=[
                logging.FileHandler("bot.log", encoding="utf-8"),
                logging.StreamHandler(sys.stdout)
            ]
        )
        # 機器人啟動訊息
        @client.event
        async def on_ready():
            try:
                global user
                user = await client.fetch_user(user_discord_id) # 開發者設定
                activity = discord.Activity(type=discord.ActivityType.listening, name="春日影")
                await client.change_presence(activity=activity)
                try:
                    print("機器人起動中...")
                    print("同步指令中...")
                    try:
                        await client.setup_hook()
                        print(f"已同步指令到 {len(client.guilds)} 個伺服器\n")
                    except Exception as sync_error:
                        logging.error(f"指令同步失敗: {sync_error}")
                        print(f"指令同步失敗: {sync_error}")
                    print(f"機器人名稱: {client.user.name} (ID: {client.user.id}),已上線！\n目前已加入 {len(client.guilds)} 個伺服器。\n"+"-"*30)
                except Exception as e:
                    logging.error(f"機器人啟動失敗: {e}")
                    print(f"機器人啟動失敗: {e}")
                    # 傳送訊息給開發者
                    if user:
                        await user.send(f"> :x: 機器人啟動失敗\n錯誤訊息: {e}")
            except Exception as e:
                logging.error(f"機器人啟動外部錯誤: {e}")
                print(f"機器人啟動外部錯誤: {e}")
            
        # 機器人加入伺服器事件
        @client.event
        async def on_guild_join(guild):
            print(f"機器人加入了新伺服器：{guild.name} (ID: {guild.id})")
            # 同步指令
            new_guild = discord.Object(id=guild.id)
            sync_msg = ""
            try:
                await client.setup_hook()
                sync_msg = "\n> ✅ 指令同步成功！"
            except Exception as e:
                sync_msg = f"\n> ❌ 指令同步失敗：{e}"
            embed = discord.Embed(
                title=":white_check_mark: 機器人已加入新伺服器",
                description=f"> 機器人已加入 `{guild.name}` (ID: `{guild.id}`)！{sync_msg}",
                color=0x00ff00
            )
            userOP = await client.fetch_user(user_discord_id)
            await userOP.send(embed=embed)
            
        # 機器人退出伺服器事件
        @client.event
        async def on_guild_remove(guild):
            print(f"機器人退出了伺服器：{guild.name} (ID: {guild.id})")
            embed = discord.Embed(
                title=":x: 機器人已退出伺服器",
                description=f"> 機器人已退出 `{guild.name}` (ID: `{guild.id}`)！",
                color=0xff0000
            )
            userOP = await client.fetch_user(user_discord_id)
            await userOP.send(embed=embed)

        # 同步指令(開發人員指令)
        @client.tree.command()
        async def sync(interaction: discord.Interaction):
            """同步指令(僅限開發人員)"""
            if interaction.user.id == user_discord_id:
                await client.setup_hook()
                await interaction.response.send_message("> ✅ 同步指令成功！", ephemeral=True)
            else:
                await interaction.response.send_message("> ❌ 你沒有權限這麼做！", ephemeral=True)

        #HELP指令
        @client.tree.command()
        @app_commands.describe(page="頁數")
        async def help(interaction: discord.Interaction, page: int = 1):
            """:question: 查詢指令"""
            commands = list(client.tree.walk_commands())
            if interaction.user.id != user_discord_id:
                commands = [cmd for cmd in commands if not (cmd.description and "僅限開發人員" in cmd.description)]
                total_pages = (len(commands) + 9) // 10  # 每頁 10 條
                page = max(1, min(page, total_pages))
                start = (page - 1) * 10
                end = start + 10
                embed = discord.Embed(description="**Made by By blueskylt**\n你可以使用以下指令", color=0xff0000)
                embed.set_author(name="送報小祥", icon_url="https://i.postimg.cc/3xVY4Yjc/image.png")
            for command in commands[start:end]:
                embed.add_field(name=f"/{command.name}", value=command.description or "", inline=False)
                embed.set_footer(text=f"Page {page}/{total_pages} - 使用 /help <頁數> 來查看其他頁面")
            await interaction.response.send_message(embed=embed, ephemeral=True)

        # INFO指令
        @client.tree.command()
        async def info(interaction: discord.Interaction):
            """查詢機器人狀態"""
            server_count = len(client.guilds)
            latency = round(client.latency * 1000)  # 毫秒
            embed = discord.Embed(title="ℹ️ 機器人資訊", color=0x3498db)
            embed.add_field(name="已加入的伺服器數量", value=f"{server_count} 個", inline=False)
            embed.add_field(name="延遲", value=f"{latency} ms", inline=False)
            await interaction.response.send_message(embed=embed, ephemeral=True)

        # 搜尋文字指令
        @client.tree.command()
        @app_commands.describe(query="要搜尋的台詞")
        @app_commands.checks.cooldown(1, SEARCH_COOLDOWN, key=lambda i: i.user.id)
        async def 搜尋文字(interaction: discord.Interaction, query: str):
            """搜尋最相近的掃描結果"""
            import json
            import difflib
            try:
                with open("data.json", "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception as e:
                logging.error(f"搜尋文字 data.json 讀取失敗: {e}")
                await interaction.response.send_message("❌ 伺服器資料異常，請聯絡開發人員！", ephemeral=True)
                return
            try:
                # 先找有包含關鍵字的
                contains = [item for item in data if query in item["掃描結果"]]
                not_contains = [item for item in data if query not in item["掃描結果"]]
                scored = []
                for item in not_contains:
                    score = difflib.SequenceMatcher(None, query, item["掃描結果"]).ratio()
                    scored.append((score, item))
                scored.sort(reverse=True, key=lambda x: x[0])
                # 只取最相近一筆
                if contains:
                    best = contains[0]
                elif scored:
                    best = scored[0][1]
                else:
                    await interaction.response.send_message("❌ 找不到相關台詞！", ephemeral=True)
                    return
                ep = best["子資料夾名稱"]
                time = best["時間"]
                link = best["連結"]
                result = best["掃描結果"]
                role = best["角色"]
                img_name = best["圖片名稱"].replace(".png", "") if "圖片名稱" in best else "無資料"
                img_url = best.get("圖片連結", None)
                embed = discord.Embed(title=f"📢 搜尋結果通知 (由{interaction.user.display_name}搜尋)", color=0x3498db)
                embed.add_field(name="🔎 搜尋關鍵字", value=query, inline=False)
                embed.add_field(name="📺 出自", value=f"第{ep}集 的 [{time}]({link})", inline=False)
                embed.add_field(name="🎭 角色", value=role, inline=False)
                embed.add_field(name="💬 台詞", value=f"[{role}] {result}", inline=False)
                embed.add_field(name="🆔 圖片編號", value=img_name, inline=False)

                if img_url:
                    embed.set_image(url=img_url)
                else:
                    embed.add_field(name="圖片狀態", value="❌ 找不到對應圖片！", inline=False)
                embed.set_footer(text="輸出結果如有錯誤請聯絡作者")
                await interaction.response.send_message(embed=embed, ephemeral=False)
            except Exception as e:
                logging.error(f"搜尋文字指令錯誤: {e}")
                await interaction.response.send_message("❌ 查詢過程發生錯誤，請聯絡開發人員！", ephemeral=True)

        @搜尋文字.autocomplete("query")
        async def 搜尋文字_autocomplete(interaction: discord.Interaction, current: str):
            import json
            with open("data.json", "r", encoding="utf-8") as f:
                data = json.load(f)
            # 顯示 [角色] 台詞內容
            results = [(item["角色"], item["掃描結果"]) for item in data if current in item["掃描結果"]]
            return [app_commands.Choice(name=f"[{role}] {text}", value=text) for role, text in results[:25]]

        # 回報問題指令
        @client.tree.command()
        async def 回報(interaction: discord.Interaction):
            """回報圖片相關問題，訊息會傳送給開發者"""
            from discord import ui
            class ReportModal(ui.Modal, title="問題回報表單"):
                img_id = ui.TextInput(label="圖片ID", placeholder="請輸入圖片ID", required=True)
                issue = ui.TextInput(label="回報問題", style=discord.TextStyle.paragraph, placeholder="請詳細描述問題", required=True)
                async def on_submit(self, interaction2: discord.Interaction):
                    embed = discord.Embed(title="📝 使用者回報問題", color=0xff9900)
                    embed.add_field(name="🆔 圖片ID", value=self.img_id.value, inline=False)
                    embed.add_field(name="❗ 問題描述", value=self.issue.value, inline=False)
                    embed.add_field(name="👤 使用者名稱Tag", value=interaction2.user.name + "#" + interaction2.user.discriminator, inline=False)
                    embed.set_footer(text=f"由 {interaction2.user.display_name} (ID: {interaction2.user.id}) 回報")
                    dev_user = await interaction2.client.fetch_user(user_discord_id)
                    await dev_user.send(embed=embed)
                    await interaction2.response.send_message("✅ 已回報問題，感謝你的協助！", ephemeral=True)
            await interaction.response.send_modal(ReportModal())

        角色選項 = ["燈", "愛音", "樂奈", "爽世", "立希", "祥子", "睦", "初華", "海鈴", "若麥", "Ｏthers"]

        @client.tree.command()
        @app_commands.describe(role="指定角色（必選）", query="搜尋該角色台詞（必選）")
        @app_commands.checks.cooldown(1, SEARCH_COOLDOWN, key=lambda i: i.user.id)
        async def 搜尋角色(interaction: discord.Interaction, role: str, query: str):
            """透過角色和關鍵字搜尋台詞"""
            try:
                with open("data.json", "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception as e:
                logging.error(f"搜尋角色 data.json 讀取失敗: {e}")
                await interaction.response.send_message("❌ 伺服器資料異常，請聯絡開發人員！", ephemeral=True)
                return
            try:
                filtered = [item for item in data if item["角色"] == role]
                if not filtered:
                    await interaction.response.send_message(f"❌ 找不到角色 {role} 的台詞！", ephemeral=True)
                    return
                contains = [item for item in filtered if query in item["掃描結果"]]
                not_contains = [item for item in filtered if query not in item["掃描結果"]]
                scored = []
                for item in not_contains:
                    score = difflib.SequenceMatcher(None, query, item["掃描結果"]).ratio()
                    scored.append((score, item))
                scored.sort(reverse=True, key=lambda x: x[0])
                if contains:
                    best = contains[0]
                elif scored:
                    best = scored[0][1]
                else:
                    await interaction.response.send_message(f"❌ 找不到角色 {role} 包含 '{query}' 的台詞！", ephemeral=True)
                    return
                ep = best["子資料夾名稱"]
                time = best["時間"]
                link = best["連結"]
                result = best["掃描結果"]
                img_name = best["圖片名稱"].replace(".png", "") if "圖片名稱" in best else "無資料"
                img_url = best.get("圖片連結", None)
                embed = discord.Embed(title=f"🎭 {role} 的台詞搜尋結果（關鍵字：{query}）", color=0x3498db)
                embed.add_field(name="🔎 搜尋關鍵字", value=query, inline=False)
                embed.add_field(name="📺 出自", value=f"第{ep}集 的 [{time}]({link})", inline=False)
                embed.add_field(name="🎭 角色", value=role, inline=False)
                embed.add_field(name="💬 台詞", value=result, inline=False)
                embed.add_field(name="🆔 圖片編號", value=img_name, inline=False)
                if img_url:
                    embed.set_image(url=img_url)
                else:
                    embed.add_field(name="圖片狀態", value="❌ 找不到對應圖片！", inline=False)
                embed.set_footer(text="只顯示最相近一筆，如需更多請聯絡作者")
                await interaction.response.send_message(embed=embed, ephemeral=False)
            except Exception as e:
                logging.error(f"搜尋角色指令錯誤: {e}")
                await interaction.response.send_message("❌ 查詢過程發生錯誤，請聯絡開發人員！", ephemeral=True)

        @client.tree.error
        async def on_app_command_error(interaction, error):
            if isinstance(error, app_commands.errors.CommandOnCooldown):
                await interaction.response.send_message(f"⏳ 請稍後再試！冷卻剩餘 {error.retry_after:.1f} 秒。", ephemeral=True)
            else:
                raise error
        
        @搜尋角色.autocomplete("role")
        async def 搜尋角色_autocomplete(interaction: discord.Interaction, current: str):
            import json
            with open("data.json", "r", encoding="utf-8") as f:
                data = json.load(f)
            roles = sorted(set(item["角色"] for item in data))
            results = [r for r in roles if current in r]
            return [app_commands.Choice(name=r, value=r) for r in results[:25]]

        @搜尋角色.autocomplete("query")
        async def 搜尋角色_query_autocomplete(interaction: discord.Interaction, current: str):
            import json
            role = interaction.namespace.role if hasattr(interaction.namespace, 'role') else None
            with open("data.json", "r", encoding="utf-8") as f:
                data = json.load(f)
            if role:
                filtered = [item for item in data if item["角色"] == role]
            else:
                filtered = data
            results = [(item["角色"], item["掃描結果"]) for item in filtered if current in item["掃描結果"]]
            return [app_commands.Choice(name=f"[{role}] {text}", value=text) for role, text in results[:25]]

        @搜尋角色.autocomplete("role")
        async def 搜尋角色_autocomplete(interaction: discord.Interaction, current: str):
            results = [r for r in 角色選項 if current in r]
            return [app_commands.Choice(name=r, value=r) for r in results[:25]]

        client.run(BT)
    except Exception as e:
        user = client.get_user(user_discord_id)
        if user:
            user.send('>>> :x: 機器人異常終止'+ '\n' + str(e))
        logging.error(e)
        print("bot.py程式異常終止")
        print("錯誤訊息:" + str(e))
        sys.exit()