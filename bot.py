import discord
from discord.ext import commands
from discord import app_commands
from deep_translator import GoogleTranslator
import os
from server import keep_alive

# 啟動保活 Web Server
keep_alive()

TOKEN = os.environ["DISCORD_TOKEN"]

# --- 修改這部分 ---
intents = discord.Intents.default()
intents.message_content = True  # 讓機器人能讀取訊息內容，消除日誌警告
# -----------------

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    # 同步斜線指令（Slash Commands）
    try:
        synced = await bot.tree.sync()
        print(f"✅ 已同步 {len(synced)} 個指令")
    except Exception as e:
        print(f"❌ 同步指令失敗: {e}")
    
    print(f"Logged in as {bot.user}")

@bot.tree.command(name="翻譯", description="翻譯文字")
@app_commands.describe(
    文字="要翻譯的內容",
    目標語言="語言代碼，例如 zh-TW、en、ja"
)
async def translate(
    interaction: discord.Interaction, 
    文字: str, 
    目標語言: str = "zh-TW"
):
    # 先發送「處理中」的回應，避免翻譯太久導致互動逾時 (3秒限制)
    await interaction.response.defer(ephemeral=False) 

    try:
        result = GoogleTranslator(
            source="auto", 
            target=目標語言
        ).translate(文字)

        await interaction.followup.send(
            f"🌐 **翻譯結果** ({目標語言})\n\n"
            f"**原文：** {文字}\n"
            f"**翻譯：** {result}"
        )

    except Exception as e:
        await interaction.followup.send(
            f"❌ 翻譯失敗：{e}", 
            ephemeral=True
        )

bot.run(TOKEN)
