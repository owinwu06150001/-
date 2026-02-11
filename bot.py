import discord
from discord.ext import commands
from discord import app_commands
from deep_translator import GoogleTranslator
import os
from server import keep_alive 

# 啟動 Web Server 以便在 Render 上運行
keep_alive() 

TOKEN = os.environ.get("DISCORD_TOKEN")

# 權限設定
intents = discord.Intents.default()
intents.message_content = True 

bot = commands.Bot(command_prefix="!", intents=intents)

# --- 核心邏輯：取得說明文字 ---
def 取得使用說明(bot_user):
    return (
        f"  **多國語言翻譯機器人使用說明**\n\n"
        f"1️ **翻譯文字**：輸入 `/翻譯` 並輸入文字，點選選單即可。\n"
        f"2️ **查看說明**：輸入 `/使用方式` 或直接標註 {bot_user.mention}。\n"
        f"3️ **支援語言**：支援 繁體中文、英文、日文、韓文、法文、泰文等 20 種語言。"
    )

# --- 下拉選單類別 ---
class 語言選擇器(discord.ui.View):
    def __init__(self, 要翻譯的文字):
        super().__init__(timeout=180)
        self.要翻譯的文字 = 要翻譯的文字

        選項 = [
            discord.SelectOption(label="繁體中文", value="zh-TW", emoji="🇹🇼"),
            discord.SelectOption(label="English (英文)", value="en", emoji="🇺🇸"),
            discord.SelectOption(label="日本語 (日文)", value="ja", emoji="🇯🇵"),
            discord.SelectOption(label="한국어 (韓文)", value="ko", emoji="🇰🇷"),
            discord.SelectOption(label="Tiếng Việt (越南文)", value="vi", emoji="🇻🇳"),
            discord.SelectOption(label="ไทย (泰文)", value="th", emoji="🇹🇭"),
            discord.SelectOption(label="Français (法文)", value="fr", emoji="🇫🇷"),
            discord.SelectOption(label="Deutsch (德文)", value="de", emoji="🇩🇪"),
            discord.SelectOption(label="Español (西班牙文)", value="es", emoji="🇪🇸"),
            discord.SelectOption(label="Italiano (義大利文)", value="it", emoji="🇮🇹"),
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

        self.選單 = discord.ui.Select(
            placeholder="請選擇目標語言...",
            options=選項
        )
        self.選單.callback = self.選單回調
        self.add_item(self.選單)

    async def 選單回調(self, interaction: discord.Interaction):
        # 1. 延遲回應，預留翻譯時間（解決 10062 錯誤）
        await interaction.response.defer()
        目標語言 = self.選單.values[0]

        try:
            # 2. 執行翻譯
            結果 = GoogleTranslator(source="auto", target=目標語言).translate(self.要翻譯的文字)
            
            # 3. 強制校正邏輯：如果原文跟翻譯結果一模一樣，且目標不是中文，強制指定來源
            if 結果.strip() == self.要翻譯的文字.strip() and 目標語言 != "zh-TW":
                結果 = GoogleTranslator(source="zh-TW", target=目標語言).translate(self.要翻譯的文字)

            # 4. 輸出美觀結果
            embed = discord.Embed(title="翻譯完成", color=0x3498db)
            embed.add_field(name="原文內容", value=f"```{self.要翻譯的文字}```", inline=False)
            embed.add_field(name=f"翻譯結果 ({目標語言})", value=f"```{結果}```", inline=False)
            embed.set_footer(text=f"由 {interaction.user.display_name} 請求", icon_url=interaction.user.display_avatar.url)
            
            await interaction.followup.send(embed=embed)
        except Exception as e:
            await interaction.followup.send(f"❌ 翻譯時發生錯誤: {e}", ephemeral=True)

# --- 機器人事件 ---

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="/翻譯"))
    try:
        await bot.tree.sync()
        print(f"指令同步成功")
    except Exception as e:
        print(f"指令同步失敗: {e}")
    print(f"機器人已上線：{bot.user}")

@bot.event
async def on_message(message):
    if message.author == bot.user: return
    # 標註機器人時顯示說明
    if bot.user.mentioned_in(message) and not message.mention_everyone:
        await message.channel.send(取得使用說明(bot.user))
    await bot.process_commands(message)

# --- 斜線指令 ---

@bot.tree.command(name="使用方式", description="查看機器人操作說明")
async def help_command(interaction: discord.Interaction):
    # 加入延遲回應避免逾時
    await interaction.response.defer()
    await interaction.followup.send(取得使用說明(bot.user))

@bot.tree.command(name="翻譯", description="輸入文字並選擇語言進行翻譯")
@app_commands.describe(文字="請輸入想要翻譯的內容")
async def translate(interaction: discord.Interaction, 文字: str):
    view = 語言選擇器(文字)
    await interaction.response.send_message(
        f"**您輸入的內容：** {文字}\n請選擇要翻譯成的語言：", 
        view=view
    )

bot.run(TOKEN)
