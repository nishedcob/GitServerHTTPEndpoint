
from authApp.models import APIToken

import bcrypt
import jwt


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
