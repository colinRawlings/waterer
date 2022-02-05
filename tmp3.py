import asyncio

import aiohttp.web


async def main():
    # add stuff to the loop, e.g. using asyncio.create_task()
    ...

    routes = aiohttp.web.RouteTableDef()

    @routes.get("/")
    async def hello(request):
        return aiohttp.web.Response(text="Hello, world")

    app = aiohttp.web.Application()
    app.add_routes(routes)

    runner = aiohttp.web.AppRunner(app)
    await runner.setup()
    site = aiohttp.web.TCPSite(runner, port=5000)
    await site.start()

    # add more stuff to the loop, if needed
    ...

    # wait forever
    await asyncio.Event().wait()


asyncio.run(main())
