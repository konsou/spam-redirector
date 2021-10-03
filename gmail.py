import webbrowser
import re
from base64 import urlsafe_b64decode
from sys import exit
from os import mkdir
from os.path import isfile, isdir

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

from bs4 import BeautifulSoup

from settings import *


class GmailHandler:
    def __init__(self):
        print(f'Init GmailHandler')
        self.service = self.authenticate()

    @staticmethod
    def first_time_setup() -> None:
        """ First-time setup for Gmail API """

        if not isdir(SECRETS_DIRECTORY):
            print(f"No directory {SECRETS_DIRECTORY} present - creating...")
            try:
                mkdir(SECRETS_DIRECTORY)
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

    @staticmethod
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

    def get_labels(self) -> list[str]:
        # Call the Gmail API
        results = self.service.users().labels().list(userId='me').execute()
        labels = results.get('labels', [])

        if not labels:
            print('No labels found.')
        else:
            print('Labels:')
            for label in labels:
                print(label['name'])
        return labels

    def list_messages_with_labels(self, label_ids, user_id='me', ):
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
        response = self.service.users().messages().list(userId=user_id,
                                                   labelIds=label_ids).execute()
        messages = []
        if 'messages' in response:
            messages.extend(response['messages'])

        while 'nextPageToken' in response:
            page_token = response['nextPageToken']
            response = self.service.users().messages().list(userId=user_id,
                                                       labelIds=label_ids,
                                                       pageToken=page_token).execute()
        messages.extend(response['messages'])

        return messages

    def get_message(self, message_id):
        return self.service.users().messages().get(userId='me', id=message_id, format='full').execute()

    @staticmethod
    def extract_message_body_text(message, format='full') -> str:
        message_body = None
        try:
            message_body = urlsafe_b64decode(message['payload']['parts'][0]['body']['data']).decode(encoding='utf-8')
        except KeyError:
            # Expected if not a multipart message
            print(f'Not multipart message. Trying next parsing method...')
            pass

        if message_body is None:
            try:
                message_body = urlsafe_b64decode(message['payload']['body']['data']).decode(encoding='utf-8')
            except KeyError as e:
                print(f'Unexpected email message format. KeyError: {e}')
                print(f'Using snippet as fallback.')
                print(message)
                return message['snippet']

        # Body is usually in HTML format - extract text
        soup = BeautifulSoup(message_body, "html.parser")
        message_text = soup.get_text()

        # Remove excessive linebreaks
        message_text = re.sub(r'\n\s*\n', '\n\n', message_text)

        return message_text

    @staticmethod
    def extract_message_subject(message) -> str:
        try:
            for header in message['payload']['headers']:
                if header['name'] == 'Subject':
                    return header['value']
        except KeyError as e:
            print(f'Error extracting message subject')
            print(e)
            return ''
        return ''

    @staticmethod
    def censor_string(string: str, pattern: str, replacement='name') -> str:
        return re.sub(pattern, replacement, string, flags=re.IGNORECASE)

    def fetch_mail_and_format(self, message_id: int, strings_to_filter_out: list[str]) -> str:
        """Return a nicely formatted email - subject at the top, then the body text.
        Filter out some strings if needed."""
        message = self.get_message(message_id)
        message_parsed = f'*{self.extract_message_subject(message)}*\n\n{self.extract_message_body_text(message)}'

        pattern_string = "|".join(strings_to_filter_out)
        message_parsed = self.censor_string(message_parsed, pattern=pattern_string)
        return message_parsed


