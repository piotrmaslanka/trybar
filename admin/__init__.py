def must_be_admin(func):
    def f(*args, **kwargs):
        if not args[0].session['is_Admin']: return redirect('/')
        return func(*args, **kwargs)
    return f

def is_admin(request):
    if request.user == None: return False
    return request.session['is_Admin']