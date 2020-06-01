import json
from hashlib import sha256

from look.hook.authmanager import validate_token
from look.model import Base

from falcon import HTTP_200, before, HTTPBadRequest, HTTPInternalServerError
from falcon.uri import parse_query_string

from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.orm.exc import NoResultFound

async def find_model(self, table, col_list=None):
    result = {
        "success" : False,
        "description" : "",
        "data" : {},
    }

    self.model = Base._decl_class_registry.get(table[0].upper()+table[1:], None)
    
    if self.model:
        if not col_list == None:
            if not col_list:
                self.attrs = self.model.__table__.columns.keys()
                for relationship in self.model.__mapper__.relationships.keys():
                    self.attrs.append(relationship)
            else:
                self.attrs = col_list
        result["success"] = True
    else: result["description"] = "TABLE NOT FOUND"

    return result


class Collection(object):
    async def insert_data(self, db_session, table, data):
        result = await find_model(self, table)
        
        if result["success"]:
            if 'password' in data: data['password'] = sha256(data['password'].encode()).hexdigest()
            print(self.model.__tablename__, data)
            if data:
                try:
                    db_session.add(self.model(**data))
                except TypeError as e:
                    result["success"] = False
                    result["description"] = "INVALID PARAMETER"
            else:
                result["success"] = False
                result["description"] = "DATA NOT FOUND"
            
        return result

    async def select_data(self, db_session, table, col_list=[], depth=0, print_parent=False):
        result = await find_model(self, table, col_list)

        if result["success"]:
            db_data = db_session.query(self.model).all()

            if db_data:
                result["data"] = [row.get_data(self.attrs, depth=depth, print_parent=print_parent) for row in db_data]
            else:
                result["success"] = False
                result["description"] = "NO RESULT FOUND"

        return result
    
    async def on_post(self, req, res, table):
        data = req.context['data']
        db_session = req.context['db_session']
        result = await self.insert_data(db_session, table, data)
        if result and "success" in result:
            if result["success"]:
                res.status = HTTP_200
                res.body = json.dumps(result)
            else: raise HTTPBadRequest(description=result["description"])
        else: raise HTTPInternalServerError()

    @before(validate_token, is_async=True)
    async def on_get(self, req, res, table):
        db_session = req.context['db_session']
        depth = 0
        print_parent = False

        if req.query_string:
            query = parse_query_string(req.query_string)
            if 'depth' in query:
                try:
                    depth = int(query['depth'])
                except ValueError:
                    pass
            if 'print_parent' in query:
                print_parent = True

        result = await self.select_data(db_session, table, depth=depth, print_parent=print_parent)

        if result and "success" in result:
            if result["success"]:
                res.status = HTTP_200
                res.body = json.dumps(result)
            else: raise HTTPBadRequest(description=result["description"])
        else: raise HTTPInternalServerError()

class Item(object):
    async def select_data(self, db_session, table, id_, col_list=[], depth=0):
        result = await find_model(self, table, col_list)

        if result["success"]:
            try:
                db_data = db_session.query(self.model).filter(self.model.id == id_).one()
            except NoResultFound:
                result["success"] = False
                result["description"] = "NO RESULT FOUND"
            except:
                result["success"] = False
                result["description"] = "UNKNOWN ERROR"
            else:
                result["data"] = db_data.get_data(self.attrs, depth=depth)
        
        return result

    @before(validate_token, is_async=True)
    async def on_get(self, req, res, table, id_):
        db_session = req.context['db_session']
        depth = 0

        if req.query_string:
            query = parse_query_string(req.query_string)

            if 'depth' in query:
                try:
                    depth = int(query['depth'])
                except ValueError:
                    pass

        result = await self.select_data(db_session, table, id_, depth=depth)

        if result and "success" in result:
            if result["success"]:
                res.status = HTTP_200
                res.body = json.dumps(result)
            else: raise HTTPBadRequest(description=result["description"])
        else: raise HTTPInternalServerError()