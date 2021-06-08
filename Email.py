class Email:
    def __init__(self):
        self.Subject = None
        self.From = None
        self.Message = None
        self.Files = None
        self.ReceiveDate = None

    def __init__(self, sub, fro, mes, fil, rec):
        self.Subject = sub
        self.From = fro
        self.Message = mes
        self.Files = fil
        self.ReceiveDate = rec

    def to_string(self):
        return "From: %s\nSubject: %s\nMessage: %s\nReceived: %s"%(self.From, self.Subject, self.Message, self.ReceiveDate)