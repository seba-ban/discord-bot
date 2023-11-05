import re

from discord.ext.commands import Context

from ..bot import bot

extras = {"tag": "links"}

url_regex = re.compile(
    r"https?:\/\/(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&\/=]*)"
)

MESSAGES_TO_SEARCH = 1000


@bot.command(
    description=f"get a list of all links from the past {MESSAGES_TO_SEARCH} messages in a DM",
    extras=extras,
)
async def links(ctx: Context, *filters: str):
    links = set()
    oldest, newest = None, None
    async for msg in ctx.channel.history(limit=MESSAGES_TO_SEARCH, oldest_first=True):
        for match in re.finditer(url_regex, msg.content):
            link = match.group()
            if link in links or (
                filters and not any(filter in link for filter in filters)
            ):
                continue

            if oldest is None or msg.created_at < oldest:
                oldest = msg.created_at
            if newest is None or msg.created_at > newest:
                newest = msg.created_at

            links.add(link)

    channel_name = ctx.channel.id
    if not links:
        await ctx.author.send(f"No links found in channel {channel_name}.")
    else:
        await ctx.author.send(
            f"Links from messages from {oldest} to {newest} from channel {channel_name}.\n\n"
            + "\n".join(sorted(links))
        )
