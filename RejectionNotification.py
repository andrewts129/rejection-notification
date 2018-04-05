from O365 import Inbox
import os
import subprocess
import datetime
import logging

logging.basicConfig(filename="logs/rejection-notification.log", format='%(asctime)s %(message)s', level=logging.INFO)


def is_rejection(subject, body):
    full_text = (subject + body).lower()

    # Needs to have one of these
    required_words = ["intern", "internship"]
    required_counts = [full_text.count(x) for x in required_words]

    # Should have at least a few of these
    troublesome_words = ["unfortunately", "other candidates", "other applicants", "another candidate",
                         "another applicant", "your interest", "not be moving forward",
                         "unable to move forward", "not to move forward", "not selected for this position",
                         "unable to offer you a position at this time", "has been filled", "wish you the best of luck",
                         "was not selected", "carefully reviewed your"]
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

    logging.info("Found " + str(len(inbox.messages)) + " messages")

    for message in inbox.messages:
        logging.info("Found message with subject: " + message.getSubject())
        if is_rejection(message.getSubject(), message.getBody()):
            logging.info("Rejected!")
            play_taps()
        else:
            logging.info("Not rejected...")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.error(e)
