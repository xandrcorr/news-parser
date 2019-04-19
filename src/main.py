import aiohttp 
from aiohttp import web
import asyncio
import traceback
from datetime import datetime
import json
import os

from infrastructure.parser import Parser
from infrastructure.repository import Repository

update_timeout = int(os.environ.get('POST_UPDATE_TIMEOUT', "3600"))
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
            limit = int(query_dict.get('limit', "5"))
            offset = int(query_dict.get('offset', "0"))
            sort = query_dict.get('order', "created_desc")
            sort_key, sort_order = tuple(i for i in sort.split('_'))
            output = await fetch_from_db(limit=limit,
                                         offset=offset,
                                         sort_key=sort_key,
                                         sort_order=sort_order)
        except:
            print(traceback.format_exc())
            # TODO: return error reason
            return web.Response(text="Bad request", status=400)
    return web.Response(text=json.dumps(output, indent=2), status=200)

async def fetch_from_db(limit, offset, sort_key, sort_order):
    return repo.get(limit=limit, 
                    offset=offset, 
                    sort_key=sort_key, 
                    sort_order=sort_order)

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
        await asyncio.sleep(update_timeout)


if __name__ == "__main__":
    app = web.Application()
    app.add_routes(routes)
    loop = asyncio.get_event_loop()
    tasks = [loop.create_task(main()), loop.create_task(web.run_app(app))]
    wait_tasks = asyncio.wait(tasks)
    loop.run_until_complete(wait_tasks)
    loop.close()