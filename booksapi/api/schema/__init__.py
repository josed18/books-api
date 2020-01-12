import graphene
from graphene_sqlalchemy import SQLAlchemyConnectionField
from . import account as account_schema
from . import auth as auth_schema


class Query(graphene.ObjectType):
    node = graphene.relay.Node.Field()
    account = graphene.relay.Node.Field(account_schema.Account)
    account_list = SQLAlchemyConnectionField(account_schema.Account)


class Mutation(graphene.ObjectType):
    create_account = account_schema.CreateAccount.Field()
    login = auth_schema.Login.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)