import discord
from discord.ext import commands
from discord import app_commands
from deep_translator import GoogleTranslator
import os
from server import keep_alive

# 啟動保活 Web Server
keep_alive()

TOKEN = os.environ["DISCORD_TOKEN"]

# 完整權限設定
intents = discord.Intents.default()
intents.message_content = True 
intents.presences = True  
intents.members = True    

bot = commands.Bot(command_prefix="!", intents=intents)

# 定義使用說明文字
USAGE_TEXT = (
    "🌐 **翻譯機器人使用說明**\n\n"
    "1️⃣ **斜線指令**：輸入 `/翻譯` 並填入文字與目標語言代碼。\n"
    "2️⃣ **常用語言代碼表**：\n"
    "   - `zh-TW`: 繁體中文 | `zh-CN`: 簡體中文\n"
    "   - `en`: 英文 | `ja`: 日文 | `ko`: 韓文\n"
    "   - `fr`: 法文 | `de`: 德文 | `es`: 西班牙文\n"
    "   - `it`: 義大利文 | `ru`: 俄文 | `th`: 泰文\n"
    "   - `vi`: 越南文 | `pt`: 葡萄牙文\n"
    "3️⃣ **直接標註**：在頻道中 `@機器人` 即可查看此說明。"
)

@bot.event
async def on_ready():
    # 設定機器人狀態：正在收聽 /使用方式
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="/使用方式"))
    
    # 同步斜線指令
    try:
        synced = await bot.tree.sync()
        print(f"✅ 已同步 {len(synced)} 個指令")
    except Exception as e:
        print(f"❌ 同步指令失敗: {e}")
    
    print(f"Logged in as {bot.user}")

# 當機器人被標註時回應
@bot.event
async def on_message(message):
    # 排除機器人自己的訊息，並檢查是否被標註
    if bot.user.mentioned_in(message) and not message.mention_everyone:
        await message.channel.send(f"你好 {message.author.mention}！\n{USAGE_TEXT}")
    
    # 確保其他指令正常運作
    await bot.process_commands(message)

# 使用方式指令 (加上 defer 解決 10062 錯誤)
@bot.tree.command(name="使用方式", description="查看機器人操作說明與完整語言代碼")
async def help_command(interaction: discord.Interaction):
    try:
        # 第一時間回應 Discord 避免 3 秒超時
        await interaction.response.defer(ephemeral=False) 
        # 發送說明文字
        await interaction.followup.send(USAGE_TEXT)
    except Exception as e:
        print(f"指令執行出錯: {e}")

# 翻譯指令 (加上 defer 並保持原輸出台詞)
@bot.tree.command(name="翻譯", description="翻譯文字")
@app_commands.describe(
    文字="要翻譯的內容",
    目標語言="語言代碼 @機器人後會提供"
)
async def translate(
    interaction: discord.Interaction, 
    文字: str, 
    目標語言: str = "zh-TW"
):
    try:
        # 第一時間回應 Discord 避免 3 秒超時
        await interaction.response.defer(ephemeral=False) 
    except:
        return

    try:
        # 執行翻譯邏輯
        result = GoogleTranslator(
            source="auto", 
            target=目標語言
        ).translate(文字)

        # 保持原本要求的輸出格式
        await interaction.followup.send(
            f"**翻譯結果** ({目標語言})\n\n"
            f"**原文：** {文字}\n"
            f"**翻譯：** {result}"
        )
    except Exception as e:
        await interaction.followup.send(f"翻譯失敗：{e}", ephemeral=True)

bot.run(TOKEN)
