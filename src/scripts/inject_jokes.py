import asyncio

import asyncpg
import httpx

from bot.models import Joke
from bot.settings import DbSettings


# https://github.com/taivop/joke-dataset/tree/master
async def iterate_jokes():
    urls = [
        "https://raw.githubusercontent.com/taivop/joke-dataset/master/reddit_jokes.json",
        "https://raw.githubusercontent.com/taivop/joke-dataset/master/stupidstuff.json",
        "https://raw.githubusercontent.com/taivop/joke-dataset/master/wocka.json",
    ]
    async with httpx.AsyncClient() as client:
        for url in urls:
            print(f"fetching {url}")
            res = await client.get(url, follow_redirects=True)
            jokes = res.json()
            for joke in jokes:
                # category, title, body
                vals = (
                    joke.get("category", "uncategorized"),
                    joke.get("title"),
                    joke.get("body"),
                )

                if len(vals[1] or "") + len(vals[2]) < 2000:
                    yield vals


async def copy_to_table():
    con = await asyncpg.connect(dsn=DbSettings(scheme="postgresql").dsn())
    result = await con.copy_records_to_table(
        Joke.__tablename__,
        columns=[Joke.category.name, Joke.title.name, Joke.body.name],
        records=iterate_jokes(),
    )


if __name__ == "__main__":
    asyncio.run(copy_to_table())
