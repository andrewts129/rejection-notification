import json
import random

INPUT_FILE_NAME = "emails.json"
TOTAL_SUBSET_SIZE = 50
PERCENT_REJECTIONS = 0.5


def get_weighted_subset(emails, subset_size):
    rejections = [email for email in emails if email["isRejection"]]
    non_rejections = [email for email in emails if not email["isRejection"]]

    rejections_sample = get_random_subset(rejections, subset_size * PERCENT_REJECTIONS)
    non_rejections_sample = get_random_subset(non_rejections, subset_size * (1 - PERCENT_REJECTIONS))

    return rejections_sample + non_rejections_sample


def get_random_subset(emails, subset_size):
    return [email for email in emails if random.random() < (subset_size / len(emails))]


def is_rejection_simple(subject, body):
    full_text = (subject + body).lower()

    # Needs to have one of these
    required_words = ["intern", "internship"]
    required_counts = [full_text.count(x) for x in required_words]

    # Should have at least a few of these
    troublesome_words = ["unfortunately", "other candidates", "other applicants", "another candidate",
                         "another applicant", "your interest", "not be moving forward",
                         "unable to move forward", "not to move forward", "not selected for this position",
                         "unable to offer you a position at this time", "has been filled", "wish you the best of luck",
                         "was not selected", "carefully reviewed your", "unable to move forward"]
    troublesome_counts = [full_text.count(x) for x in troublesome_words]

    return sum(required_counts) >= 1 and sum(troublesome_counts) >= 2


def main():
    with open(INPUT_FILE_NAME, "r") as file:
        emails = json.load(file)

    for email in emails:
        email["isRejection"] = is_rejection_simple(email["subject"], email["bodyText"])

    email_subset = get_weighted_subset(emails, TOTAL_SUBSET_SIZE)

    with open("emails-" + str(len(email_subset)) + ".json", "w") as file:
        json.dump(email_subset, file, sort_keys=True, indent=4)

    print("Saved " + str(len(email_subset)) + " emails as emails-" + str(len(email_subset)) + ".json")


if __name__ == '__main__':
    main()
