from grader.GmailFetcher import GmailFetcher
import datetime
import sys

def main():
    gm = GmailFetcher("Assignment 1")
    email_list = gm.get_emails(datetime.date(2021, 6, 7), datetime.date(2021, 6, 8))

    print("Received following emails for the given criteria:")
    for email in email_list:
        print(email.to_string())
main()