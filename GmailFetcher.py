from grader.Email import Email
from grader.EmailFetcher import EmailFetcher
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
import os.path
import base64
import email
from bs4 import BeautifulSoup
import datetime
import traceback
from fuzzywuzzy import fuzz

class GmailFetcher(EmailFetcher):
    def __init__(self, assignment_name):
        self.assignment_name = assignment_name
        super().__init__()
    def get_emails(self, start_date, end_date):
        start_date_time = datetime.datetime(start_date.year, start_date.month, start_date.day, 0, 0, 0)
        end_date_time = datetime.datetime(end_date.year, end_date.month, end_date.day, 0, 0, 0)
        email_list = []
        # adapted from https://www.geeksforgeeks.org/how-to-read-emails-from-gmail-using-gmail-api-in-python/
        # Define the SCOPES. If modifying it, delete the token.pickle file.
        SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

        # Variable creds will store the user access token.
        # If no valid token found, we will create one.
        creds = None

        # The file token.pickle contains the user access token.
        # Check if it exists
        if os.path.exists('token.pickle'):
            # Read the token from the file and store it in the variable creds
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)

        # If credentials are not available or are invalid, ask the user to log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)

            # Save the access token in token.pickle file for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        # Connect to the Gmail API
        service = build('gmail', 'v1', credentials=creds)

        # request a list of all the messages
        result = service.users().messages().list(userId='me').execute()

        # We can also pass maxResults to get any number of emails. Like this:
        # result = service.users().messages().list(maxResults=200, userId='me').execute()
        messages = result.get('messages')

        # messages is a list of dictionaries where each dictionary contains a message id.

        # iterate through all the messages
        for msg in messages:
            # Get the message from its id
            txt = service.users().messages().get(userId='me', id=msg['id']).execute()
            invalid = False
            # Use try-except to avoid any Errors
            try:
                # Get value of 'payload' from dictionary 'txt'
                payload = txt['payload']
                headers = payload['headers']

                # Look for Subject and Sender Email in the headers
                found_received_time = False
                for d in headers:
                    if d['name'] == 'Subject':
                        subject = d['value']
                    elif d['name'] == 'From':
                        sender = d['value']
                    elif d['name'] == 'Received' and not found_received_time:
                        # retrieve the date email was received

                        # TODO figure out why hours are offset when printed by runner
                        received_date_raw = d['value'].split(',')[1].strip()
                        # print(received_date_raw)
                        day = int(received_date_raw.split(' ')[0])
                        month = received_date_raw.split(' ')[1]
                        month_number = super().date_string_to_value_index(month)
                        year = int(received_date_raw.split(' ')[2])
                        time = received_date_raw.split(' ')[3]
                        # print(time)
                        hour = int(time.split(':')[0])
                        # print(hour)
                        minute = int(time.split(':')[1])
                        second = int(time.split(':')[2])
                        # print(year, month_number, day, hour, minute, second)
                        constructed_datetime = datetime.datetime(year, month_number, day, hour, minute, second)
                        # print(constructed_datetime)
                        if not (start_date_time <= constructed_datetime <= end_date_time):
                            invalid = True
                            break
                        else:
                            found_received_time = True
                if not invalid and fuzz.ratio(subject, self.assignment_name) > 80:
                    # The Body of the message is in Encrypted format. So, we have to decode it.
                    # Get the data and decode it with base 64 decoder.
                    body = None
                    """
                    parts = payload.get('parts')[0]
                    data = parts['body']['data']
                    data = data.replace("-", "+").replace("_", "/")
                    decoded_data = base64.b64decode(data)

                    # Now, the data obtained is in lxml. So, we will parse
                    # it with BeautifulSoup library
                    soup = BeautifulSoup(decoded_data, "lxml")
                    body = soup.body()

                    """
                    parts = [txt['payload']]

                    # look for attachments
                    # adapted from https://stackoverflow.com/a/45592202
                    while parts:
                        part = parts.pop()
                        if part.get('parts'):
                            parts.extend(part['parts'])
                        if part.get('filename'):
                            if 'data' in part['body']:
                                file_data = base64.urlsafe_b64decode(part['body']['data'].encode('UTF-8'))
                            elif 'attachmentId' in part['body']:
                                attachment = service.users().messages().attachments().get(
                                    userId='me', messageId=msg['id'], id=part['body']['attachmentId']
                                ).execute()
                                file_data = base64.urlsafe_b64decode(attachment['data'].encode('UTF-8'))
                            else:
                                file_data = None
                            # valid file data found, save to disk
                            if file_data:

                                # assignment folder
                                path = super().STORAGE_PATH + self.assignment_name
                                if not os.path.exists(path):
                                    os.mkdir(path)

                                # user submission folder for assignment
                                path = path + "/" + sender.split('<')[0].strip() + "/"
                                if not os.path.exists(path):
                                    os.mkdir(path)
                                path = ''.join([path, part['filename']])

                                # write file contents to user submission folder
                                with open(path, 'wb') as f:
                                    f.write(file_data)

                    # Printing the subject, sender's email and message
                    # print("Subject: ", subject)
                    # print("From: ", sender)
                    # print("Message: ", body)

                    # create email object from this email's data
                    constructed_email = Email(subject, sender, body, None, constructed_datetime)
                    # print(constructed_email.to_string())
                    email_list.append(constructed_email)
            except Exception as e:
                traceback.print_exc()
                pass
            if invalid:
                break
        return email_list

    def date_string_to_value_index(self, string):
        return super().date_string_to_value_index(string)