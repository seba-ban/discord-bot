from discord.ext.commands import Context
from sqlalchemy import delete as delete_q
from sqlalchemy import select

from bot.db import session_factory
from bot.logger import logger
from bot.models import UserSavedMessage

from ..bot import bot

extras = {"tag": "save-for-later"}


async def list_data(user_id: int, channel_id: int):
    async with session_factory() as session:
        query = (
            select(UserSavedMessage)
            .where(UserSavedMessage.user_id == user_id)
            .where(UserSavedMessage.channel_id == channel_id)
            .order_by(UserSavedMessage.created_at.desc())
        )
        res = await session.execute(query)
        return res.scalars().all()


async def save_data(user_id: int, channel_id: int, data: str):
    async with session_factory() as session:
        msg = UserSavedMessage(
            id=None, created_at=None, channel_id=channel_id, user_id=user_id, data=data
        )
        session.add(msg)
        await session.commit()
        return msg


async def delete_data(user_id: int, channel_id: int, data_id: int):
    async with session_factory() as session:
        query = (
            delete_q(UserSavedMessage)
            .where(UserSavedMessage.id == data_id)
            .where(UserSavedMessage.user_id == user_id)
            .where(UserSavedMessage.channel_id == channel_id)
        )
        await session.execute(query)
        await session.commit()


@bot.command(description="save a string", extras=extras)
async def save(ctx: Context, *, arg: str):
    data = await save_data(ctx.author.id, ctx.channel.id, arg)
    await ctx.send(data.pretty())


@bot.command(description="list saved strings", extras=extras)
async def saved(ctx: Context):
    res = "\n".join(
        msg.pretty() for msg in await list_data(ctx.author.id, ctx.channel.id)
    )
    await ctx.send(res or "nothing here")


@bot.command(description="delete saved string by id", extras=extras)
async def delete(ctx: Context, msg_id: str):
    try:
        msg_id = int(msg_id)
    except ValueError:
        await ctx.send("invalid id")
        return

    try:
        await delete_data(ctx.author.id, ctx.channel.id, msg_id)
    except Exception as err:
        logger.error("delete failed", exc_info=err)
        await ctx.send("delete failed")
        return
