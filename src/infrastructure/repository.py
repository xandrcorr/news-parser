from datetime import datetime
import os
import traceback

import pymongo

class Repository:
    def __init__(self, host=None, port=None):
        host = host or os.environ.get("REPOSITORY_HOST", "localhost")
        port = port or int(os.environ.get("REPOSITORY_PORT", "27017"))
        self.__client = pymongo.MongoClient(host=host,
                                    port=port)
        self.__db = self.__client.news_storage
        self.__collection = self.__db.news
        # creating unique index for url field to avoid duplicate news
        self.__collection.create_index('url', unique=True)

    def add(self, item: dict):
        try:
            self.__collection.insert_one(item)
        except pymongo.errors.DuplicateKeyError:
            # TODO: add logger
            print("Failed to add duplicate key")
            raise

    def add_many(self, items):
        # Inserting one-by-one for handling duplicate news
        add_cntr = 0
        for item in items:
            try:
                self.add(item)
                add_cntr += 1
            except pymongo.errors.DuplicateKeyError:
                continue
        return add_cntr

    def get(self, limit=5, offset=0, sort_key="created", sort_desc=True) -> []:
        # TODO: write more tests for this method
        try:
            stats = self.__db.command('collstats', 'news')
            if limit < 1 or limit > stats['count']:
                # TODO: raise proper exception for limit
                raise Exception
            if offset < 0 or offset + limit > stats['count']:
                # TODO: raise proper exception for offset
                raise Exception
            output = []
            sort=[(sort_key, pymongo.DESCENDING if sort_desc else pymongo.ASCENDING)]
            cursor = self.__collection.find(skip=offset, limit=limit, sort=sort)
            for n, item in enumerate(cursor):
                output.append({
                    "id": n+1,
                    "title": item['title'],
                    "url": item['url'],
                    "created": datetime.utcfromtimestamp(item['created']).isoformat()
                })
            return output
        except:
            print(traceback.format_exc())
            raise