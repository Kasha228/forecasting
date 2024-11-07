from flask import Response 
from flask_restx import Namespace, Resource
from functools import wraps

api_namespace = Namespace('api')

def request_wrapper(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        try:
            # Assuming 'self' is the first argument for class methods
            if args and isinstance(args[0], Resource):
                self = args[0]
                response = func(self, *args[1:], **kwargs)
            else:
                response = func(*args, **kwargs)

            # Check if the response is already a Flask Response object
            if isinstance(response, Response):
                return response

            # If it's a tuple, assume it's (data, status_code, headers)
            if isinstance(response, tuple):
                data, status_code, headers = response
                return self.api.make_response(data, status_code, headers)

            # Otherwise, assume it's data to be serialized and return it with 200 OK
            return response, 200

        except ValueError as e:
            return {"error": str(e)}, 400

        except Exception as e:
            return {"error": str(e)}, 500

    return decorated_function