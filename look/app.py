import falcon.asgi

from look.db import init_db, insert_dummy_data
from look.socket import TerminalNamespace, init_socket
from look.api import auth, db
from look.middleware.jsontranslator import JSONTranslator
from look.middleware.dbmanager import DBManager
from look.middleware.socketmanager import SocketManager

db_session = init_db()
# insert_dummy_data(db_session())
middleware = [
    JSONTranslator(),
    DBManager(db_session),
]

app = application = falcon.asgi.App(middleware=middleware)
socket, sio = init_socket(app)
sio.register_namespace(TerminalNamespace('/', sio))
app.add_middleware(SocketManager(sio))

class RootPage(object):
    async def on_get(self, req, res):
        res.body = "Hello, World!"

app.add_route('/', RootPage())

app.add_route('/api/auth/check', auth.Check())
app.add_route('/api/auth/register', auth.Register())
app.add_route('/api/auth/login', auth.Login())

app.add_route('/api/{table}', db.Collection())
app.add_route('/api/{table}/{id}', db.Item())