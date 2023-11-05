from random import randint

from discord.ext.commands import Context
from sqlalchemy import func, select

from bot.db import session_factory
from bot.logger import logger
from bot.models import Joke

from ..bot import bot

extras = {"tag": "jokes"}


@bot.command(description="get a random joke", extras=extras)
async def joke(ctx: Context):
    """Get a random joke from the database."""
    async with session_factory() as session:
        rank_cte = select(
            Joke.id, func.rank().over(order_by=Joke.id).label("rank")
        ).cte("joke_rank")
        count_cte = (
            select(func.count()).select_from(Joke).cte("joke_count", nesting=True)
        )
        random_cte = select(
            func.floor(func.random() * (count_cte.c.count - 1 + 1) + 1).label("random")
        ).cte("joke_random", nesting=True)

        query = (
            select(Joke)
            .select_from(Joke)
            .join(rank_cte, rank_cte.c.id == Joke.id)
            .where(rank_cte.c.rank == random_cte.c.random)
        )
        joke = (await session.execute(query)).scalar_one()
        await ctx.send(str(joke))
