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
            await asyncio.sleep(5)


    client.loop.create_task(task_example())
    client.run(token)