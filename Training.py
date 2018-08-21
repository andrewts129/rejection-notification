import json
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.linear_model import LogisticRegression
from sklearn import svm
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import confusion_matrix
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
from imblearn.over_sampling import SMOTE


with open("emails-labelled.json", "r") as file:
    data = json.load(file)

subject_vectorizer = TfidfVectorizer()
subject_vectorizer.fit([email["subject"] for email in data])
body_vectorizer = TfidfVectorizer()
body_vectorizer.fit([email["bodyText"] for email in data])
sender_name_vectorizer = TfidfVectorizer()
sender_name_vectorizer.fit([email["senderName"] for email in data])


subject_feature = np.asarray([row for row in subject_vectorizer.transform([email["subject"] for email in data]).A])
body_feature = np.asarray([row for row in subject_vectorizer.transform([email["bodyText"] for email in data]).A])
sender_name_feature = np.asarray([row for row in subject_vectorizer.transform([email["senderName"] for email in data]).A])

features = np.asarray([subject_feature, body_feature, sender_name_feature])

# Needed bc scikit's fit function only accepts 2D arrays
features = features.reshape(len(data), -1)

labels = np.asarray([int(email["isRejection"]) for email in data])

train, test, train_labels, test_labels = train_test_split(features, labels, test_size=0.20, random_state=109)

train, train_labels = SMOTE(random_state=109).fit_sample(train, train_labels)

algo = LogisticRegression(class_weight="balanced")
#algo = svm.SVC(kernel="linear", class_weight="balanced")
#algo = RandomForestClassifier(class_weight="balanced")
#algo = GradientBoostingClassifier()
model = algo.fit(train, train_labels)

predictions = algo.predict(test)

cm = confusion_matrix(test_labels, predictions)

print("True Negatives: " + str(cm[0][0]) + " (" + format(cm[0][0] / len(predictions) * 100, ".2f") + "%)")
print("False Negatives: " + str(cm[1][0]) + " (" + format(cm[1][0] / len(predictions) * 100, ".2f") + "%)")
print("True Positives: " + str(cm[1][1]) + " (" + format(cm[1][1] / len(predictions) * 100, ".2f") + "%)")
print("False Positives: " + str(cm[0][1]) + " (" + format(cm[0][1] / len(predictions) * 100, ".2f") + "%)")
print()
print("Rejections Correct: " + format(cm[1][1] / (cm[1][0] + cm[1][1]) * 100, ".2f") + "%")
