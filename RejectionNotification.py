from O365 import Inbox
import os
import subprocess
import datetime
import logging
import schedule
import time
from sklearn.externals import joblib
from bs4 import BeautifulSoup
from bs4.element import Comment
import json
import json
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.linear_model import LogisticRegression
from sklearn import svm
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import confusion_matrix, roc_auc_score
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
from imblearn.over_sampling import SMOTE
from sklearn.externals import joblib


logging.basicConfig(filename="logs/rejection-notification.log", format='%(asctime)s %(message)s', level=logging.INFO)


def train_model():
    with open("emails-labelled.json", "r") as file:
        data = json.load(file)

    subject_vectorizer = TfidfVectorizer()
    subject_vectorizer.fit([email["subject"] for email in data])
    body_vectorizer = TfidfVectorizer()
    body_vectorizer.fit([email["bodyText"] for email in data])
    sender_name_vectorizer = TfidfVectorizer()
    sender_name_vectorizer.fit([email["senderName"] for email in data])

    subject_feature = np.asarray(
        [row for row in subject_vectorizer.transform([email["subject"] for email in data]).A])
    body_feature = np.asarray(
        [row for row in subject_vectorizer.transform([email["bodyText"] for email in data]).A])
    sender_name_feature = np.asarray(
        [row for row in subject_vectorizer.transform([email["senderName"] for email in data]).A])

    features = np.asarray([subject_feature, body_feature, sender_name_feature])

    # Needed bc scikit's fit function only accepts 2D arrays
    features = features.reshape(len(data), -1)

    labels = np.asarray([int(email["isRejection"]) for email in data])

    model = LogisticRegression(class_weight="balanced")
    model.fit(features, labels)

    # Adjusts the intercept because the data is heavily biased (way more non-rejections than rejections)
    prior = 0.57
    model.intercept_ += np.log(prior / (1 - prior)) - np.log((1 - prior) / prior)

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
        one_minute_ago = datetime.datetime.utcnow() - datetime.timedelta(minutes=1, seconds=1)
        inbox.setFilter("DateTimeReceived gt " + one_minute_ago.strftime("%Y-%m-%dT%H:%M:%SZ"))
        inbox.getMessages()

        return [build_email_dict(message) for message in inbox.messages]

    messages = get_messages(inbox)

    subject_feature = np.asarray(
        [row for row in subject_vectorizer.transform([email["subject"] for email in messages]).A])
    body_feature = np.asarray(
        [row for row in subject_vectorizer.transform([email["bodyText"] for email in messages]).A])
    sender_name_feature = np.asarray(
        [row for row in subject_vectorizer.transform([email["senderName"] for email in messages]).A])

    features = np.asarray([subject_feature, body_feature, sender_name_feature])

    predictions = model.predict(features)

    if sum(predictions) > 0:
        play_music()


def play_music():
    subprocess.call(["mpg321", "Taps.mp3"])


def main():
    auth = (os.environ["EMAIL_ADDRESS"], os.environ["PASSWORD"])
    inbox = Inbox(auth=auth, getNow=False)

    messages =
    model, subject_vectorizer, body_vectorizer, sender_name_vectorizer = train_model(messages)
    schedule.every(1).minutes.do(check_for_rejections, inbox, model, subject_vectorizer, body_vectorizer, sender_name_vectorizer)

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.error(e)
