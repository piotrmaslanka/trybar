from django.shortcuts import redirect

def must_be_logged(func):
    def f(*args, **kwargs):
        if args[0].user == None: return redirect('/')
        return func(*args, **kwargs)
    return f