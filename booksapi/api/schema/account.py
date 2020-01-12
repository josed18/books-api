import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType
from booksapi.api import db_session
from booksapi.api.database.models import Account as AccountModel
from booksapi.api.utils.helper import input_to_dictionary, encrypt_password
from booksapi.api.schema.validator import Validate, InvalidValuesInput
from booksapi.api.schema.utils import ObjectError


class AccountAttributes:
    email = graphene.String(description="email of the account")


class Account(SQLAlchemyObjectType, AccountAttributes):

    class Meta:
        model = AccountModel
        interfaces = (graphene.relay.Node,)
        only_fields = ("email",)


class CreateAccountSuccess(graphene.ObjectType):
    account = graphene.Field(lambda: Account, description="Account created by this mutation")


class CreateAccountError(graphene.ObjectType, ObjectError):
    pass


class CreateAccountPayload(graphene.Union):

    class Meta:
        types = (InvalidValuesInput, CreateAccountSuccess, CreateAccountError)


class CreateAccountInput(graphene.InputObjectType, AccountAttributes):
    password = graphene.String(description="password of the account")


class CreateAccount(graphene.Mutation):

    Output = CreateAccountPayload

    class Arguments:
        input = CreateAccountInput(required=True)

    def mutate(self, info, input):
        data = input_to_dictionary(input)

        validations_schema = {
            'email': {'type': 'string', 'required': True, 'regex': r"^(\w+[.|\w])*@(\w{2,}[.])*\w{2,}$"},
            'password': {'type': 'string', 'required': True, 'regex': r"^(?=.*?[a-zA-Z])(?=.*?[0-9]).*$", 'minlength': 8, 'maxlength': 50}
        }

        validate = Validate(data, validations_schema)
        if validate.is_invalid:
            return validate.error_node

        if AccountModel.query.filter_by(email=data.get('email')).first() is not None:
            return CreateAccountError(
                code="EMAIL_ALREADY_EXISTS",
                message="the email is already registered in the app"
            )

        data['password'] = encrypt_password(data.get('password'))

        account = AccountModel(**data)
        db_session.add(account)
        db_session.commit()

        return CreateAccountSuccess(account=account)

