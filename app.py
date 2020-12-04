import flask
from flask_cors import CORS, cross_origin

from src.routes.corrector_routes import blueprint as corrector
from src.service.corrector_service import CorrectorService


if __name__ == '__main__':

    app = flask.Flask(__name__)

    CORS(app)
    app.config['CORS_HEADERS'] = 'Content-Type'

    app.register_blueprint(corrector)

    corrector_model = CorrectorService()
    corrector_model.prepare()

    @app.errorhandler(404)
    @cross_origin()
    def handle_404(err):
        response = {
            'message': str(err),
        }
        return flask.jsonify(response), 404

    app.run(debug=True, host='0.0.0.0', port=5001)