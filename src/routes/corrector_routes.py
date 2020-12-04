import logging
from flask import Blueprint, request, jsonify
from flask_cors import cross_origin

from src.service.corrector_service import CorrectorService
from src.model.log_model import LogModel


blueprint = Blueprint('corrector', __name__, url_prefix='/corrector')

@blueprint.route('/<word>', methods=['POST'])
@cross_origin()
def corrector(word):
    LogModel.log('blueprint corrector Inicio')
    try:
        if not word:
            err = {
                'message': 'Data was not sent',
            }
            return jsonify(err), 400

        data = request.json

        if data:
            use_probability = data['use_probability']
        else:
            use_probability = True

        corrector_service = CorrectorService()

        possible_words = corrector_service.corrector(word, use_probability)


        response = {
            'possible_words': possible_words,
            'original': word,
        }

        LogModel.log('blueprint corrector Fim')

        return jsonify(response)
    except Exception as e:
        logging.error('Error - corrector: ' + str(e))
        err = {
            'message': 'Internal server error',
        }
        return jsonify(err), 500

@blueprint.route('/turbo/<word>', methods=['POST'])
@cross_origin()
def corrector_turbo(word):
    LogModel.log('blueprint corrector_turbo Inicio')
    try:
        if not word:
            err = {
                'message': 'Data was not sent',
            }
            return jsonify(err), 400

        data = request.json

        if data:
            use_probability = data['use_probability']
        else:
            use_probability = True

        corrector_service = CorrectorService()

        possible_words = corrector_service.corrector_turbo(word, use_probability)

        response = {
            'possible_words': possible_words,
            'original': word,
        }

        LogModel.log('blueprint corrector_turbo Fim')

        return jsonify(response)
    except Exception as e:
        logging.error('Error - corrector_word: ' + str(e))
        err = {
            'message': 'Internal server error',
        }
        return jsonify(err), 500

@blueprint.route('/evaluator', methods=['POST'])
@cross_origin()
def evaluator():
    LogModel.log('blueprint evaluator Inicio')
    try:
        corrector_service = CorrectorService()

        corrector_service.evaluator()

        response = {
            'message': 'OK',
        }

        LogModel.log('blueprint evaluator Fim')

        return jsonify(response)
    except Exception as e:
        logging.error('Error - evaluator: ' + str(e))
        err = {
            'message': 'Internal server error',
        }
        return jsonify(err), 500

@blueprint.route('/evaluator/turbo', methods=['POST'])
@cross_origin()
def evaluator_turbo():
    LogModel.log('blueprint evaluator_turbo Inicio')
    try:
        corrector_service = CorrectorService()

        corrector_service.evaluator_turbo()

        response = {
            'message': 'OK',
        }

        LogModel.log('blueprint evaluator_turbo Fim')

        return jsonify(response)
    except Exception as e:
        logging.error('Error - evaluator_turbo: ' + str(e))
        err = {
            'message': 'Internal server error',
        }
        return jsonify(err), 500