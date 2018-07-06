#DEPRECATED IN LIEU OF USING SESSION
from AeroMembersApp.models import *
# def company(request):
#     context = {}
#     if request.user.is_anonymous:
#         return context
#     else:
#         activeUserPlan = Subscription.objects.filter(user=request.user,status="Active",plan__type="USER")
#         if activeUserPlan.exists():
#             context['userPlan'] = activeUserPlan.get().plan
#         companies = CompanyUser.objects.filter(user=request.user)
#         context['companies']=companies
#         if request.session.get('currCompanyId',None) != None:
#             context['currCompany'] = Company.objects.get(pk=request.session['currCompanyId'])
#         else:
#             context['currCompany'] = None
#         return context
