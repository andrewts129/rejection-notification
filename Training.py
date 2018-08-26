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


with open("emails-labelled.json", "r") as file:
    data = json.load(file)

print("Vectorizing...")

subject_vectorizer = TfidfVectorizer()
subject_vectorizer.fit([email["subject"] for email in data])
body_vectorizer = TfidfVectorizer()
body_vectorizer.fit([email["bodyText"] for email in data])
sender_name_vectorizer = TfidfVectorizer()
sender_name_vectorizer.fit([email["senderName"] for email in data])

body_feature = np.asarray([row for row in body_vectorizer.transform([email["bodyText"] for email in data]).A])
subject_feature = np.asarray([row for row in subject_vectorizer.transform([email["subject"] for email in data]).A])
sender_name_feature = np.asarray([row for row in sender_name_vectorizer.transform([email["senderName"] for email in data]).A])

print("About to shape...")
skeleton = np.zeros(body_feature.shape)
skeleton[:subject_feature.shape[0], :subject_feature.shape[1]] = subject_feature
subject_feature = skeleton

skeleton = np.zeros(body_feature.shape)
skeleton[:sender_name_feature.shape[0], :sender_name_feature.shape[1]] = sender_name_feature
sender_name_feature = skeleton

features = np.asarray([body_feature, subject_feature, sender_name_feature])

# Needed bc scikit's fit function only accepts 2D arrays
features = features.reshape(len(data), -1)

labels = np.asarray([int(email["isRejection"]) for email in data])

print("Splitting...")
train, test, train_labels, test_labels = train_test_split(features, labels, test_size=0.20, random_state=109)

#print("SMOTING...")
#train, train_labels = SMOTE(random_state=109).fit_sample(train, train_labels)

print("About to train...")
model = LogisticRegression(class_weight="balanced")
#model = svm.SVC(kernel="linear", class_weight="balanced")
#model = RandomForestClassifier(class_weight="balanced")
#model = GradientBoostingClassifier()
model.fit(train, train_labels)

# Adjusts the intercept because the data is heavily biased (way more non-rejections than rejections)
#prior = 0.54
#model.intercept_ += np.log(prior / (1 - prior)) - np.log((1 - prior) / prior)

print("Predicting...")
predictions = model.predict(test)

cm = confusion_matrix(test_labels, predictions)

print("True Negatives: " + str(cm[0][0]) + " (" + format(cm[0][0] / len(predictions) * 100, ".2f") + "%)")
print("False Negatives: " + str(cm[1][0]) + " (" + format(cm[1][0] / len(predictions) * 100, ".2f") + "%)")
print("True Positives: " + str(cm[1][1]) + " (" + format(cm[1][1] / len(predictions) * 100, ".2f") + "%)")
print("False Positives: " + str(cm[0][1]) + " (" + format(cm[0][1] / len(predictions) * 100, ".2f") + "%)")
print()
print("Rejections Correct: " + format(cm[1][1] / (cm[1][0] + cm[1][1]) * 100, ".2f") + "%")
print()
print("ROC AUC Score: " + str(roc_auc_score(test_labels, predictions)))

print("Dumping...")
joblib.dump(model, "model.pkl", compress=9)
