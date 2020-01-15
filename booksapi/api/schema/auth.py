import graphene
from flask_graphql_auth import create_access_token
from .account import Account
from booksapi.api.utils.helper import input_to_dictionary, check_passwod
from booksapi.api.database.models import Account as AccountModel
from booksapi.api.schema.validator import Validate, InvalidValuesInput
from booksapi.api.schema.utils import ObjectError


class LoginInput(graphene.InputObjectType):
    email = graphene.String(description="email of the account to login")
    password = graphene.String(password="password of the account to login")


class LoginSuccess(graphene.ObjectType):
    access_token = graphene.String()
    account = graphene.Field(lambda: Account)


class LoginError(graphene.ObjectType, ObjectError):
    pass


class LoginPayload(graphene.Union):
    class Meta:
        types = (LoginSuccess, InvalidValuesInput, LoginError)


class Login(graphene.Mutation):
    """Login to use the app"""
    Output = LoginPayload

    class Arguments:
        input = LoginInput(required=True)

    def mutate(self, info, input):
        data = input_to_dictionary(input)

        validations_schema = {
            'email': {'type': 'string', 'required': True, 'regex': r"^(\w+[.|\w])*@(\w{2,}[.])*\w{2,}$"},
            'password': {'type': 'string', 'required': True, 'regex': r"^(?=.*?[a-zA-Z])(?=.*?[0-9]).*$", 'minlength': 8, 'maxlength': 50}
        }

        validate = Validate(data, validations_schema)
        if validate.is_invalid:
            return validate.error_node

        account = AccountModel.query.filter_by(email=data.get('email')).first()

        if account is None:
            return LoginError(
                code="EMAIL_NOT_FOUND",
                message="the email is not registered in the app"
            )

        if not check_passwod(account.password, data.get('password')):
            return LoginError(
                code="INCORRECT_DATA",
                message="user or email is incorrect"
            )

        account_info = {'email': account.email, 'id': account.id}
        return LoginSuccess(
            access_token=create_access_token(account_info),
            account=account
        )

