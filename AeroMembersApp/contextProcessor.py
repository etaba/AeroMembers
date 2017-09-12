from models import *
def company(request):
	if request.user.is_anonymous():
		return {}
	else:
		companies = CompanyUser.objects.filter(user=request.user)
		return {'companies':companies}
