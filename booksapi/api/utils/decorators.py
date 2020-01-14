from functools import wraps
from booksapi.api.database.models import Account
from flask_graphql_auth import get_jwt_identity
import graphene


class AccountNoExist(graphene.ObjectType):

    message = graphene.String(description="message with description of the error")


def extract_account_from_token_in_mutation(fn):
    @wraps(fn)
    def wrapper(cls, *args, **kwargs):
        user_info = get_jwt_identity()
        account = Account.query.get(user_info.get('id'))
        if account is None:
            return cls(AccountNoExist(message="the account no exist in the app"))

        kwargs['account'] = account

        return fn(cls, *args, **kwargs)

    return wrapper


def extract_account_from_token_in_query(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user_info = get_jwt_identity()
        account = Account.query.get(user_info.get('id'))
        if account is None:
            return AccountNoExist(message="the account no exist in the app")

        kwargs['account'] = account

        return fn(*args, **kwargs)

    return wrapper