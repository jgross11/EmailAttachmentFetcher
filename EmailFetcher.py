from abc import ABC, abstractmethod
import os


class EmailFetcher(ABC):
    months = {
        "Jan": 1,
        "Feb": 2,
        "Mar": 3,
        "Apr": 4,
        "May": 5,
        "Jun": 6,
        "Jul": 7,
        "Aug": 8,
        "Sep": 9,
        "Oct": 10,
        "Nov": 11,
        "Dec": 12
    }
    STORAGE_PATH = "C://GraderSubmissions/"

    def __init__(self):
        if not os.path.exists(self.STORAGE_PATH):
            os.mkdir(self.STORAGE_PATH)

    @abstractmethod
    def get_emails(self, startDate, endDate):
        pass
    def date_string_to_value_index(self, string):
        if string in self.months:
            return self.months[string]
        else:
            print("invalid month string obtained when fetching emails")