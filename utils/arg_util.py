import sys
class ArgUtil:
    
    @staticmethod
    def get_named_arg(name, short_name = None):
        args = sys.argv
        
        for arg in args:
            
            long_prefix = "--" + name + "="
            if arg.startswith(long_prefix):
                return arg[len(long_prefix):]
            
            short_prefix = "-" + short_name + "="
            if arg.startswith(short_prefix):
                return arg[len(short_prefix):]
        
        return None