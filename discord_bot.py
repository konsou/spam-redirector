import asyncio
import json

import discord
from discord.ext import tasks

from settings import *


SentIds = dict[int: int]


def save_sent_ids(ids: SentIds) -> None:
    print('Saving sent id\'s to disk...')
    with open(SENT_IDS_FILE, 'w', encoding='utf-8') as f:
        json.dump(ids, f)


def load_sent_ids() -> SentIds:
    print('Loading sent id\'s from disk...')
    with open(SENT_IDS_FILE, encoding='utf-8') as f:
        return json.load(f)


if __name__ == '__main__':
    with open(DISCORD_TOKEN_FILE) as f:
        token = f.read().strip()

    client = discord.Client()

    sent_ids: SentIds
    try:
        sent_ids = load_sent_ids()
    except (FileNotFoundError, json.JSONDecodeError):
        print(f'Creating new empty sent id\'s file...')
        sent_ids = dict()
        save_sent_ids(sent_ids)

    @client.event
    async def on_ready():
        print('We have logged in as {0.user}'.format(client))


    @client.event
    async def on_message(message):
        if message.author == client.user:
            return

        if message.content.startswith('$hello'):
            await message.channel.send('Hello!')

    async def task_example():
        while True:
            print(f'Running task')
            for channel_id in CHANNELS_TO_SPAM_TO:
                channel = client.get_channel(channel_id)
                print(channel)
                if channel is not None:
                    await channel.send("Running task")
            await asyncio.sleep(TASK_RUN_TIME_INTERVAL_SECONDS)


    client.loop.create_task(task_example())
    client.run(token)
