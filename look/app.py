import os
import falcon
import falcon.asgi

from look.db import init_db, insert_dummy_data, truncate_table, drop_db, create_db
from look.api import auth, db, gql
from look.middleware.requestdatamanager import RequetDataManager
from look.middleware.dbmanager import DBManager
from look.middleware.socketmanager import SocketManager
from look.schema import schema

from falcon import media
from falcon.media import MultipartFormHandler
from falcon.media.multipart import MultipartParseOptions

db_session, engine = init_db()

parse_options = MultipartParseOptions()
parse_options.max_body_part_buffer_size = 3 * 1024 * 1024
handlers = media.Handlers({
    'multipart/form-data': MultipartFormHandler(parse_options=parse_options),
})


middleware = [
    RequetDataManager(),
    DBManager(db_session, schema),
]

app = application = falcon.asgi.App(middleware=middleware)

app.req_options.strip_url_path_trailing_slash = True
app.req_options.media_handlers.update(handlers)
app.resp_options.media_handlers.update(handlers)

class RootPage(object):
    async def on_get(self, req, res):
        res.body = "codedu"

    async def on_post(self, req, res):
        media = await req.get_media()
        if media:
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

app.add_route('/api/graphql', gql.Collection())