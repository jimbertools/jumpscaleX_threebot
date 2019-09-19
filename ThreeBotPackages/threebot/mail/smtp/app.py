from Jumpscale import j
import smtpd
from .gsmtpd import SMTPServer
from .handleMail import parse_email_body


class MailServer(SMTPServer):
    # Do something with the gathered message
    def process_message(self, peer, mailfrom, rcpttos, data):
        # import ipdb

        # ipdb.set_trace()
        # inheaders = 1
        # lines = data.split("\n")
        # print("---------- MESSAGE FOLLOWS ----------")
        # for line in lines:
        #     # headers first
        #     if inheaders and not line:
        #         print("X-Peer:", peer[0])
        #         inheaders = 0
        #     print(line)
        # print("------------ END MESSAGE ------------")
        self.store_mail(data)
        print("------------ Data saved In bcdb ------------")

    def store_mail(self, data):
        # j.debug()
        result = parse_email_body(data)
        print("The result")
        print(result)
        smtpInstance = j.data.bcdb.get("mails")
        mail_model = smtpInstance.model_get(url="jumpscale.email.message")
        mail = mail_model.new()
        # mail.sender = mailform
        # mail.receiver = rcpttos
        # mail.body = data
        # mail.save()

