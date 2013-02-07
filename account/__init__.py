from django.shortcuts import redirect

def must_be_logged(func):
    def f(*args, **kwargs):
        if args[0].user == None: return redirect('/')
        return func(*args, **kwargs)
    return f

def standard_profile_page_dict(request):
	"""for use in pages that have a 'MOJE KONTO' part - this info can be used to provide the data in 
	consistent manner.

	Will throw if user is not logged in"""
	account = request.user
	return {'profile_ranking':account.meta.rank,
			'profile_points':account.meta.score,
			'profile_bars':account.meta.bar_count,
            'profile_events':account.events_owned.count(),
			'profile_frequenter':account.meta.frequenter_count,
			'profile_familiars':account.meta.familiar_count,
            'profile_messages':account.mail_received.count() + account.befriendee_set.filter(confirmed=False).count()}