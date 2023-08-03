from aiohttp import web

# This is the route table that will be used by Quart
routes = web.RouteTableDef()

# This is the route that will be called by the client
@routes.get("/", allow_head=True)
async def root_route_handler(request):
    return web.Response(text="Hello World")

# This is the function that will be called automatically by Quart
async def web_server():
    web_app = web.Application(client_max_size=30000000)
    web_app.add_routes(routes)
    return web_app