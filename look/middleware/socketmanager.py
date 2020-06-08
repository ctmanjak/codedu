class SocketManager:
    def __init__(self, sio):
        self.sio = sio

    async def process_resource(self, req, resp, resource, params):
        req.context['sio'] = self.sio