import sys
class CLIUtil:
    
    @staticmethod
    def get_named_arg(name, short_name = None):
        args = sys.argv
        
        for arg in args:
            
            long_prefix = "--" + name + "="
            if arg.startswith(long_prefix):
                return arg[len(long_prefix):]
            
            if short_name:
                short_prefix = "-" + short_name + "="
                if arg.startswith(short_prefix):
                    return arg[len(short_prefix):]
        
        return None
    
    @staticmethod
    def get_named_arg_from_ps_line(ps_line, name, short_name=None):
        keys=["--"+name+"="]
        if short_name:
            keys.append("-"+short_name+"=")
        
        for k in keys:
            if k in ps_line:
                values_part = ps_line.split(k)[1]
                return values_part.split(" ")[0] 
        
        return None