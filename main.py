import json
import re

from bs4 import BeautifulSoup

import gmail
from settings import *




if __name__ == '__main__':
    service = gmail.authenticate()
    spam_messages = gmail.list_messages_with_labels(service=service,
                                                    label_ids=['SPAM'])
    #
    # messages = []
    for message in spam_messages[:10]:
        message = gmail.get_message(service=service, message_id=message['id'])
        message_parsed = f'*{gmail.extract_message_subject(message)}*\n\n{gmail.extract_message_body_text(message)}'
        message_parsed = censor_string(message_parsed, STRINGS_TO_FILTER_OUT)
        print(
            f'{message_parsed}\n\n-------------------------------------------------------------------------------------------\n\n')

    #
    # with open('messages_dump_full.json', 'w', encoding='utf-8') as f:
    #     json.dump(messages, f)

    # with open('messages_dump_full.json', encoding='utf-8') as f:
    #     messages = json.load(f)
    #
    # with open('extracted_texts.txt', 'w', encoding='utf-8') as f:
    #     for message in messages:
    #         f.write(
    #             '\n\n-------------------------------------------------------------------------------------------\n\n')
    #
    #         subject = ''
    #
    #         for header in message['payload']['headers']:
    #             if header['name'] == 'Subject':
    #                 subject = censor_string(header['value'], pattern=STRINGS_TO_FILTER_OUT)
    #
    #         try:
    #             message_html = extract_message_body(message, format='full')
    #         except KeyError as e:
    #             print('Error extracting message')
    #             f.write(f'Error extracting message: {e}\n\n')
    #             f.write(str(dir(message['payload'])) + '\n')
    #             f.write(f'{message["payload"]}\n')
    #             continue
    #         soup = BeautifulSoup(message_html, "html.parser")
    #         message_text = soup.get_text()
    #
    #         # Remove excessive linebreaks
    #         message_text = re.sub(r'\n\s*\n', '\n\n', message_text)
    #         # Remove censored word
    #         message_text = censor_string(message_text, pattern=STRINGS_TO_FILTER_OUT)
    #
    #         f.write(f'*{subject}*\n\n')
    #         f.write(message_text)
    #
    # print(urlsafe_b64decode(messages[0]['raw']))
