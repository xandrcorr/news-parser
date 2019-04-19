import aiohttp 
from aiohttp import web
import asyncio
import traceback
from datetime import datetime

from infrastructure.parser import Parser
from infrastructure.repository import Repository

routes = web.RouteTableDef()
repo = Repository()

@routes.get('/')
async def index_handler(request):
    print("index")
    pass

@routes.get('/posts')
async def posts_handler(request):
    if request.query_string == '':
        output = repo.get()
    else:
        try:
            query_dict = { query.split('=')[0]: query.split('=')[1] 
                        for query in request.query_string.split('&') 
                        }
            # TODO: handle in more pretty way if possible, especially sort direction
            limit = int(query_dict.get('limit', "5"))
            offset = int(query_dict.get('offset', "0"))
            sort_key = query_dict.get('order', "created")
            sort_desc = query_dict.get('direction', "desc") == "desc"
            output = repo.get(limit=limit, 
                            offset=offset, 
                            sort_key=sort_key, 
                            sort_desc=sort_desc)
        except:
            print(traceback.format_exc())
            return web.Response(status=400)
    return web.Response(text=str(output), status=200)

async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()

async def main():
    while True:
        async with aiohttp.ClientSession() as session:
            raw_html = await fetch(session, 'https://news.ycombinator.com/news')
            news = Parser.parse_news(raw_html)
            added = repo.add_many(news)
            t = datetime.utcnow().isoformat()
            print("[{0}] Added {1} news".format(t, added))
        # check for a new articles every 1 hour
        await asyncio.sleep(3600)


if __name__ == "__main__":
    app = web.Application()
    app.add_routes(routes)
    loop = asyncio.get_event_loop()
    tasks = [loop.create_task(main()), loop.create_task(web.run_app(app))]
    wait_tasks = asyncio.wait(tasks)
    loop.run_until_complete(wait_tasks)
    loop.close()