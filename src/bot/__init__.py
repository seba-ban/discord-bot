import logging

logging.basicConfig(level=logging.DEBUG)
from discord.ext.commands import Context

from . import commands
from .bot import bot
from .settings import BotSettings


@bot.command()
async def help(ctx: Context):
    lines = ["Available commands:"]
    tags_cmds = sorted(
        (cmd.extras.get("tag", "general"), cmd_name)
        for cmd_name, cmd in bot.all_commands.items()
    )
    last_tag = None
    for tag, cmd_name in sorted(
        (cmd.extras.get("tag", "general"), cmd_name)
        for cmd_name, cmd in bot.all_commands.items()
    ):
        if last_tag != tag:
            lines.append(f"**{tag}**")
            last_tag = tag
        lines.append(f'* `{cmd_name}`: {bot.all_commands[cmd_name].description or ""}')
    await ctx.send("\n".join(lines))


def start():
    settings = BotSettings()
    bot.run(settings.token)
