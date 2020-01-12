__author__ = 'josed18'
import logging

from flask import Flask
from flask_caching import Cache
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from threading import Thread
from flask_graphql_auth import GraphQLAuth

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
app = Flask(__name__)
app.config.from_pyfile('../settings.cfg')
app.cache = Cache(app)

auth = GraphQLAuth(app)

db = SQLAlchemy(app)
engine = db.get_engine(app)
db_session = scoped_session(sessionmaker(bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


def make_async(f):
    def wrapper(*args, **kwargs):
        thr = Thread(target=f, args=args, kwargs=kwargs)
        thr.start()
    return wrapper