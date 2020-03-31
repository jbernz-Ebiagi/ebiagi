import functools
import traceback
import subprocess

def catch_exception(f):
    @functools.wraps(f)
    def func(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except:
            args[0].log(traceback.format_exc())
    return func

def strip_name_params(name):
    if name.find('[') != -1:
        return name[0:name.find('[')]
    return name