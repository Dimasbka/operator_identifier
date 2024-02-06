from django.shortcuts import render
from django.http import JsonResponse

# Create your views here.

from .models import *

from django import forms
from django.core.validators import RegexValidator
from django.shortcuts import render

from django.views import View




class PhoneNumberVerificationForm (forms.Form):
    phone_numder = forms.CharField(
                label='номер абонента',
                error_messages={"incomplete": "Введите номер телефона"},
                validators=[RegexValidator(r"^7[0-9]{10,}$", "Неправильный формат номер ")],
                help_text='введите российский номер в формате MSISDN (например, 79173453223)',
            )

class FindPhoneNumber(View):
    http_method_names = ["post","get"]

    def post(self, request, *args, **kwargs):
        form = PhoneNumberVerificationForm( request.POST, )
        if form.is_valid():
            form_data = form.cleaned_data
            op = OperatorProvider()
            data = op.get_data(form_data['phone_numder'])

            if not data:
                data = {'error': op.error }

        return render(request,'index.html',{'form':form,'data':data} )


    def get(self, request, *args, **kwargs):
        form = PhoneNumberVerificationForm()
        return render(request,'index.html',{'form':form } )



# def find_phone_number( request ):
#     res = {  }
#     if request.POST:
#         form = PhoneNumberVerificationForm( request.POST, )
#         if form.is_valid():
            
#             form_data = form.cleaned_data
            
#             op = OperatorProvider()
#             data = op.get_data(form_data['phone_numder'])
#             if not data:
#                 data['error'] = op.error

#             res['data'] = data
#     else:
#         form = PhoneNumberVerificationForm()

#     res['form'] = form
#     return render(request,'index.html',res )



# классы для корректной работы с руским языком в json 
class JsonResponseUTF8(JsonResponse):
    def __init__(self, *args, json_dumps_params=None, **kwargs):
        json_dumps_params = {"ensure_ascii": False, **(json_dumps_params or {})}
        super().__init__(*args, json_dumps_params=json_dumps_params, **kwargs)

class JsonResponseBadRequest(JsonResponseUTF8):
    status_code = 400

class JsonResponseNotFound(JsonResponseUTF8):
    status_code = 404


class FindPhoneNumberAPI(View):
    http_method_names = [
        "get",
    ]

    def get(self, request, *args, **kwargs):
        if ('phone_numder' not in request.GET) or (request.GET['phone_numder']==''):
            return JsonResponseBadRequest({
                'error':"Не передан обязательный параметр 'phone_numder'"
            })

        phone_numder = request.GET['phone_numder']

        op = OperatorProvider()
        op_data = op.get_data(phone_numder)

        if op_data:
            return JsonResponseUTF8(op_data)
        else:
            return JsonResponseBadRequest({
                'error':op.error
            })



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions

class FindPhoneNumberAPI2(APIView):
    # permission_classes = [permissions.AllowAny]

    def get(self, request, format=None):

        if ('phone_numder' not in request.GET) or (request.GET['phone_numder']==''):
            return Response ({
                'error':"Не передан обязательный параметр 'phone_numder'"
            }, status=400)

        phone_numder = request.GET['phone_numder']

        op = OperatorProvider()
        op_data = op.get_data(phone_numder)

        if op_data:
            return Response(op_data)
        else:
            return Response({
                'error':op.error
            }, status=op.status)


        """
        Return a list of all users.
        """
        # usernames = [user.username for user in User.objects.all()]
        # return Response(usernames)
        return Response([])