import graphene
from graphene_sqlalchemy import SQLAlchemyConnectionField
from . import account as account_schema
from . import auth as auth_schema
from . import book as book_schema


class Query(graphene.ObjectType):
    node = graphene.relay.Node.Field()
    account = graphene.relay.Node.Field(account_schema.Account)
    account_list = SQLAlchemyConnectionField(account_schema.Account)
    book = graphene.relay.Node.Field(book_schema.Book)
    book_list = SQLAlchemyConnectionField(book_schema.Book)
    book_search = graphene.Field(book_schema.BookSearchPayload, search=graphene.String(description="term to search"),
                                 resolver=book_schema.resolver_book_search)


class Mutation(graphene.ObjectType):
    create_account = account_schema.CreateAccount.Field()
    login = auth_schema.Login.Field()
    create_book = book_schema.CreateBook.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)