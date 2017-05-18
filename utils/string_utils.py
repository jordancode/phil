from framework.config.config import Config
import datetime
import calendar

class StringUtils:
    
    @staticmethod
    def is_valid_name(full_name):
        if not isinstance(full_name,str):
            return False
        
        full_name=full_name.strip()
        full_name=full_name.lower()
        
        if len(full_name) < 3:
            return False
        
        for c in full_name:
            #apostrophes, hypens are ok
            if not ( c.isalpha() or c in [" ","'","-", "."] ):
                return False
                
        split_name = full_name.split()

        
        if not len(split_name) > 1:
            return False
        
        if StringUtils.has_title(full_name):
            split_name.pop(0)

            
        split_name = [n.strip() for n in split_name if n.strip()]
        
        #every name needs a letter
        for name in split_name:
            has_letter=False
            for c in name:
                if c.isalpha():
                    has_letter=True
                    
            if not has_letter:
                return False
        
        if len(split_name) > 4 or len(split_name) < 2:
            return False
        
                
        return True
    
    @staticmethod
    def suffix_integer(d):
        return 'th' if 11<=d<=13 else {1:'st',2:'nd',3:'rd'}.get(d%10, 'th')
    
    @staticmethod
    def get_friendly_date_string(dt):
        today=datetime.datetime.now()
        ret = ""
        if dt.year != today.year:
            ret = str(dt.year)#1995
        elif dt.month == today.month-1:
            ret = "last month"
        elif  dt.month != today.month:
            ret = calendar.month_name[dt.month]#January
        elif dt.day > today.day -7:
            ret = calendar.day_name[dt.weekday()]#Thursday
        elif dt.day > today.day -14:
            ret = "last " + calendar.day_name[dt.weekday()]#last Thursday
        elif dt.day != today.day:
            ret = "earlier this month"
        else:
            ret = "today"
        
        return ret
    
    
    @staticmethod
    def is_male_name(full_name):
        
        MALE_TITLES=["MR","MR.", "SR", "SR."]
        male_names = Config.get("names", "male_name_list")
        
        split_name = full_name.split()
        split_name = [n.strip() for n in split_name if n.strip()]
        
        if not len(split_name):
            return False
        
        first_name =split_name[0].upper()
        if first_name in MALE_TITLES or first_name in male_names:
            return True
        
        return False
    
    
    @staticmethod
    def has_title(full_name):
        
        full_name=full_name.strip()
        full_name=full_name.lower()
                
        TITLES=[ "mr", "mr.","ms","ms.","mrs", "mrs.", "sr", "sr.", "srta", "srta.", "sra", "sra." ]
        
        split_name = full_name.split()
        
        if split_name[0] in TITLES:
            return True
        
        return False
        