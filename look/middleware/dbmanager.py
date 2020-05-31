from traceback import print_exc

from falcon import HTTPBadRequest, HTTPInternalServerError

from sqlalchemy.exc import IntegrityError, OperationalError

class DBManager:
    def __init__(self, db_session, schema):
        self.db_session = db_session
        self.schema = schema

    async def process_resource(self, req, resp, resource, params):
        req.context['db_session'] = self.db_session()
        req.context['schema'] = self.schema
        
    async def process_response(self, req, resp, resource, req_succeeded):
        db_session = req.context.get('db_session', None)
        if db_session:
            if not req_succeeded:
                req.context['db_session'].rollback()
            else:
                try:
                    db_session.commit()
                except IntegrityError:
                    db_session.rollback()
                    raise HTTPBadRequest(description="INTEGRITY ERROR")
                except OperationalError:
                    db_session.rollback()
                    raise HTTPBadRequest(description="OPERATIONAL ERROR")
                except:
                    db_session.rollback()
                    print_exc()
                    raise HTTPInternalServerError(description="UNKNOWN ERROR")

            req.context['db_session'].close()