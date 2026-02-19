import discord
from discord.ext import commands
from discord import app_commands
from deep_translator import GoogleTranslator
import os
from server import keep_alive 
import aiohttp

# 啟動 Web Server
keep_alive()

TOKEN = os.environ.get("DISCORD_TOKEN")
OCR_API_KEY = os.environ.get("OCR_API_KEY")

# 權限設定
intents = discord.Intents.default()
intents.message_content = True 

# ⭐⭐⭐ 先建立 bot ⭐⭐⭐
bot = commands.Bot(command_prefix="!", intents=intents)

# -------------------------
# 下面才開始放指令
# -------------------------

@bot.tree.command(name="圖片翻譯", description="上傳圖片並翻譯圖片中的文字")
@app_commands.describe(圖片="請上傳要翻譯的圖片")
async def image_translate(interaction: discord.Interaction, 圖片: discord.Attachment):

    await interaction.response.defer()

    if not OCR_API_KEY:
        await interaction.followup.send("❌ 找不到 OCR_API_KEY，請在 Render 設定環境變數", ephemeral=True)
        return

    try:
        async with aiohttp.ClientSession() as session:
            payload = {
                'apikey': OCR_API_KEY,
                'url': 圖片.url,
                'language': 'cht',
            }

            async with session.post('https://api.ocr.space/parse/image', data=payload) as resp:
                result = await resp.json()

        if result.get("IsErroredOnProcessing"):
            await interaction.followup.send("❌ OCR 辨識失敗")
            return

        text = result["ParsedResults"][0]["ParsedText"]

        if not text.strip():
            await interaction.followup.send("❌ 圖片中沒有辨識到文字")
            return

        view = 語言選擇器(text)

        await interaction.followup.send(
            f"📷 **辨識到的文字：**\n```{text[:1000]}```\n請選擇翻譯語言：",
            view=view
        )

    except Exception as e:
        await interaction.followup.send(f"❌ 發生錯誤: {e}")

# -------------------------
# 下面是你的其他程式
# -------------------------
