import json

INPUT_FILE_NAME = "emails.json"


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
        # TODO remove this
        del email["bodyHtml"]
        email["isRejection"] = is_rejection_simple(email["subject"], email["bodyText"])

    # Sorts the list so that rejections are on top
    emails = sorted(emails, key=lambda x: x["isRejection"], reverse=True)

    with open(INPUT_FILE_NAME.split(".")[0] + "-labelled.json", "w") as file:
        json.dump(emails, file, sort_keys=True, indent=4)


if __name__ == '__main__':
    main()
