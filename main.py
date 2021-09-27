import webbrowser
from sys import exit
from os import mkdir
from os.path import isfile, isdir, join
# from gmail import send_mail
# from constants import *

GMAIL_API_QUICKSTART_URL = 'https://developers.google.com/gmail/api/quickstart/python'
SETTINGS_DIRECTORY = 'settings'
SECRETS_DIRECTORY = 'secrets'
GMAIL_TOKEN_FILE = join(SECRETS_DIRECTORY, 'gmail_token.json')
GMAIL_CREDENTIALS_FILE = join(SECRETS_DIRECTORY, 'credentials.json')
SENDER_ADDRESS_FILE = join(SETTINGS_DIRECTORY, '.sender_address')
# If modifying these scopes, delete the file token.json.
GMAIL_SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'
GMAIL_USER_ID = 'me'  # Special value used by Gmail API


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


if __name__ == '__main__':
    first_time_setup()
