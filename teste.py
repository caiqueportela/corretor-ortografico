import redis
import nltk
nltk.download('punkt')

r = redis.Redis('localhost', password='Redis2020@Corrector!', charset="utf-8", decode_responses=True)

print(f"dataset: {r.llen('dataset')}")
print(f"dictionary: {r.scard('dictionary')}")