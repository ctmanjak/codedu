class DBManager:
    def __init__(self, db_session):
        self.db_session = db_session

    async def process_resource(self, req, resp, resource, params):
        if req.method == 'OPTIONS':
            return
        req.context['db_session'] = self.db_session()
        
    async def process_response(self, req, resp, resource, req_succeeded):
        if req.method == 'OPTIONS':
            return
        if req.context.get('db_session'):
            if not req_succeeded:
                req.context['db_session'].rollback()
            req.context['db_session'].close()