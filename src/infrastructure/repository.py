from datetime import datetime
import os
import traceback

import pymongo

from infrastructure import LoggerFactory
from infrastructure.errors import BadArgumentError

class Repository:
    def __init__(self, host=None, port=None, database=None):
        host = host or os.environ.get("REPOSITORY_HOST", "localhost")
        port = port or int(os.environ.get("REPOSITORY_PORT", "27017"))
        self.__client = pymongo.MongoClient(host=host,
                                    port=port)
        database = database or os.environ.get("REPOSITORY_DB", "news_storage")
        self.__db = self.__client.get_database(name=database)
        self.__collection = self.__db.news
        # creating unique index for url field to avoid duplicate news
        self.__collection.create_index('url', unique=True)
        self.__sort_order = ['asc', 'desc']
        self.__sort_keys = ['title', 'url', 'created']
        self.__logger = LoggerFactory.create_logger(self.__class__.__name__)
        self.__logger.info("Repository initiated on {0}:{1}".format(host, port))

    def add(self, item: dict):
        try:
            self.__collection.insert_one(item)
        except pymongo.errors.DuplicateKeyError:
            self.__logger.error("Can't add duplicate item to collection.")
            raise

    def add_many(self, items: [dict]):
        # Inserting one-by-one for handling duplicate news
        add_cntr = 0
        for item in items:
            try:
                self.add(item)
                add_cntr += 1
            except pymongo.errors.DuplicateKeyError:
                continue
        return add_cntr

    def get(self, limit: int = 5,
            offset: int = 0, 
            sort_key: str = "created", 
            sort_order: str = "desc") -> []:
        # TODO: write more tests for this method
        try:
            stats = self.__db.command('collstats', 'news')
            if limit < 1 or limit > stats['count']:
                # TODO: raise proper exception for limit
                raise BadArgumentError("Limit argument is too big or too low.")
            if offset < 0 or offset + limit > stats['count']:
                # TODO: raise proper exception for offset
                raise BadArgumentError("Offset argument is too big or too low.")
            if sort_order in self.__sort_order and sort_key in self.__sort_keys:
                sort=[(sort_key, pymongo.DESCENDING if sort_order=="desc" else pymongo.ASCENDING)]
            else:
                # TODO: raise proper exception for sort
                raise BadArgumentError("Invalid order argument.")
            output = []
            cursor = self.__collection.find(skip=offset, limit=limit, sort=sort)
            for item in cursor:
                output.append({
                    "id": str(item['_id']),
                    "title": item['title'],
                    "url": item['url'],
                    "created": datetime.utcfromtimestamp(item['created']).isoformat()
                })
            return output
        except:
            self.__logger.error(traceback.format_exc())
            raise

    def clean_db(self):
        self.__logger.warning("Dropping collection {0}".format(self.__collection.name))
        self.__collection.drop()
