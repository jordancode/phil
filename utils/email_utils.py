

GMAIL= "@gmail."
YAHOO = "@yahoo."
ATT_NET = "@att.net"
AIM = "@aim."
AOL = "@aol."
APPLE = "@apple."
ICLOUD = "@icloud."
MSN = "@msn."
LIVE_COM = "@live.com"
PASSPORT = "@pasport."
OUTLOOK = "@outlook."
HOTMAIL = "@hotmail."
MAIL_COM = "@mail.com"
YANDEX = "@yandex."
HEARTTHIS = "@heartthis.com"
SCHOOLFEED = "@schoolfeed.com"
PHOTOKEEPER = "@photokeeper.com"
EDU = ".edu"


GOOGLE_TYPES = [GMAIL,HEARTTHIS,SCHOOLFEED,PHOTOKEEPER]
MICROSOFT_TYPES = [MSN,OUTLOOK,HOTMAIL,LIVE_COM,PASSPORT]
APPLE_TYPES = [APPLE,ICLOUD]
AOL_TYPES = [AOL,AIM]
YAHOO_TYPES = [YAHOO, ATT_NET]


CONSUMER_IPS = GOOGLE_TYPES + MICROSOFT_TYPES + APPLE_TYPES + AOL_TYPES + YAHOO_TYPES + [MAIL_COM, YANDEX]


GOOGLE_BCC = "photokeeper.bcc@gmail.com"
YAHOO_BCC = "photokeeper.bcc@yahoo.com"
AOL_BCC = "photokeeper.bcc@aol.com"
MICROSOFT_BCC = "photokeeper.bcc@outlook.com"



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
    "lancetokuda@att.net"
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
    def get_bcc_address(cls, email):
        if cls.is_isp(email, GOOGLE_TYPES):
            return GOOGLE_BCC
        elif cls.is_isp(email, YAHOO_TYPES):
            return YAHOO_BCC
        elif cls.is_isp(email, AOL_TYPES):
            return AOL_BCC
        elif cls.is_isp(email, MICROSOFT_TYPES):
            return MICROSOFT_BCC
        
        return None
        
        
    
    
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
    
    
    @classmethod
    def parse_from_field(cls, from_field):
        ret = []
        from_field.replace("'","")
        from_field.replace('"',"")
        from_arr = from_field.split(",")
        for address in from_arr:
            address_parts = address.split("<")
            
            if len(address_parts) == 2:
                name = address_parts[0].strip()
                email = address_parts[1].split(">")[0].strip()
                o = {}
                if name:
                    o["name"]=name
                if email:
                    o["email"]=email
                
                if o:
                    ret.append(o)
            else:
                field=address_parts[0].strip()
                if field:
                    if cls.is_valid_email(field):
                        ret.append({"email" : field})
                    else:
                        ret.append({"name" : field})
        
        return ret
        
        
        