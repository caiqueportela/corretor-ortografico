import os

import nltk
# nltk.download('punkt')

from src.model.dataset_model import DatasetModel
from src.model.dictionary_model import DictionaryModel
from src.model.log_model import LogModel
from src.service.redis_service import RedisService


class CorrectorService:

    def __init__(self):
        LogModel.log('CorrectorService __init__ Inicio')
        self.redis = RedisService()
        self.dictionary_model = DictionaryModel()
        self.dataset_model = DatasetModel()
        self.words = 'abcdefghijklmnopqrstuvwxyzàáâãèéêìíîòóôõùúûç'

        self.root_dir = os.path.abspath(os.curdir)

        dataset = self.redis.dataset_retrieve()
        self.frequency = nltk.FreqDist(dataset)
        self.count_dataset_words = self.redis.dataset_count()
        LogModel.log('CorrectorService __init__ Fim')

    def prepare(self):
        LogModel.log('CorrectorService prepare Inicio')
        if self.redis.dictionary_count() > 0:
            return

        self.redis.init()

        self.dictionary_model.prepare_dictionary()
        LogModel.log(f'dictionary: {len(self.dictionary_model.known_words)}')

        self.dataset_model.prepare_dataset()

        self.dictionary_model.update_with_dataset(self.dataset_model.dataset)
        self.redis.persist_dictionary(self.dictionary_model.known_words)
        self.redis.persist_dataset(self.dataset_model.dataset)
        LogModel.log('CorrectorService prepare Fim')

    def slice_word(self, word):
        return [(word[:i], word[i:]) for i in range(len(word) + 1)]

    def insert_letter(self, slices):
        new_words = []
        for L, R in slices:
            for word in self.words:
                new_words.append(L + word + R)
        return new_words

    def delete_letter(self, slices):
        new_words = []
        for L, R in slices:
            new_words.append(L + R[1:])
        return new_words

    def reverse_letter(self, slices):
        new_words = []
        for L, R in slices:
            if len(R) >= 2:
                new_words.append(L + R[1] + R[0] + R[2:])
        return new_words

    def change_letter(self, slices):
        new_words = []
        for L, R in slices:
            for word in self.words:
                new_words.append(L + word + R[1:])
        return new_words

    def delete_two_letters(self, slices):
        new_slices = []
        new_words = self.delete_letter(slices)
        for word in new_words:
            new_slices += self.slice_word(word)
        deleted_letter = self.delete_letter(new_slices)
        return deleted_letter

    def remove_change_letter(self, slices):
        new_slices = []
        new_words = self.delete_letter(slices)
        for word in new_words:
            new_slices += self.slice_word(word)
        changed_letters = self.change_letter(new_slices)
        return changed_letters

    def change_two_letters(self, slices):
        new_slices = []
        new_words = self.change_letter(slices)
        for word in new_words:
            new_slices += self.slice_word(word)
        changed_letter = self.change_letter(new_slices)
        return changed_letter

    def generate_words(self, word):
        LogModel.log(f'CorrectorService generate_words({word}) Inicio')
        slices = self.slice_word(word)
        generated_words = []
        generated_words += self.insert_letter(slices)
        generated_words += self.delete_letter(slices)
        generated_words += self.reverse_letter(slices)
        generated_words += self.change_letter(slices)
        generated_words += self.remove_change_letter(slices)
        generated_words += self.delete_two_letters(slices)
        generated_words += self.change_two_letters(slices)
        LogModel.log(f'CorrectorService generate_words({word}) Fim')
        return generated_words

    def probability(self, generated_word):
        return self.frequency[generated_word] / self.count_dataset_words

    def corrector(self, word, use_probability=True):
        LogModel.log(f'CorrectorService corrector({word}) Inicio')
        generated_words = self.generate_words(word)
        LogModel.log(f'generated_words => {len(generated_words)}')

        if use_probability:
            LogModel.log(f'count_dataset_words => {self.count_dataset_words}')
            LogModel.log(f'{word} in know_words = {self.redis.dictionary_contains(word)}')
            return max(generated_words, key=self.probability)

        possible_words = [word for word in generated_words if self.redis.dictionary_contains(word)]
        LogModel.log(f'CorrectorService corrector({word}) Fim')
        return possible_words

    def ocurrency_percentage(self, words):
        word = None
        frequency = 0
        for w in words:
            p = self.probability(w)
            if frequency == 0 or p > frequency:
                frequency = p
                word = w

        return word, frequency

    def corrector_turbo(self, word, use_probability=True):
        methods = [
            'insert_letter',
            'delete_letter',
            'reverse_letter',
            'change_letter',
            'remove_change_letter',
            'change_two_letters',
            'delete_two_letters',
        ]
        slices = self.slice_word(word)
        generated_words = []
        min_percent = 3 * 10 ** -5

        for method_name in methods:
            result = getattr(self, method_name)(slices)

            if use_probability:
                occurrence = self.ocurrency_percentage(result)
                if occurrence[1] >= min_percent:
                    return occurrence[0]
                generated_words += result

            possible_words = [word for word in generated_words if self.redis.dictionary_contains(word)]
            return possible_words

    def evaluator(self, use_probability=True, debug=False):
        test_data = []

        f = open(self.root_dir + '/data/palavras.txt', 'r')
        for line in f:
            correct, wrong = line.split()
            test_data.append((correct, wrong))
        f.close()

        count_words = len(test_data)
        hit = 0
        unknown = 0
        for correct, wrong in test_data:
            possible_words = self.corrector(wrong, use_probability)
            unknown += (not self.redis.dictionary_contains(correct.tolower()))
            if correct in possible_words:
                hit += 1
                if debug:
                    LogModel.log(f'Correta: {correct}, errada: {wrong}, geradas: {possible_words}')
            else:
                LogModel.log(f'Incorreto: {correct}, errada: {wrong}, geradas: {possible_words}')
        hit_rate = round((hit * 100) / count_words, 2)
        unknown_rate = round((unknown * 100) / count_words, 2)
        LogModel.log(f'Taxa de acerto: {hit_rate}% de {count_words}, com taxa de desconhecimento: {unknown_rate}%')

    def evaluator_turbo(self):
        test_data = []

        f = open(self.root_dir + '/data/palavras.txt', 'r')
        for line in f:
            correct, wrong = line.split()
            test_data.append((correct, wrong))
        f.close()

        count_words = len(test_data)
        hit = 0
        unknown = 0
        for correct, wrong in test_data:
            possible_words = self.corrector_turbo(wrong)
            unknown += (not self.redis.dictionary_contains(correct.tolower()))
            if correct in possible_words:
                hit += 1
            else:
                LogModel.log(f'Correta: {correct}, errada: {wrong}, geradas: {possible_words}')
        hit_rate = round((hit * 100) / count_words, 2)
        unknown_rate = round((unknown * 100) / count_words, 2)
        LogModel.log(f'Taxa de acerto: {hit_rate}% de {count_words}, com taxa de desconhecimento: {unknown_rate}%')