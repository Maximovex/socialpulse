import requests
import asyncio
import aiohttp
import time

from aiohttp import ClientSession


def top_ids(quant: int = 10) -> list[int]:
    stories = requests.get(
        "https://hacker-news.firebaseio.com/v0/topstories.json"
    ).json()[:quant]
    return stories


def get_story(story_id: int) -> dict:
    url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
    return requests.get(url).json()


async def get_story_async(session: ClientSession, story_id: int) -> dict:
    url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
    async with session.get(url) as response:
        return await response.json()


async def fetch_stories(list_stories: list) -> list[dict]:
    async with aiohttp.ClientSession() as session:
        stories = [get_story_async(session, story_id) for story_id in list_stories]
        return await asyncio.gather(*stories)


async def main():
    ids = top_ids(50)
    start = time.time()
    stories = await fetch_stories(ids)
    print(f"50 stories async: {time.time() - start:.2f}s")


if __name__ == "__main__":
    asyncio.run(main())
    # top_stories=fetch_stories(top_ids(10))
# new=[(story.get("title"),story.get("score")) for story in top_stories]
# print(*new,sep="\n")
