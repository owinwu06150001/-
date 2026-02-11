import discord
from discord.ext import commands
from discord import app_commands
from deep_translator import GoogleTranslator
import os
# from server import keep_alive # 記得啟用您的保活機制

# keep_alive() 

TOKEN = os.environ.get("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True 

bot = commands.Bot(command_prefix="!", intents=intents)

# 1. 定義選單的介面 (View)
class LanguageSelect(discord.ui.View):
    def __init__(self, text_to_translate):
        super().__init__(timeout=180) # 選單 3 分鐘後失效
        self.text_to_translate = text_to_translate

        # 定義選單選項
        options = [
            discord.SelectOption(label="繁體中文", description="Translate to Traditional Chinese", value="zh-TW", emoji="🇹🇼"),
            discord.SelectOption(label="English", description="翻譯成英文", value="en", emoji="🇺🇸"),
            discord.SelectOption(label="日本語", description="Translate to Japanese", value="ja", emoji="🇯🇵"),
            discord.SelectOption(label="한국어", description="Translate to Korean", value="ko", emoji="🇰🇷"),
            discord.SelectOption(label="Español", description="Translate to Spanish", value="es", emoji="🇪🇸"),
        ]

        # 建立下拉選單元件
        self.select = discord.ui.Select(
            placeholder="請選擇目標語言...",
            min_values=1,
            max_values=1,
            options=options
        )
        # 綁定選單事件
        self.select.callback = self.select_callback
        self.add_item(self.select)

    async def select_callback(self, interaction: discord.Interaction):
        # 使用者選擇語言後執行的邏輯
        target_lang = self.select.values[0]
        
        # 顯示正在翻譯
        await interaction.response.defer()

        try:
            result = GoogleTranslator(source="auto", target=target_lang).translate(self.text_to_translate)
            
            # 更新訊息內容
            await interaction.followup.send(
                f"**翻譯完成** ({target_lang})\n\n"
                f"**原文：** {self.text_to_translate}\n"
                f"**翻譯：** {result}"
            )
        except Exception as e:
            await interaction.followup.send(f"翻譯出錯: {e}", ephemeral=True)

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="/translate"))
    try:
        synced = await bot.tree.sync()
        print(f"已同步 {len(synced)} 個指令")
    except Exception as e:
        print(f"同步指令失敗: {e}")
    print(f"Logged in as {bot.user}")

# 2. 修改斜線指令
@bot.tree.command(name="translate", description="輸入文字並選擇語言進行翻譯")
@app_commands.describe(文字="要翻譯的內容")
async def translate(interaction: discord.Interaction, 文字: str):
    # 發送帶有下拉選單的訊息
    view = LanguageSelect(文字)
    await interaction.response.send_message(
        f"請選擇 **'{文字}'** 的目標語言：", 
        view=view
    )

bot.run(TOKEN)
