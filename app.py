import flask

from src.routes.corrector_routes import blueprint as corrector
from src.service.corrector_service import CorrectorService


if __name__ == '__main__':

    app = flask.Flask(__name__)

    app.register_blueprint(corrector)

    corrector_model = CorrectorService()
    corrector_model.prepare()

    @app.errorhandler(404)
    def handle_404(err):
        response = {
            'message': str(err),
        }
        return flask.jsonify(response), 404

    app.run(debug=True, host='0.0.0.0', port=5001)