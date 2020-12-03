import redis

from src.model.log_model import LogModel


class RedisService:

    def __init__(self):
        self.redis = redis.Redis('redis', password='Redis2020@Corrector!', charset='utf-8', decode_responses=True)

    def init(self):
        self.redis.sadd('dictionary', *set(['python']))
        self.redis.lpush('dataset', 'python')

    def persist_dictionary(self, words):
        LogModel.log('RedisService persist_dictionary Inicio')
        self.redis.sadd('dictionary', *words)
        LogModel.log('RedisService persist_dictionary Fim')

    def persist_dataset(self, dataset):
        LogModel.log('RedisService persist_dataset Inicio')
        step = 10000
        for i in range(0, len(dataset), step):
            LogModel.log(f'Persist dataset range - {i}~{i+step}')
            self.redis.lpush('dataset', *dataset[i:(i+step)])
        LogModel.log('RedisService persist_dataset Fim')

    def dictionary_retrieve(self):
        LogModel.log('RedisService dictionary_retrieve Inicio')
        dictionary =  self.redis.smembers('dictionary')
        LogModel.log('RedisService dictionary_retrieve Fim')
        return dictionary

    def dataset_retrieve(self):
        LogModel.log('RedisService dataset_retrieve Inicio')
        dataset = self.redis.lrange('dataset', 0, -1)
        LogModel.log('RedisService dataset_retrieve Fim')
        return dataset

    def dataset_count(self):
        LogModel.log('RedisService dataset_count Inicio')
        dataset = self.redis.llen('dataset')
        LogModel.log(f'RedisService dataset_count {dataset} Fim')
        return dataset

    def dictionary_count(self):
        LogModel.log('RedisService dictionary_count Inicio')
        dictionary = self.redis.scard('dictionary')
        LogModel.log(f'RedisService dictionary_count {dictionary} Fim')
        return dictionary

    def dictionary_contains(self, value):
        LogModel.log('RedisService dictionary_contains Inicio')
        dictionary = self.redis.sismember('dictionary', value)
        LogModel.log(f'RedisService dictionary_contains({value}) Fim')
        return dictionary