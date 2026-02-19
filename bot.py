import discord
from discord.ext import commands
from discord import app_commands
from deep_translator import GoogleTranslator
import os
from server import keep_alive
import aiohttp

# ----------------------------
# 啟動 Web Server（Render 用）
# ----------------------------
keep_alive()

TOKEN = os.environ.get("DISCORD_TOKEN")
OCR_API_KEY = os.environ.get("OCR_API_KEY")

if not TOKEN:
    raise ValueError("❌ 找不到 DISCORD_TOKEN，請在 Render 設定環境變數")

# ----------------------------
# 權限設定
# ----------------------------
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ----------------------------
# 使用說明
# ----------------------------
def 取得使用說明(bot_user):
    return (
        f"  **多國語言翻譯機器人使用說明**\n\n"
        f"1️ **翻譯文字**：輸入 `/翻譯` 並輸入文字，點選選單即可。\n"
        f"2️ **圖片翻譯**：輸入 `/圖片翻譯` 並上傳圖片。\n"
        f"3️ **查看說明**：輸入 `/使用方式` 或直接標註 {bot_user.mention}。\n"
        f"4️ **支援語言**：支援 繁體中文、英文、日文、韓文、法文、泰文等 20 種語言。"
    )

# ----------------------------
# 語言選單
# ----------------------------
class 語言選擇器(discord.ui.View):
    def __init__(self, 要翻譯的文字):
        super().__init__(timeout=180)
        self.要翻譯的文字 = 要翻譯的文字

        選項 = [
            discord.SelectOption(label="繁體中文", value="zh-TW", emoji="🇹🇼"),
            discord.SelectOption(label="English (英文)", value="en", emoji="🇺🇸"),
            discord.SelectOption(label="日本語 (日文)", value="ja", emoji="🇯🇵"),
            discord.SelectOption(label="한국어 (韓文)", value="ko", emoji="🇰🇷"),
            discord.SelectOption(label="Français (法文)", value="fr", emoji="🇫🇷"),
            discord.SelectOption(label="Deutsch (德文)", value="de", emoji="🇩🇪"),
            discord.SelectOption(label="Español (西班牙文)", value="es", emoji="🇪🇸"),
            discord.SelectOption(label="ไทย (泰文)", value="th", emoji="🇹🇭"),
            discord.SelectOption(label="Tiếng Việt (越南文)", value="vi", emoji="🇻🇳"),
            discord.SelectOption(label="Русский (俄文)", value="ru", emoji="🇷🇺"),
            discord.SelectOption(label="Português (葡萄牙文)", value="pt", emoji="🇵🇹"),
            discord.SelectOption(label="Nederlands (荷蘭文)", value="nl", emoji="🇳🇱"),
            discord.SelectOption(label="العربية (阿拉伯文)", value="ar", emoji="🇸🇦"),
            discord.SelectOption(label="Türkçe (土耳其文)", value="tr", emoji="🇹🇷"),
            discord.SelectOption(label="हिन्दी (印地文)", value="hi", emoji="🇮🇳"),
            discord.SelectOption(label="Tagalog (菲律賓文)", value="tl", emoji="🇵🇭"),
            discord.SelectOption(label="Polski (波蘭文)", value="pl", emoji="🇵🇱"),
            discord.SelectOption(label="Bahasa Indonesia (印尼文)", value="id", emoji="🇮🇩"),
            discord.SelectOption(label="zh-CN (簡體中文)", value="zh-CN", emoji="🇨🇳"),
        ]

        self.select = discord.ui.Select(
            placeholder="請選擇目標語言...",
            options=選項
        )
        self.select.callback = self.選單回調
        self.add_item(self.select)

    async def 選單回調(self, interaction: discord.Interaction):
        await interaction.response.defer()
        目標語言 = self.select.values[0]

        try:
            結果 = GoogleTranslator(source="auto", target=目標語言).translate(self.要翻譯的文字)

            if 結果.strip() == self.要翻譯的文字.strip() and 目標語言 != "zh-TW":
                結果 = GoogleTranslator(source="zh-TW", target=目標語言).translate(self.要翻譯的文字)

            embed = discord.Embed(title="翻譯完成", color=0x3498db)
            embed.add_field(name="原文內容", value=f"```{self.要翻譯的文字[:1000]}```", inline=False)
            embed.add_field(name=f"翻譯結果 ({目標語言})", value=f"```{結果[:1000]}```", inline=False)
            embed.set_footer(text=f"由 {interaction.user.display_name} 請求")

            await interaction.followup.send(embed=embed)

        except Exception as e:
            await interaction.followup.send(f"❌ 翻譯時發生錯誤: {e}", ephemeral=True)

# ----------------------------
# 事件
# ----------------------------
@bot.event
async def on_ready():
    await bot.change_presence(
        activity=discord.Activity(type=discord.ActivityType.listening, name="/翻譯")
    )
    await bot.tree.sync()
    print(f"✅ 機器人已上線：{bot.user}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if bot.user.mentioned_in(message) and not message.mention_everyone:
        await message.channel.send(取得使用說明(bot.user))
    await bot.process_commands(message)

# ----------------------------
# 斜線指令
# ----------------------------
@bot.tree.command(name="使用方式", description="查看機器人操作說明")
async def help_command(interaction: discord.Interaction):
    await interaction.response.send_message(取得使用說明(bot.user))

@bot.tree.command(name="翻譯", description="輸入文字並選擇語言進行翻譯")
@app_commands.describe(文字="請輸入想要翻譯的內容")
async def translate(interaction: discord.Interaction, 文字: str):
    view = 語言選擇器(文字)
    await interaction.response.send_message(
        f"**您輸入的內容：** {文字}\n請選擇要翻譯成的語言：",
        view=view
    )

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
                "apikey": OCR_API_KEY,
                "url": 圖片.url,
                "language": "cht"
            }

            async with session.post("https://api.ocr.space/parse/image", data=payload) as resp:
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

# ----------------------------
# 啟動
# ----------------------------
bot.run(TOKEN)
