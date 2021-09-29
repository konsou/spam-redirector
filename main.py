import webbrowser
import json
import re
from base64 import urlsafe_b64decode
from sys import exit
from os import mkdir
from os.path import isfile, isdir, join
# from gmail import send_mail
# from constants import *

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

from bs4 import BeautifulSoup

GMAIL_API_QUICKSTART_URL = 'https://developers.google.com/gmail/api/quickstart/python'
SETTINGS_DIRECTORY = 'settings'
SECRETS_DIRECTORY = 'secrets'
GMAIL_TOKEN_FILE = join(SECRETS_DIRECTORY, 'gmail_token.json')
GMAIL_CREDENTIALS_FILE = join(SECRETS_DIRECTORY, 'credentials.json')
SENDER_ADDRESS_FILE = join(SETTINGS_DIRECTORY, '.sender_address')
# If modifying these scopes, delete the file token.json.
GMAIL_SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'
GMAIL_USER_ID = 'me'  # Special value used by Gmail API

STRINGS_TO_FILTER_OUT = ['tomi', 'javanainen', 'konso']


def first_time_setup() -> None:
    """ First-time setup for Gmail API """

    for dir_ in (SETTINGS_DIRECTORY, SECRETS_DIRECTORY):
        if not isdir(dir_):
            print(f"No directory {dir_} present - creating...")
            try:
                mkdir(dir_)
            except OSError as e:
                print(f"FAILURE: Couldn't create directory. Probably need to run this script with sudo.")
                exit(1)

    while not isfile(GMAIL_CREDENTIALS_FILE):
        print(f"Credentials file {GMAIL_CREDENTIALS_FILE} not found")
        print("Opening Gmail API Python Quickstart...")
        print(GMAIL_API_QUICKSTART_URL)
        print("Please click on \"ENABLE THE GMAIL API\" and then download credentials.json by clicking "
              "\"DOWNLOAD CLIENT CONFIGURATION\"")
        print(f"Save the file as {GMAIL_CREDENTIALS_FILE}")
        webbrowser.open(GMAIL_API_QUICKSTART_URL)
        input("Press ENTER when ready...")

    print(f"Credentials file {GMAIL_CREDENTIALS_FILE} found!")

    print(f"On the first time you need to complete Oauth authentication and possibly restart this script")
    print(f"Setup script finished.")


def authenticate():
    """Returns a service instance"""
    credentials = None
    if isfile(GMAIL_TOKEN_FILE):
        credentials = Credentials.from_authorized_user_file(GMAIL_TOKEN_FILE, GMAIL_SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                GMAIL_CREDENTIALS_FILE, GMAIL_SCOPES)
            credentials = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(GMAIL_TOKEN_FILE, 'w') as token:
            token.write(credentials.to_json())

    service = build('gmail', 'v1', credentials=credentials)
    return service


def get_labels(service):
    # Call the Gmail API
    results = service.users().labels().list(userId='me').execute()
    labels = results.get('labels', [])

    if not labels:
        print('No labels found.')
    else:
        print('Labels:')
        for label in labels:
            print(label['name'])


def list_messages_with_labels(service, label_ids, user_id='me', ):
    """
    List all Messages of the user's mailbox with label_ids applied.

    Args:
        user_id: User's email address. The special value "me"
            can be used to indicate the authenticated user.
        label_ids: Only return Messages with these labelIds applied.

    Returns:
        List of Messages that have all required Labels applied. Note that the
        returned list contains Message IDs, you must use get with the
        appropriate id to get the details of a Message.
    """
    response = service.users().messages().list(userId=user_id,
                                               labelIds=label_ids).execute()
    messages = []
    if 'messages' in response:
        messages.extend(response['messages'])

    while 'nextPageToken' in response:
        page_token = response['nextPageToken']
        response = service.users().messages().list(userId=user_id,
                                                   labelIds=label_ids,
                                                   pageToken=page_token).execute()
    messages.extend(response['messages'])

    return messages


def get_message(service, message_id):
    return service.users().messages().get(userId='me', id=message_id, format='full').execute()


if __name__ == '__main__':
    # service = authenticate()
    # get_labels(service)
    # spam_messages = list_messages_with_labels(service=service,
    #                                           label_ids=['SPAM'])
    #
    # messages = []
    # for message in spam_messages[:10]:
    #     message = get_message(service=service, message_id=message['id'])
    #     print(f'Write message {message["id"]}')
    #     messages.append(message)
    #
    # with open('messages_dump_full.json', 'w', encoding='utf-8') as f:
    #     json.dump(messages, f)

    with open('messages_dump_full.json', encoding='utf-8') as f:
        messages = json.load(f)

    message = messages[0]
    for header in message['payload']['headers']:
        if header['name'] == 'Subject':
            print(header['value'])

    message_html = urlsafe_b64decode(message['payload']['parts'][0]['body']['data'])
    soup = BeautifulSoup(message_html, "html.parser")
    message_text = soup.get_text()

    message_text = re.sub(r'\n\s*\n', '\n\n', message_text)
    for string_to_filter in STRINGS_TO_FILTER_OUT:
        message_text = re.sub(string_to_filter, '', message_text, flags=re.IGNORECASE)
    print(message_text)

    #print(urlsafe_b64decode(messages[0]['raw']))
