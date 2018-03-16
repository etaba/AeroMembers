from AeroMembersApp.models import *
def company(request):
    context = {}
    if request.user.is_anonymous:
        return context
    else:
        if hasattr(request.user,'membership'):
            context['membership'] = request.user.membership.level
        companies = CompanyUser.objects.filter(user=request.user)
        context['companies']=companies
        if request.session.get('currCompanyId',None) != None:
            context['currCompany'] = Company.objects.get(pk=request.session['currCompanyId'])
        else:
            context['currCompany'] = None
        return context
