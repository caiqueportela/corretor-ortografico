from src.service.corrector_service import CorrectorService
from src.model.log_model import LogModel
import settings

LogModel.log('-------------------------------------------------')
#settings.init_settings()

word = 'lóigca'

corrector_service = CorrectorService()

corrector_service.prepare()

possible_words = corrector_service.corrector(word)

response = {
    'possible_words': possible_words,
    'original': word,
}

LogModel.log(response)

LogModel.log('-------------------------------------------------')