import O365
import os
import json
import uuid
from bs4 import BeautifulSoup
from bs4.element import Comment


MESSAGES_PER_FETCH = 40


def download_all_emails(inbox):
    all_messages = inbox.from_folder("Inbox").fetch(MESSAGES_PER_FETCH - 1)

    next_messages_buffer = inbox.fetch_next(1)
    while len(next_messages_buffer) > 0:
        all_messages.extend(next_messages_buffer)
        next_messages_buffer = inbox.fetch_next(MESSAGES_PER_FETCH)
        print("Retrieved " + str(len(all_messages)) + " emails...")

    return all_messages


def build_email_dict(message_obj):
    def text_from_html(body):
        # https://stackoverflow.com/questions/1936466/beautifulsoup-grab-visible-webpage-text
        def tag_visible(element):
            if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
                return False
            if isinstance(element, Comment):
                return False
            return True

        soup = BeautifulSoup(body, 'html.parser')
        texts = soup.findAll(text=True)
        visible_texts = filter(tag_visible, texts)
        return u" ".join(t.strip() for t in visible_texts)

    return {"senderEmail": message_obj.getSenderEmail() if message_obj.getSenderEmail() is not None else "",
            "senderName": message_obj.getSenderName() if message_obj.getSenderName() is not None else "",
            "subject": message_obj.getSubject() if message_obj.getSubject() is not None else "",
            "bodyHtml": message_obj.getBody() if message_obj.getBody() is not None else "",
            "bodyText": text_from_html(message_obj.getBody()) if message_obj.getBody() is not None else "",
            "timeSent": message_obj.json["DateTimeSent"],
            "id": str(uuid.uuid4())}


def main():
    conn = O365.Connection.login(os.environ["EMAIL_ADDRESS"], os.environ["PASSWORD"])
    inbox = O365.FluentInbox()

    messages = download_all_emails(inbox)
    email_dicts = [build_email_dict(message) for message in messages]

    with open("emails.json", "w") as file:
        json.dump(email_dicts, file)


if __name__ == '__main__':
    main()
