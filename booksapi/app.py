__author__ = 'josed18'

from flask import jsonify
from werkzeug.contrib.fixers import ProxyFix

from booksapi.api import app
app.wsgi_app = ProxyFix(app.wsgi_app)

from flask_graphql import GraphQLView
from booksapi.api.schema import schema

app.add_url_rule(
    '/graphql',
    view_func=GraphQLView.as_view('graphql',
                                  schema=schema,
                                  graphiql=True)
)

@app.route('/', methods=['GET'])
def run():
    return jsonify({
        'status': 'Online',
        'message': 'Books API - 2020'
    })

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=80)