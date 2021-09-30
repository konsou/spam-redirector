from os.path import join


GMAIL_API_QUICKSTART_URL = 'https://developers.google.com/gmail/api/quickstart/python'
SECRETS_DIRECTORY = 'secrets'
GMAIL_TOKEN_FILE = join(SECRETS_DIRECTORY, 'gmail_token.json')
GMAIL_CREDENTIALS_FILE = join(SECRETS_DIRECTORY, 'credentials.json')

# If modifying these scopes, delete the file token.json.
GMAIL_SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
GMAIL_USER_ID = 'me'  # Special value used by Gmail API

DISCORD_TOKEN_FILE = join(SECRETS_DIRECTORY, 'discord_bot_token')

STRINGS_TO_FILTER_OUT = 'tomi|javanainen|konso'
