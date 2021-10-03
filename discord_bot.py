import asyncio
import json

import discord
from discord.ext import tasks

import gmail
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
    gmail_handler = gmail.GmailHandler()

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

    async def email_task():
        while True:
            print(f'Running task')
            print(f'Fetch emails')
            fetched_message_ids = [message['id'] for message in gmail_handler.list_messages_with_labels(['SPAM'])]
            for message_id in fetched_message_ids:
                if message_id in sent_ids:
                    print(f'{message_id} already sent, skipping')
                    continue

                mail_text = gmail_handler.fetch_mail_and_format(message_id=message_id,
                                                                strings_to_filter_out=STRINGS_TO_FILTER_OUT)
                for channel_id in CHANNELS_TO_SPAM_TO:
                    channel = client.get_channel(channel_id)
                    if channel is not None:
                        print(f'Sending message {message_id} to channel {channel}...')
                        await channel.send(mail_text[:1999])
                        sent_ids[message_id] = 1

                save_sent_ids(sent_ids)

            await asyncio.sleep(TASK_RUN_TIME_INTERVAL_SECONDS)


    client.loop.create_task(email_task())
    client.run(token)
