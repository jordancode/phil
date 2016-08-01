
class PhoneNumberUtils:
    
    
    @staticmethod
    def is_valid_phone_number(input_str):
        
        input_str=input_str.lower()
        if input_str.startswith("tel:"):
            input_str=input_str[4:]
        
        for c in input_str:
            if not c.isdigit() and c not in ["+","(",")","-","."]:
                return False
            
        is_international =  (input_str.startswith("+"))
        if is_international:
            input_str=input_str[1:]
        
        
        number_str = "".join([c for c in input_str if c.isdigit()])
        
        if is_international:
            return len(number_str) > 10 and len(number_str) < 14
        else:
            return len(number_str) == 10
        