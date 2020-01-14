from sqlalchemy import or_
from booksapi.api import db_session
from booksapi.api.database.models import Book as BookModel
from booksapi.api.database.models import BookAuthor as BookAuthorModel
from booksapi.api.database.models import BookCategory as BookCategoryModel
from booksapi.api.database.models import Author as AuthorModel
from booksapi.api.database.models import Category as CategoryModel


def search_book(search_term):
    search_term = f"%{search_term}%"
    return db_session.query(BookModel).outerjoin(BookCategoryModel).outerjoin(CategoryModel)\
        .outerjoin(BookAuthorModel).outerjoin(AuthorModel).filter(or_(
            BookModel.title.like(search_term),
            BookModel.sub_title.like(search_term),
            BookModel.description.like(search_term),
            BookModel.publisher.like(search_term),
            BookModel.publish_date.like(search_term),
            CategoryModel.name.like(search_term),
            AuthorModel.name.like(search_term),
        )).all()


def add_authors_to_book(book, authors_names):
    for author_name in authors_names:
        author = AuthorModel.query.filter_by(name=author_name).first()
        if author is None:
            author = AuthorModel(name=author_name)
            db_session.add(author)
            db_session.flush()

        book_author = BookAuthorModel(
            book_id=book.id,
            author_id=author.id
        )
        db_session.add(book_author)
        db_session.flush()


def add_categories_to_book(book, categories_names):
    for category_name in categories_names:
        category = CategoryModel.query.filter_by(name=category_name).first()
        if category is None:
            category = CategoryModel(name=category_name)
            db_session.add(category)
            db_session.flush()

        book_categories = BookCategoryModel(
            book_id=book.id,
            category_id=category.id
        )
        db_session.add(book_categories)
        db_session.flush()


def create_book_by_google_info(book_info):
    book = BookModel(
        title=book_info.get('volumeInfo', {}).get("title"),
        sub_title=book_info.get('volumeInfo', {}).get("subtitle"),
        publish_date=book_info.get('volumeInfo', {}).get("publishedDate"),
        publisher=book_info.get('volumeInfo', {}).get("publisher"),
        description=book_info.get('volumeInfo', {}).get("description")
    )
    db_session.add(book)
    db_session.flush()

    add_authors_to_book(book, book_info.get('volumeInfo', {}).get("authors", []))
    add_categories_to_book(book, book_info.get('volumeInfo', {}).get("categories", []))

    db_session.commit()

    return book
