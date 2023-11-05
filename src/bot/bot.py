import discord
from discord.ext import commands

intents = discord.Intents.none()
intents.message_content = True
intents.messages = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)
