# coding=UTF-8
from __future__ import division
from trybar.account.models import Account
from django.shortcuts import redirect

class AuthenticationManagementMiddleware(object):
    """
    Annotates current request with some functions
    
    If user is logged in, request gains:
        - property, 'user', which is Account instance of currently logged-in user
        - method, 'logout()', which logs out currenty logged-in user
        
    If user is not logged in, request, gains:
        - property, 'user', which is None
        - method, 'login(aobj)', which logs in user described by aobj, which is Account instance of user to log-in
    
    """
    def process_view(self, request, view_func, view_args, view_kwargs):
    
        def logout(request):
            """Logs out currently logged-in user"""
            del request.session['Account_id']
            request.session.flush()
    
        def login(request, aobj):
            """Logs in user described by aobj. User will not be considered logged-in until the end of current request.
            @type aobj: trybar.account.models.Account instance.
            
            Before called, the invoking code has to check for all conditions that would normally not allow the user 
            to log in (such as activation or bans).
            """
            request.session['Account_id'] = aobj.id
    
        request.user = None
        if 'Account_id' in request.session:
            request.user = Account.objects.get(id=request.session['Account_id'])
            request.logout = lambda: logout(request)
        else:
            request.login = lambda aobj: login(request, aobj)
            request.user = None
            
        return None