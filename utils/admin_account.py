from framework.utils.singleton import Singleton
import bcrypt

MIN_PASSWORD = 6
MIN_UN = 3

class AdminAccount(metaclass=Singleton):
    
    _user_hash = None
    
    def __init__(self):
        self._load_file()
    
    def authorize(self, user_name, password):
        if user_name in self._user_hash:
            return self._pw_check(password, self._user_hash[user_name])
        
        return False
    
    def add_user(self, user_name, password):
                
        self._verify_user_name(user_name)
        self._verify_password(password)
        
        self._user_hash[user_name] = self._hash_pw(password)
        
        return self._write_file()
    
    
    #------------- I/O ----------------
    
    def _load_file(self):
        
        self._user_hash = {}
        
        try:
            with open('./config/admin_accounts.txt',"r") as data_file:
                account_list = data_file.read().splitlines() 
        except IOError:
            return False
        
        for line in account_list:
            try:
                user_name, password = self._parse_line(line)
                self._user_hash[user_name] = password
            except Exception:
                pass
    
    def _write_file(self):
        try:
            with open('./config/admin_accounts.txt',"w") as data_file:
                temp =  self._user_hash.copy()
                for un,p in self._user_hash.items():
                    try:
                        data_file.write(self._create_line(un,p))
                        temp[un] = p
                    except Exception:
                        pass
                
                #filters out broken users
                self._user_hash = temp
                
        except IOError:
            return False
        
        return True
    
    def _parse_line(self, text_line):
        text_arr = text_line.split("|")
        
        user_name = text_arr[0]
        hashed_pw = text_arr[1].encode('utf-8')
        
        self._verify_user_name(user_name)
        self._verify_hashed_password(hashed_pw)
        
        return user_name, hashed_pw
    
    def _create_line(self, user_name, hashed_pw):
        self._verify_user_name(user_name)
        self._verify_hashed_password(hashed_pw)
        
        return ( user_name + "|" + hashed_pw.decode('utf-8') + "\n" )
    
    
    #------------- Input validation ------------- 
        
    def _verify_user_name(self, user_name):
        if len(user_name) < MIN_UN:
            raise Exception("User name must be at least " + str(MIN_UN) + " chars")
        if not str.isalnum(user_name):
            raise Exception("User name can only be letters and numbers")
        
    
    def _verify_password(self, password):
        if len(password) < MIN_PASSWORD:
            raise Exception("Password must be at least " + str(MIN_PASSWORD) + " chars") 
    
    def _verify_hashed_password(self, hashed_pw):
        if not hashed_pw:
            raise Exception("Password hash is empty")   
    
    
    
    #------------- Password hashing -------------
    
    def _pw_check(self, plaintext_pw, hashed_pw):
        return (bcrypt.hashpw(plaintext_pw.encode('utf-8'), hashed_pw) == hashed_pw)
    
    def _hash_pw(self, password):
        return bcrypt.hashpw(password.encode('utf-8'),bcrypt.gensalt()) 
    
    