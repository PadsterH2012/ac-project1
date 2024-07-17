from flask import jsonify
from werkzeug.exceptions import HTTPException

def register_error_handlers(app):
    @app.errorhandler(Exception)
    def handle_exception(e):
        # Pass through HTTP errors
        if isinstance(e, HTTPException):
            return e

        # Now handle non-HTTP exceptions
        app.logger.error(f"An error occurred: {str(e)}")
        return jsonify(error=str(e)), 500

    @app.errorhandler(404)
    def not_found(e):
        return jsonify(error=str(e)), 404

    @app.errorhandler(400)
    def bad_request(e):
        return jsonify(error=str(e)), 400
