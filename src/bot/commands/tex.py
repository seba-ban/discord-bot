from io import BytesIO

import discord
import matplotlib
import matplotlib.pyplot as plt
from discord.ext.commands import Context

from bot.logger import logger

from ..bot import bot

extras = {"tag": "latex"}


def latex_to_png(latex_equation, dpi=300, fontsize=12) -> BytesIO:
    fig, _ = plt.subplots(figsize=(2, 1))
    matplotlib.rc("text", usetex=True)
    plt.text(
        0.5, 0.5, f"${latex_equation}$", fontsize=fontsize, ha="center", va="center"
    )
    plt.axis("off")
    buffer = BytesIO()
    plt.savefig(buffer, format="png", dpi=dpi, bbox_inches="tight", pad_inches=0.1)
    buffer.seek(0)
    plt.close(fig)
    return buffer


@bot.command(description="generates equation from a latex string", extras=extras)
async def tex(ctx: Context, *, arg: str):
    try:
        file = discord.File(latex_to_png(arg), filename="tex.png")
    except Exception as err:
        logger.error("converting to latex failed", exc_info=err, extra={"input": latex})
        await ctx.send(f"invalid latex string: {arg}")
        return
    await ctx.channel.send(file=file)
