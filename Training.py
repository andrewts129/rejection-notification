import json
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import confusion_matrix
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np


with open("emails-labelled.json", "r") as file:
    data = json.load(file)

subject_vectorizer = TfidfVectorizer()
subject_vectorizer.fit([email["subject"] for email in data])
body_vectorizer = TfidfVectorizer()
body_vectorizer.fit([email["bodyText"] for email in data])

subject_feature = np.asarray([row for row in subject_vectorizer.transform([email["subject"] for email in data]).A])
body_feature = np.asarray([row for row in subject_vectorizer.transform([email["bodyText"] for email in data]).A])

features = np.asarray([subject_feature, body_feature])

# Needed bc scikit's fit function only accepts 2D arrays
features = features.reshape(len(data), -1)

labels = np.asarray([int(email["isRejection"]) for email in data])

train, test, train_labels, test_labels = train_test_split(features, labels, test_size=0.2)

gnb = GaussianNB()
model = gnb.fit(train, train_labels)

predictions = gnb.predict(test)

cm = confusion_matrix(test_labels, predictions)

print("True Negatives: " + str(cm[0][0]) + " (" + str(cm[0][0] / len(predictions) * 100) + "%)")
print("False Negatives: " + str(cm[1][0]) + " (" + str(cm[1][0] / len(predictions) * 100) + "%)")
print("True Positives: " + str(cm[1][1]) + " (" + str(cm[1][1] / len(predictions) * 100) + "%)")
print("False Positives: " + str(cm[0][1]) + " (" + str(cm[0][1] / len(predictions) * 100) + "%)")
