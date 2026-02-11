import discord
from discord.ext import commands
from discord import app_commands
from deep_translator import GoogleTranslator
import os
from server import keep_alive 

keep_alive() 

TOKEN = os.environ.get("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True 

bot = commands.Bot(command_prefix="!", intents=intents)

def 取得使用說明(bot_user):
    return (
        f"  **多國語言翻譯機器人**\n\n"
        f"1️ **使用指令**：輸入 `/翻譯` 並輸入文字。\n"
        f"2️ **選擇語言**：從下拉選單選擇目標語言（支援 20 種）。\n"
        f"3️ **幫助說明**：輸入 `/使用方式` 或標註 {bot_user.mention}。"
    )

class 語言選擇器(discord.ui.View):
    def __init__(self, 要翻譯的文字):
        super().__init__(timeout=180)
        self.要翻譯的文字 = 要翻譯的文字

        # 擴充語言清單 (最多可放 25 個)
        選項 = [
            # 亞洲
            discord.SelectOption(label="繁體中文", value="zh-TW", emoji="🇹🇼"),
            discord.SelectOption(label="簡體中文", value="zh-CN", emoji="🇨🇳"),
            discord.SelectOption(label="English (英文)", value="en", emoji="🇺🇸"),
            discord.SelectOption(label="日本語 (日文)", value="ja", emoji="🇯🇵"),
            discord.SelectOption(label="한국어 (韓文)", value="ko", emoji="🇰🇷"),
            discord.SelectOption(label="Tiếng Việt (越南文)", value="vi", emoji="🇻🇳"),
            discord.SelectOption(label="ไทย (泰文)", value="th", emoji="🇹🇭"),
            discord.SelectOption(label="Bahasa Indonesia (印尼文)", value="id", emoji="🇮🇩"),
            # 歐洲
            discord.SelectOption(label="Français (法文)", value="fr", emoji="🇫🇷"),
            discord.SelectOption(label="Deutsch (德文)", value="de", emoji="🇩🇪"),
            discord.SelectOption(label="Español (西班牙文)", value="es", emoji="🇪🇸"),
            discord.SelectOption(label="Italiano (義大利文)", value="it", emoji="🇮🇹"),
            discord.SelectOption(label="Русский (俄文)", value="ru", emoji="🇷🇺"),
            discord.SelectOption(label="Português (葡萄牙文)", value="pt", emoji="🇵🇹"),
            discord.SelectOption(label="Nederlands (荷蘭文)", value="nl", emoji="🇳🇱"),
            # 其他
            discord.SelectOption(label="العربية (阿拉伯文)", value="ar", emoji="🇸🇦"),
            discord.SelectOption(label="Türkçe (土耳其文)", value="tr", emoji="🇹🇷"),
            discord.SelectOption(label="हिन्दी (印地文)", value="hi", emoji="🇮🇳"),
            discord.SelectOption(label="Tagalog (菲律賓文)", value="tl", emoji="🇵🇭"),
            discord.SelectOption(label="Polski (波蘭文)", value="pl", emoji="🇵🇱"),
        ]

        self.選單 = discord.ui.Select(
            placeholder="🎯 請選擇目標語言...",
            min_values=1,
            max_values=1,
            options=選項
        )
        self.選單.callback = self.選單回調函數
        self.add_item(self.選單)

    async def 選單回調函數(self, interaction: discord.Interaction):
        目標語言 = self.選單.values[0]
        await interaction.response.defer()

        try:
            結果 = GoogleTranslator(source="auto", target=目標語言).translate(self.要翻譯的文字)
            
            embed = discord.Embed(title="✨ 翻譯完成", color=0x3498db)
            embed.add_field(name=" 原文", value=f"```{self.要翻譯的文字}```", inline=False)
            embed.add_field(name=f"翻譯結果 ({目標語言})", value=f"```{結果}```", inline=False)
            embed.set_footer(text=f"由 {interaction.user.display_name} 請求", icon_url=interaction.user.display_avatar.url)
            
            await interaction.followup.send(embed=embed)
        except Exception as e:
            await interaction.followup.send(f"❌ 翻譯出錯: {e}", ephemeral=True)

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="/翻譯"))
    try:
        await bot.tree.sync()
        print(f"已同步指令")
    except Exception as e:
        print(f"同步失敗: {e}")
    print(f"機器人已準備就緒：{bot.user}")

@bot.event
async def on_message(message):
    if message.author == bot.user: return
    if bot.user.mentioned_in(message) and not message.mention_everyone:
        await message.channel.send(取得使用說明(bot.user))
    await bot.process_commands(message)

@bot.tree.command(name="使用方式", description="查看機器人的操作說明")
async def help_command(interaction: discord.Interaction):
    await interaction.response.send_message(取得使用說明(bot.user))

@bot.tree.command(name="翻譯", description="輸入文字並透過選單選擇目標語言")
@app_commands.describe(文字="請輸入想要翻譯的內容")
async def translate(interaction: discord.Interaction, 文字: str):
    view = 語言選擇器(文字)
    await interaction.response.send_message(
        f"**您輸入的內容：** {文字}\n請選擇要翻譯成的語言：", 
        view=view
    )

bot.run(TOKEN)
