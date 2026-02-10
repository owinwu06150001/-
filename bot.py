import discord
from discord.ext import commands
from discord import app_commands
from deep_translator import GoogleTranslator
import os

TOKEN = os.environ["DISCORD_TOKEN"]

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    await bot.tree.sync()
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
    try:
        result = GoogleTranslator(
            source="auto",
            target=目標語言
        ).translate(文字)

        await interaction.response.send_message(
            f"🌐 **翻譯結果**\n\n"
            f"**原文：** {文字}\n"
            f"**翻譯：** {result}"
        )

    except Exception as e:
        await interaction.response.send_message(
            f"翻譯失敗：{e}",
            ephemeral=True
        )

bot.run(TOKEN)
