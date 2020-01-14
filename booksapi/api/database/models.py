from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP, Enum, Text, Boolean, DECIMAL
from sqlalchemy.orm import relationship

from booksapi.api import Base


class Account(Base):
    __tablename__ = "account"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(360), nullable=False)
    password = Column(String(100), nullable=True)


class Book(Base):
    __tablename__ = "book"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    sub_title = Column(String(200), nullable=True)
    publish_date = Column(String(10), nullable=True)
    publisher = Column(String(200), nullable=True)
    description = Column(Text)
    authors = relationship('BookAuthor', backref='book')
    categories = relationship('BookCategory', backref='book')


class BookAuthor(Base):
    __tablename__ = "book_author"

    id = Column(Integer, primary_key=True, autoincrement=True)
    book_id = Column(ForeignKey('book.id'), nullable=False)
    author_id = Column(ForeignKey('author.id'), nullable=False)


class Author(Base):
    __tablename__ = "author"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    books = relationship('BookAuthor', backref='author')


class BookCategory(Base):
    __tablename__ = "book_category"

    id = Column(Integer, primary_key=True, autoincrement=True)
    book_id = Column(ForeignKey('book.id'), nullable=False)
    category_id = Column(ForeignKey('category.id'), nullable=False)


class Category(Base):
    __tablename__ = "category"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    books = relationship('BookCategory', backref='category')
