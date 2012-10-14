from trybar.accnews.models import *

def accnews_for(account, newstype, *args):
	"""account is a doer, so his familiars will be notified about the issue"""

	if len(args) == 0:
		args = (0, 0)
	elif len(args) == 1:
		args = (args[0] if type(args[0]) == int else args[0].id, 0)
	elif len(args) == 2:
		args = (args[0] if type(args[0]) == int else args[0].id,
				args[1] if type(args[1]) == int else args[1].id)

	elif len(args) > 2:
		raise Exception, 'Invalid invocation: maximum two extra-arguments expected'

	accnkwa = {'who':account, 'report_type':newstype, 'arg1':args[0], 'arg2':args[1]}

	for familiar in account.familiar_set:
		AccNews(whom=familiar, **accnkwa).save()