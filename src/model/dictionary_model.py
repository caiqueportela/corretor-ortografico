import os
import zipfile
import xml.etree.ElementTree as ET

import nltk
# nltk.download('punkt')

from src.model.log_model import LogModel
from src.service.redis_service import RedisService


class DictionaryModel:

    def __init__(self):
        self.redis = RedisService()
        self.root_dir = os.path.abspath(os.curdir)
        self.known_words = []

    def prepare_dictionary_one(self):
        with zipfile.ZipFile(self.root_dir + '/data/xmls.zip', 'r') as zip_ref:
            zip_ref.extractall('data')

        dictionary_one_words = []

        for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            root = ET.parse(self.root_dir + '/data/xmls/' + letter + '.xml').getroot()

            for entry in root.findall('entry'):
                form = entry.find('form')
                orth = form.find('orth')
                word = orth.text.lower()
                dictionary_one_words.append(word)

        self.known_words += dictionary_one_words

    def prepare_dictionary_two(self):
        with open(self.root_dir + '/data/br-utf8.txt', 'r') as f:
            file_words = f.read()

        dictionary_two_words = []
        dictionary_two_words += [word.lower() for word in nltk.tokenize.word_tokenize(file_words)]

        self.known_words += dictionary_two_words

    def prepare_dictionary_three(self):
        dictionary_three_words = []

        with open(self.root_dir + '/data/pt_BR.dic', encoding='latin-1') as file:
            for i, line in enumerate(file):
                if i == 0:
                    continue
                line = line.lower()
                line = line.strip()
                line = line.split('/')[0]
                parts = line.split('-')
                if line:
                    dictionary_three_words.append(line)
                if len(parts) > 1:
                    for word in parts:
                        if word:
                            dictionary_three_words.append(word)

        self.known_words += dictionary_three_words

    def prepare_dictionary(self):
        LogModel.log('DictionaryModel prepare_dictionary Inicio')
        self.prepare_dictionary_one()
        self.prepare_dictionary_two()
        self.prepare_dictionary_three()
        LogModel.log('DictionaryModel prepare_dictionary Fim')

    def update_with_dataset(self, dataset):
        LogModel.log('DictionaryModel update_with_dataset Inicio')
        self.known_words += dataset
        print(f'words => {self.known_words[:10]}')
        print(f'dataset => {dataset[:10]}')
        self.known_words = set(self.known_words)
        LogModel.log('DictionaryModel update_with_dataset Fim')