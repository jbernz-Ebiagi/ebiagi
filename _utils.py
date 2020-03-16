import functools
import traceback
import subprocess

def catch_exception(f):
    @functools.wraps(f)
    def func(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except:
            args[0].canonical_parent.log_message(traceback.format_exc())
    return func