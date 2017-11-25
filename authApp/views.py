from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import HttpResponse

import bcrypt
import jwt
import json

from authApp import forms
from authApp.models import APIToken

# Create your views here.


def validate_api_token(client_api_token=None):
    if client_api_token is None:
        raise ValueError("API_Token can't be None")
    stored_api_token = APIToken.objects.get(token=client_api_token)
    if stored_api_token is None:
        raise ValueError('No Stored API Token for token \'%s\'' % client_api_token)
    api_token_values = decode_api_token(api_token=stored_api_token, token=client_api_token)
    return stored_api_token.created_date.__str__() == api_token_values.get('created_date') and \
        stored_api_token.edit_date_in_token == api_token_values.get('edit_date') and \
        (
            not stored_api_token.expires or
            stored_api_token.expire_date.__str__() == api_token_values.get('expires')
        ) and stored_api_token.app_name == api_token_values.get('app_name')


def decode_api_token(api_token=None, token=None):
    if api_token is None:
        raise ValueError("API_Token can't be None")
    if token is None:
        return jwt.decode(api_token.token, api_token.secret_key, algorithms=[api_token.token_algo])
    else:
        return jwt.decode(token, api_token.secret_key, algorithms=[api_token.token_algo])


def update_api_token(api_token=None, regen_secret_key=False):
    if api_token is None:
        raise ValueError("API_Token can't be None")
    if regen_secret_key or api_token.secret_key is None or len(api_token.secret_key) == 0:
        api_token.secret_key = bcrypt.gensalt()  # Generate Random Unique Secret_Key
    api_token.edit_date_in_token = api_token.edit_date.__str__()
    payload = {
        'app_name': api_token.app_name,
        'created_date': api_token.created_date.__str__(),
        'edit_date': api_token.edit_date_in_token,
        'expires': api_token.expires
    }
    if api_token.expires:
        if api_token.expire_date is not None:
            payload['expire_date'] = api_token.expire_date
    api_token.token = jwt.encode(payload, api_token.secret_key, algorithm='HS256')  # Generate Token
    api_token.save()


class TokensView(PermissionRequiredMixin, View):

    permission_required = 'auth_admin.manage_tokens'

    form = forms.APITokenForm
    template = 'auth/tokens.html'

    def build_context(self, form=None):
        if form is None:
            raise ValueError("Form can't be None")
        tokens = list(APIToken.objects.all())
        exist_tokens = tokens is not None and len(tokens) > 0
        return {
            'exist_tokens': exist_tokens,
            'tokens': tokens,
            'form': form,
            'show': {
                'app_name': True,
                'dates': True,
                'date_create': True,
                'date_edit': True,
                'date_expire': True,
                'secret': False,
                'token': True,
                'full_token': False,
                'edit': True,
                'delete': True,
                'regenerate_secret': True
            }
        }

    def get(self, request):
        empty_form = self.form()
        context = self.build_context(form=empty_form)
        return render(request, self.template, context)

    def post(self, request):
        form_response = self.form(request.POST)
        if form_response.is_valid():
            api_token = form_response.save(commit=False)
            update_api_token(api_token=api_token, regen_secret_key=True)
            # Update a second time to correct timestamp issue
            update_api_token(api_token=api_token, regen_secret_key=False)
        else:
            context = self.build_context(form=form_response)
            return render(request, self.template, context)
        return redirect('auth:tokens')


class TokenView(PermissionRequiredMixin, View):

    permission_required = 'auth_admin.read_tokens'

    template = 'auth/token.html'

    def build_context(self, api_token=None):
        if api_token is None:
            raise ValueError("API_Token can't be None")
        return {
            'app_name': api_token.app_name,
            'created_date': api_token.created_date.__str__(),
            'edit_date': api_token.edit_date.__str__(),
            'expires': api_token.expires,
            'expire_date': api_token.expire_date.__str__(),
            'secret_key': api_token.secret_key,
            'token': api_token.token
        }

    def get(self, request, app_name):
        if app_name is None:
            raise ValueError("App_Name can't be None")
        api_token = APIToken.objects.get(app_name=app_name)
        api_token_dict = self.build_context(api_token=api_token)
        return HttpResponse(json.dumps(api_token_dict), status=200, content_type="application/json")


class DeleteTokenView(PermissionRequiredMixin, View):

    permission_required = 'auth_admin.manage_tokens'

    def get(self, request, app_name):
        if app_name is None:
            raise ValueError("App_Name can't be None")
        api_token = APIToken.objects.get(app_name=app_name)
        api_token.delete()
        return redirect('auth:tokens')


class SecretTokenView(PermissionRequiredMixin, View):

    permission_required = 'auth_admin.manage_tokens'

    def get(self, request, app_name):
        if app_name is None:
            raise ValueError("App_Name can't be None")
        api_token = APIToken.objects.get(app_name=app_name)
        update_api_token(api_token=api_token, regen_secret_key=True)
        return redirect('auth:edit_token', app_name)


class EditTokenView(PermissionRequiredMixin, View):

    permission_required = 'auth_admin.manage_tokens'

    form = forms.APITokenForm
    template = 'auth/token_edit.html'

    def build_context(self, form=None):
        if form is None:
            raise ValueError("Form can't be None")
        return {
            'form': form
        }

    def get(self, request, app_name):
        api_token = APIToken.objects.get(app_name=app_name)
        token_form = self.form(instance=api_token)
        context = self.build_context(form=token_form)
        return render(request, self.template, context)

    def post(self, request, app_name):
        old_token = APIToken.objects.get(app_name=app_name)
        form_response = self.form(request.POST)
        form_response.instance = old_token
        if form_response.is_valid():
            api_token = form_response.save(commit=False)
            update_api_token(api_token=api_token, regen_secret_key=False)
        else:
            context = self.build_context(form=form_response)
            return render(request, self.template, context)
        return redirect('auth:tokens')
