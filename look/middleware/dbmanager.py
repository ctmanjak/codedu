from traceback import print_exc

from falcon import HTTPBadRequest, HTTPInternalServerError

from sqlalchemy.exc import IntegrityError, OperationalError

class DBManager:
    def __init__(self, db_session, schema):
        self.db_session = db_session
        self.schema = schema

    async def process_resource(self, req, res, resource, params):
        req.context['db_session'] = self.db_session()
        req.context['schema'] = self.schema
        
    async def process_response(self, req, res, resource, req_succeeded):
        db_session = req.context.get('db_session', None)
        if db_session:
            if not req_succeeded:
                db_session.rollback()
            else:
                try:
                    db_session.commit()
                except IntegrityError:
                    db_session.rollback()
                    raise HTTPBadRequest(description="INTEGRITY ERROR")
                except OperationalError:
                    db_session.rollback()
                    print_exc()
                    raise HTTPBadRequest(description="OPERATIONAL ERROR")
                except:
                    db_session.rollback()
                    print_exc()
                    raise HTTPInternalServerError(description="UNKNOWN ERROR")
                else:
                    pass
                    # image_info = req.context.get('image_info', None)
                    # image_info['name'] = f"{instance.id:010}"
                    # with open(f"images/{image_info['dir']}{image_info['name']}{image_info['ext']}", 'wb') as f:
                    #     f.write(image_info['data'])
                    # instance.user_img = f"{image_info['dir']}{image_info['name']}{image_info['ext']}"

            db_session.close()