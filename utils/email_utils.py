

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
HEARTTHIS = "@heartthis.com"
SCHOOLFEED = "@schoolfeed.com"
PHOTOKEEPER = "@photokeeper.com"

GOOGLE_TYPES = [GMAIL,HEARTTHIS,SCHOOLFEED,PHOTOKEEPER]
MICROSOFT_TYPES = [MSN,OUTLOOK,HOTMAIL]
APPLE_TYPES = [APPLE,ICLOUD]
AOL_TYPES = [AOL,AIM]
    
CONSUMER_IPS = GOOGLE_TYPES + MICROSOFT_TYPES + APPLE_TYPES + AOL_TYPES + [YAHOO, MAIL_COM, YANDEX]

WHITELIST = [
    "jordan.claassen@gmail.com", 
    "claassja@gmail.com", 
    "devjordan1@gmail.com", 
    "bob.dobalina.sf@gmail.com", 
    "phdlance@gmail.com", 
    "lance@heartthis.com", 
    "lance@schoolfeed.com",
    "phdlance@yahoo.com",
    "georgekooney@yahoo.com",
    "samerssally@yahoo.com",
    "mayor.mason@yahoo.com",
    ]


class EmailUtils:
     
    @classmethod
    def is_isp(cls, email, isp):
        
        if isinstance(isp, str):
            isp_list = [isp]
        else:
            isp_list = isp
        
        for isp_type in isp_list:
            if email.find(isp_type) > 0:
                #verify we have at least one char before "@"
                return True
        
        return False
        
    
    
    @classmethod
    def is_consumer(cls, email):
        for isp in CONSUMER_IPS:
            if cls.is_isp(email, isp):
                return True
        
        return False
    
    @classmethod
    def is_whitelisted(cls, email):
        if cls.is_isp(email, PHOTOKEEPER):
            return True
        
        return email in WHITELIST
    
    @classmethod
    def is_valid_email(cls,email_address):
        good_length = (len(email_address) >= 5 and len(email_address) <= 255)
        if not good_length:
            return False 
        
        
        split = email_address.split("@")
        good_at = (len(split) == 2 
                   and len(split[0]) >= 1 
                   and len(split[1]) >= 3)
        if not good_at:
            return False
        
        
        dot_split = split[1].split(".")
        good_dot = (len(dot_split) >= 2)
        for s in dot_split:
            good_dot = good_dot and len(s) >= 1
        
        
        return good_dot 
        