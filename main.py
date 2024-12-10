import tornado.ioloop
import tornado.web
import tornado.websocket
import asyncio
import redis.asyncio as redis  # Используем redis.asyncio вместо aioredis

REDIS_CHANNEL = "chat_room"

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("static/index.html")


class WebSocketHandler(tornado.websocket.WebSocketHandler):
    clients = set()

    async def open(self):
        self.clients.add(self)
        self.redis = redis.Redis(host='localhost', port=6379, decode_responses=True)
        asyncio.create_task(self.listen_to_redis())
        await self.write_message({"type": "info", "message": "Connected to chat"})

    async def on_message(self, message):
        # Publish message to Redis
        await self.redis.publish(REDIS_CHANNEL, message)

    async def listen_to_redis(self):
        pubsub = self.redis.pubsub()
        await pubsub.subscribe(REDIS_CHANNEL)
        async for message in pubsub.listen():
            if message['type'] == 'message':
                for client in self.clients:
                    if client is not self:
                        await client.write_message({"type": "message", "message": message['data']})

    def on_close(self):
        self.clients.remove(self)


def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/ws", WebSocketHandler),
        (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": "./static"}),  # Статические файлы
    ])


if __name__ == "__main__":
    app = make_app()
    app.listen(8888)  # Используем стандартный HTTP порт
    print("Server started at http://localhost:8888")
    tornado.ioloop.IOLoop.current().start()
