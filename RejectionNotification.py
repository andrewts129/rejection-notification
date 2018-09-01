from O365 import Inbox
import os
import subprocess
import datetime
import logging
import schedule
import time
from bs4 import BeautifulSoup
from bs4.element import Comment
import numpy as np
from sklearn.externals import joblib
import requests


#logging.basicConfig(filename="logs/rejection-notification.log", format='%(asctime)s %(message)s', level=logging.INFO)


def load_model():
    model = joblib.load("model.pkl")
    subject_vectorizer = joblib.load("subject_vectorizer.pkl")
    body_vectorizer = joblib.load("body_vectorizer.pkl")
    sender_name_vectorizer = joblib.load("sender_name_vectorizer.pkl")

    return model, subject_vectorizer, body_vectorizer, sender_name_vectorizer


def check_for_rejections(inbox, model, subject_vectorizer, body_vectorizer, sender_name_vectorizer):
    def get_messages(inbox):
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

            return {"senderName": message_obj.getSenderName() if message_obj.getSenderName() is not None else "",
                    "subject": message_obj.getSubject() if message_obj.getSubject() is not None else "",
                    "body": text_from_html(message_obj.getBody()) if message_obj.getBody() is not None else ""}

        # Gets all messages received in the last minute
        one_minute_ago = datetime.datetime.utcnow() - datetime.timedelta(minutes=1)
        inbox.setFilter("DateTimeReceived gt " + one_minute_ago.strftime("%Y-%m-%dT%H:%M:%SZ"))
        inbox.getMessages()

        return [build_email_dict(message) for message in inbox.messages]

    def contains_rejection(messages):
        body_feature = np.asarray(
            [row for row in body_vectorizer.transform([email["body"] for email in messages]).A])
        subject_feature = np.asarray(
            [row for row in subject_vectorizer.transform([email["subject"] for email in messages]).A])
        sender_name_feature = np.asarray(
            [row for row in sender_name_vectorizer.transform([email["senderName"] for email in messages]).A])

        # Padding with zeros so that all features have the same length
        skeleton = np.zeros(body_feature.shape)
        skeleton[:subject_feature.shape[0], :subject_feature.shape[1]] = subject_feature
        subject_feature = skeleton

        # Padding with zeros so that all features have the same length
        skeleton = np.zeros(body_feature.shape)
        skeleton[:sender_name_feature.shape[0], :sender_name_feature.shape[1]] = sender_name_feature
        sender_name_feature = skeleton

        features = np.asarray([body_feature, subject_feature, sender_name_feature])

        features = features.reshape(len(messages), -1)

        predictions = model.predict(features)

        return sum(predictions) > 0

    messages = get_messages(inbox)
    if len(messages) > 0 and contains_rejection(messages):
        play_music()


def play_music():
    requests.post(os.environ["SOUND_SERVER_URL"] + "/play?filename=" + os.environ["MUSIC_FILE_NAME"])


def main():
    auth = (os.environ["EMAIL_ADDRESS"], os.environ["PASSWORD"])
    inbox = Inbox(auth=auth, getNow=False)

    model, subject_vectorizer, body_vectorizer, sender_name_vectorizer = load_model()

    check_for_rejections(inbox, model, subject_vectorizer, body_vectorizer, sender_name_vectorizer)
    schedule.every(1).minutes.do(
        check_for_rejections, inbox, model, subject_vectorizer, body_vectorizer, sender_name_vectorizer
    )

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    # try:
    #     main()
    # except Exception as e:
    #     logging.error(e)

    main()
