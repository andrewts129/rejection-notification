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


def main():
    with open(INPUT_FILE_NAME, "r") as file:
        emails = json.load(file)

    email_subset = get_weighted_subset(emails, TOTAL_SUBSET_SIZE)

    with open("emails-" + str(len(email_subset)) + ".json", "w") as file:
        json.dump(email_subset, file, sort_keys=True, indent=4)

    print("Saved " + str(len(email_subset)) + " emails as emails-" + str(len(email_subset)) + ".json")


if __name__ == '__main__':
    main()
