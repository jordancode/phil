
class PhoneNumberUtils:
    
    
    @staticmethod
    def is_valid_phone_number(input_str):
        """
            Returns true if a string could represent a phone number 
        """
        input_str=input_str.replace(" ", "")
        input_str=input_str.lower()
        
        if input_str.startswith("tel:"):
            input_str=input_str[4:]
        
        for c in input_str:
            if not c.isdigit() and c not in ["+","(",")","-","."]:
                return False
            
        is_international =  (input_str.startswith("+"))
        if is_international:
            input_str=input_str[1:]
        
        
        number_str = PhoneNumberUtils.get_digits_only(input_str)
        
        if is_international:
            return len(number_str) > 10 and len(number_str) < 14
        else:
            return len(number_str) == 10
        
    
    @staticmethod
    def get_digits_only(phone_number_string):
        """
            Returns only numerical characters in a phone number string 
        """
        return  "".join([c for c in phone_number_string if c.isdigit()])
        