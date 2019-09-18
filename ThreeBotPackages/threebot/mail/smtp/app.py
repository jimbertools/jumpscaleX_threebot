from Jumpscale import j
import smtpd
from .gsmtpd import SMTPServer


class MailServer(SMTPServer):
    # Do something with the gathered message
    def process_message(self, peer, mailfrom, rcpttos, data):
        j.debug()
        inheaders = 1
        lines = data.split("\n")
        print("---------- MESSAGE FOLLOWS ----------")
        for line in lines:
            # headers first
            if inheaders and not line:
                print("X-Peer:", peer[0])
                inheaders = 0
            print(line)
        print("------------ END MESSAGE ------------")
        self.store_mail(mailfrom, rcpttos, data)
        print("------------ Data saved In bcdb ------------")

    def store_mail(self, mailform, rcpttos, data):
        smtpInstance = j.data.bcdb.get("smtp")
        mail_model = smtpInstance.model_get(url="jumpscale.smtp.models")
        mail = mail_model.new()
        mail.sender = mailform
        mail.receiver = rcpttos
        mail.body = data
        mail.save()

