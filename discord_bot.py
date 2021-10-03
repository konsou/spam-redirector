import asyncio

import discord
from discord.ext import tasks

from settings import *

if __name__ == '__main__':
    with open(DISCORD_TOKEN_FILE) as f:
        token = f.read().strip()

    client = discord.Client()

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
