import random
import string
class RandomToken:
    
    @staticmethod
    def build(length):
        return ''.join(random.SystemRandom().choice( (string.ascii_letters + string.digits) ) for _ in range(length))