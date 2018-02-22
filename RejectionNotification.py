from O365 import Inbox, Message
import os
import subprocess
import pickle
import hashlib


def get_read_messages():
    if os.path.isfile("processed_messages.txt"):
        with open("processed_messages.pkl", "rb") as f:
            read_messages = pickle.load(f)

        return read_messages
    else:
        return []


def hash_message(subject_text, body_text):
    m1 = hashlib.md5(body_text.lower().encode("utf-8"))
    m2 = hashlib.md5(subject_text.lower().encode("utf-8"))

    return str(m1.hexdigest()) + str(m2.hexdigest)


def dump_read_messages(new_read_messages):
    hashed_messages = [hash_message(message.getSubject(), message.getBody()) for message in new_read_messages]

    with open("processed_messages.pkl", "ab") as f:
        pickle.dump(hashed_messages, f)


def is_rejection(subject, body):
    full_text = (subject + body).lower

    # Needs to have one of these
    required_words = ["intern", "internship"]
    required_counts = [full_text.count(x) for x in required_words]

    # Should have a few of these
    troublesome_words = ["unfortunately", "other candidates", "other applicants", "another candidate",
                         "another applicant", "for your interest"]
    troublesome_counts = [full_text.count(x) for x in troublesome_words]

    if sum(required_counts) >= 1 and sum(troublesome_counts) >= 2:
        return True
    else:
        return False


def play_taps():
    if not os.path.isfile("Taps.mp3"):
        subprocess.call(["wget", "-O", "Taps.mp3", "http://www.music.army.mil/music/buglecalls/play.asp?Taps.mp3"])
    subprocess.call(["mpg321", "Taps.mp3"])


def main():
    auth = (os.environ["EMAIL_ADDRESS"], os.environ["PASSWORD"])
    inbox = Inbox(auth=auth, getNow=False)

    inbox.getMessages()
    for message in inbox.messages:
        print(message)

    play_taps()


if __name__ == "__main__":
    main()
