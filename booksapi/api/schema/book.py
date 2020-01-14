import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType
from flask_graphql_auth import AuthInfoField, query_header_jwt_required, mutation_header_jwt_required
from booksapi.api.database.models import Book as BookModel
from booksapi.api.database.models import Author as AuthorModel
from booksapi.api.database.models import Category as CategoryModel
from booksapi.api.utils.decorators import AccountNoExist, extract_account_from_token_in_query, extract_account_from_token_in_mutation
from booksapi.api.services import googlebooks as googlebooks_services
from booksapi.api.services import book as book_services
from booksapi.api.utils.helper import input_to_dictionary
from .validator import Validate, InvalidValuesInput
from .utils import ObjectError


class BookAttributes:
    title = graphene.String(description="title of the book")
    sub_title = graphene.String(description="sub title of the book")
    publish_date = graphene.String(description="publish date of the book")
    publisher = graphene.String(description="publisher of the book")
    description = graphene.String(description="description of the book")


class Book(SQLAlchemyObjectType, BookAttributes):
    id = graphene.GlobalID(description="ID of the book")
    authors = graphene.List(lambda: Author, description="List of author of the book")
    categories = graphene.List(lambda: Category, description="List of categories of the book")

    def resolve_authors(self, info):
        return [a.author for a in self.authors]

    def resolve_categories(self, info):
        return [a.category for a in self.categories]

    class Meta:
        model = BookModel
        interfaces = (graphene.relay.Node,)


class Author(SQLAlchemyObjectType):
    id = graphene.GlobalID(description="ID of the author")
    name = graphene.String(description="name of the author")

    class Meta:
        model = AuthorModel
        interfaces = (graphene.relay.Node,)


class Category(SQLAlchemyObjectType):
    id = graphene.GlobalID(description="ID of the category")
    name = graphene.String(description="name of the category")

    class Meta:
        model = CategoryModel
        interfaces = (graphene.relay.Node,)


class ExternalBook(graphene.ObjectType, BookAttributes):
    external_id = graphene.String(description="ID of the book in the provider")
    authors = graphene.List(lambda: ExternalAuthor, description="List of author of the book")
    categories = graphene.List(lambda: ExternalCategory, description="List of categories of the book")
    provider = graphene.String(description="name of the book information provider")

    class Meta:
        model = BookModel
        interfaces = (graphene.relay.Node,)


class ExternalAuthor(graphene.ObjectType):
    name = graphene.String(description="name of the author")


class ExternalCategory(graphene.ObjectType):
    name = graphene.String(description="name of the category")


class BookResultPayload(graphene.Union):

    class Meta:
        types = (Book, ExternalBook)


class BookList(graphene.ObjectType):
    books = graphene.List(BookResultPayload)


class BookSearchPayload(graphene.Union):

    class Meta:
        types = (AuthInfoField, AccountNoExist, BookList)


@query_header_jwt_required
@extract_account_from_token_in_query
def resolver_book_search(parent, info, account, search):

    books = book_services.search_book(search)

    if len(books) > 0:
        return BookList(books=books)

    google_books = googlebooks_services.search_books(search)

    google_books = [ExternalBook(
        external_id=book.get('id'),
        provider="google",
        title=book.get('volumeInfo', {}).get("title"),
        sub_title=book.get('volumeInfo', {}).get("subtitle"),
        publish_date=book.get('volumeInfo', {}).get("publishedDate"),
        publisher=book.get('volumeInfo', {}).get("publisher"),
        description=book.get('volumeInfo', {}).get("description"),
        authors=[ExternalAuthor(name=author) for author in book.get('volumeInfo', {}).get("authors", [])],
        categories=[ExternalCategory(name=category) for category in book.get('volumeInfo', {}).get("categories", [])]
    ) for book in google_books.get('items', [])]

    return BookList(books=google_books)


class CreateBookSuccess(graphene.ObjectType):
    book = graphene.Field(lambda: Book, description="book created by this mutation")


class CreateBookError(graphene.ObjectType, ObjectError):
    pass


class CreateBookPayload(graphene.Union):

    class Meta:
        types = (AuthInfoField, AccountNoExist, InvalidValuesInput, CreateBookSuccess, CreateBookError)


class CreateBookInput(graphene.InputObjectType):
    external_id = graphene.String(description="id of the book in the external provider")
    provider = graphene.String(description="name of the book info provider")


class CreateBook(graphene.Mutation):

    response = graphene.Field(CreateBookPayload)

    class Arguments:
        input = CreateBookInput(required=True)
        
    @classmethod
    @mutation_header_jwt_required
    @extract_account_from_token_in_mutation
    def mutate(cls, self, info, account, input):
        data = input_to_dictionary(input)

        validations_schema = {
            'external_id': {'type': 'string', 'required': True, 'empty': False},
            'provider': {'type': 'string', 'required': True, 'allowed': ['google']}
        }

        validate = Validate(data, validations_schema)
        if validate.is_invalid:
            return cls(validate.error_node)

        book = None
        if data.get('provider') == "google":

            book_info = googlebooks_services.get_book(data.get('external_id'))
            if book_info is None:
                return cls(CreateBookError(
                    code="BOOK_NOT_FOUND",
                    message="not found a book with the external id provided"
                ))

            book = book_services.create_book_by_google_info(book_info)

        return cls(CreateBookSuccess(book))