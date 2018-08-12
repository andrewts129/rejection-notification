import O365
import os
import json
import uuid

MESSAGES_PER_FETCH = 20


def download_all_emails(inbox):
    all_messages = inbox.from_folder("Inbox").fetch(MESSAGES_PER_FETCH - 1)

    next_messages_buffer = inbox.fetch_next(1)
    while len(next_messages_buffer) > 0:
        all_messages.extend(next_messages_buffer)
        next_messages_buffer = inbox.fetch_next(MESSAGES_PER_FETCH)
        print("Retrieved " + str(len(all_messages)) + " emails...")

    return all_messages


def build_email_dict(message_obj):
    return {"senderEmail": message_obj.getSenderEmail(),
            "senderName": message_obj.getSenderName(),
            "subject": message_obj.getSubject(),
            "body": message_obj.getBody(),
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
