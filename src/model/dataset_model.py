import os
import zipfile
import multiprocessing  as mp

from pandas import read_csv
import nltk
# nltk.download('punkt')

from src.model.log_model import LogModel
from src.service.redis_service import RedisService


def process(item):
    LogModel.log(f"process - {item['start']}~{item['end']}")
    return [nltk.tokenize.word_tokenize(token) for token in item['texts']]


class DatasetModel:

    def __init__(self):
        self.redis = RedisService()
        self.root_dir = os.path.abspath(os.curdir)
        self.dataset = []

    def prepare_dataset(self):
        LogModel.log('DatasetModel prepare_dataset Inicio')
        with zipfile.ZipFile(self.root_dir + '/data/articles.zip', 'r') as zip_ref:
            zip_ref.extractall('data')

        df = read_csv(self.root_dir + '/data/articles.csv', encoding='utf8')
        df = df[(df['date'] >= '2017-01-01') & (df['date'] <= '2017-12-31')]
        df = df.dropna(subset=['text']).iloc[:, [0, 1]]

        titles = df['title'].values.tolist()
        texts = df['text'].values.tolist()

        line_tokens = [nltk.tokenize.word_tokenize(token) for token in titles]

        items = []
        step = 5000
        for i in range(0, (len(texts) + step), step):
            LogModel.log(f"for - {i}~{(i+step)}")
            items.append({
                'texts': texts[i:(i+step)],
                'start': i,
                'end': (i+step),
            })

        with mp.Pool() as pool:
            line_tokens += pool.map(process, items)[0]

        # step = 10000
        # for i in range(0, (len(texts)+step), step):
        #     LogModel.log(f'Extract dataset range - {i}~{i+step}')
        #     line_tokens += [nltk.tokenize.word_tokenize(token) for token in texts[i:(i+step)]]

        tokens = []
        for line in line_tokens:
            tokens += line

        self.dataset = [token.lower() for token in tokens if token.isalpha()]

        LogModel.log('DatasetModel prepare_dataset Fim')
