from .models import *

from django import forms
from django.core.validators import RegexValidator
from django.shortcuts import render

from django.views import View

from rest_framework.views import APIView
from rest_framework.response import Response


class PhoneNumberVerificationForm(forms.Form):
    phone_number = forms.CharField(
        label="номер абонента",
        error_messages={"incomplete": "Введите номер телефона"},
        validators=[RegexValidator(r"^7[0-9]{10,}$", "Неправильный формат номер ")],
        help_text="введите российский номер в формате MSISDN (например, 79173453223)",
    )


class FindPhoneNumber(View):
    http_method_names = ["post", "get"]

    def post(self, request, *args, **kwargs):
        form = PhoneNumberVerificationForm(
            request.POST,
        )
        if form.is_valid():
            form_data = form.cleaned_data
            op = OperatorProvider()
            data = op.get_data(form_data["phone_number"])

            if not data:
                data = {"error": op.error}

        return render(request, "index.html", {"form": form, "data": data})

    def get(self, request, *args, **kwargs):
        form = PhoneNumberVerificationForm()
        return render(request, "index.html", {"form": form})


class FindPhoneNumberAPI(APIView):

    def get(self, request, format=None):

        if ("phone_number" not in request.GET) or (request.GET["phone_number"] == ""):
            return Response(
                {"error": "Не передан обязательный параметр 'phone_number'"}, status=400
            )

        phone_number = request.GET["phone_number"]

        op = OperatorProvider()
        op_data = op.get_data(phone_number)

        if op_data:
            return Response(op_data)
        else:
            return Response({"error": op.error}, status=op.status)
