from O365 import Inbox
import os
import subprocess
import datetime


def is_rejection(subject, body):
    full_text = (subject + body).lower()

    # Needs to have one of these
    required_words = ["intern", "internship"]
    required_counts = [full_text.count(x) for x in required_words]

    # Should have a few of these
    troublesome_words = ["unfortunately", "other candidates", "other applicants", "another candidate",
                         "another applicant", "for your interest"]
    troublesome_counts = [full_text.count(x) for x in troublesome_words]

    return sum(required_counts) >= 1 and sum(troublesome_counts) >= 2


def play_taps():
    if not os.path.isfile("Taps.mp3"):
        subprocess.call(["wget", "-O", "Taps.mp3", "http://www.music.army.mil/music/buglecalls/play.asp?Taps.mp3"])
    subprocess.call(["mpg321", "Taps.mp3"])


def main():
    auth = (os.environ["EMAIL_ADDRESS"], os.environ["PASSWORD"])
    inbox = Inbox(auth=auth, getNow=False)

    # Gets all messages received in the last two minutes
    # Gives an extra 10 seconds for startup time
    two_minutes_ago = datetime.datetime.utcnow() - datetime.timedelta(minutes=2, seconds=10)
    inbox.setFilter("DateTimeReceived gt " + two_minutes_ago.strftime("%Y-%m-%dT%H:%M:%SZ"))
    inbox.getMessages()

    for message in inbox.messages:
        if is_rejection(message.getSubject(), message.getBody()):
            play_taps()


if __name__ == "__main__":
    main()
