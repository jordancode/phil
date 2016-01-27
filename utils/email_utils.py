
GMAIL= "@gmail."
YAHOO = "@yahoo."
AIM = "@aim."
AOL = "@aol."
APPLE = "@apple."
ICLOUD = "@icloud."
MSN = "@msn."
OUTLOOK = "@outlook."
HOTMAIL = "@hotmail."
MAIL_COM = "@mail.com"
YANDEX = "@yandex."

    
CONSUMER_IPS = [GMAIL, GMAIL, AIM, AOL, APPLE, ICLOUD, MSN, OUTLOOK, HOTMAIL, MAIL_COM, YANDEX]

class EmailUtils:
     
    @classmethod
    def is_isp(cls, email, isp):
        return email.find(isp) > 0 #verify we have at least one char before "@"
    
    
    @classmethod
    def is_consumer(cls, email):
        for isp in CONSUMER_IPS:
            if cls.is_isp(email, isp):
                return True
        
        return False