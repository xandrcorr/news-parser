import aiohttp 
from aiohttp import web
import asyncio
import traceback
from datetime import datetime
import json
import os

from infrastructure import LoggerFactory
from infrastructure.errors import BadArgumentError
from infrastructure.parser import Parser
from infrastructure.repository import Repository

UPDATE_TIMEOUT = int(os.environ.get("POST_UPDATE_TIMEOUT", "3600"))
SERVER_PORT = int(os.environ.get("HTTP_SERVER_PORT", "8080"))

common_logger = LoggerFactory.create_logger("Main")
repo = Repository()
routes = web.RouteTableDef()


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
            limit, offset, sort_key, sort_order = parse_query_arguments(request.query_string)
            output = await fetch_from_db(limit=limit,
                                         offset=offset,
                                         sort_key=sort_key,
                                         sort_order=sort_order)
        except Exception as e:
            common_logger.error(traceback.format_exc())
            # TODO: return error reason
            if type(e) is BadArgumentError:
                err_dict = {
                    "errors": [err for err in e.args]
                }
                return web.Response(text=json.dumps(err_dict, indent=2), status=400)
            else:
                return web.Response(status=500)
            # return web.Response(text="Bad request", status=400)
    return web.Response(text=json.dumps(output, indent=2), status=200)

def parse_query_arguments(query_str):
    try:
        query_dict = { query.split('=')[0]: query.split('=')[1] 
                    for query in query_str.split('&') 
                    }
        limit = int(query_dict.get('limit', "5"))
        offset = int(query_dict.get('offset', "0"))
        sort = query_dict.get('order', "created_desc")
        sort_key, sort_order = tuple(i for i in sort.split('_'))
        return (limit, offset, sort_key, sort_order)
    except:
        raise BadArgumentError("One or more arguments are invalid.")

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
        try:
            common_logger.info("Trying to get new posts from https://news.ycombinator.com/news")
            async with aiohttp.ClientSession() as session:
                raw_html = await fetch(session, 'https://news.ycombinator.com/news')
                news = Parser.parse_news(raw_html)
                added = repo.add_many(news)
                common_logger.info("Added {0} posts".format(added))
        except:
            common_logger.error(traceback.format_exc())
        finally:
            # check for a new articles every 1 hour
            await asyncio.sleep(UPDATE_TIMEOUT)


if __name__ == "__main__":
    app = web.Application()
    app.add_routes(routes)
    loop = asyncio.get_event_loop()
    tasks = [loop.create_task(main()), loop.create_task(web.run_app(app=app, port=SERVER_PORT))]
    wait_tasks = asyncio.wait(tasks)
    loop.run_until_complete(wait_tasks)
    loop.close()