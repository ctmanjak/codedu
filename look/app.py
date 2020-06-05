import os
import falcon.asgi

from look.db import init_db, insert_dummy_data, truncate_table, drop_db, create_db
from look.terminal import TerminalNamespace, init_socket
from look.api import auth, db, gql
from look.middleware.jsontranslator import JSONTranslator
from look.middleware.dbmanager import DBManager
from look.middleware.socketmanager import SocketManager
from look.schema import schema

db_session, engine = init_db()

middleware = [
    JSONTranslator(),
    DBManager(db_session, schema),
]

app = application = falcon.asgi.App(middleware=middleware)
socket, sio = init_socket(app)
sio.register_namespace(TerminalNamespace('/', sio))
app.add_middleware(SocketManager(sio))

app.req_options.strip_url_path_trailing_slash = True

class RootPage(object):
    async def on_get(self, req, res):
        res.body = "codedu"

    async def on_post(self, req, res):
        media = await req.get_media()
        for part in media:
            if part.name == 'image':
                if not os.path.isdir('images'): os.mkdir('images')
                with open(f'images/{part.filename}', 'wb') as dest:
                    part.stream.pipe(dest)

        res.body = "hi"


class TestPage(object):
    async def on_get(self, req, res):
        res.body = "HOSTNAME: " + os.environ.get('HOSTNAME', 'codedu')

class DBControl(object):
    async def on_get(self, req, res):
        create_db(engine)

    async def on_post(self, req, res):
        insert_dummy_data(db_session())

    async def on_delete(self, req, res):
        # truncate_table(db_session(), engine, table)
        drop_db(engine)

    async def on_put(self, req, res):
        await self.on_delete(req, res)
        await self.on_get(req, res)
        await self.on_post(req, res)

app.add_route('/', RootPage())
app.add_route('/test', TestPage())

app.add_route('/test/db', DBControl())

app.add_route('/api/auth/check', auth.Check())
app.add_route('/api/auth/register', auth.Register())
app.add_route('/api/auth/login', auth.Login())

app.add_route('/api/db/{table}', db.Collection())
app.add_route('/api/db/{table}/{id}', db.Item())

app.add_route('/api/graphql', gql.Collection(search=False))
app.add_route('/api/graphql/search', gql.Collection(search=True))