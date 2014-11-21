from flask import jsonify, request, abort, make_response
from functools import wraps

def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 401)


def authorized(fn):
    """Decorator that checks if there is an app id
    in the request the is valid, protecting our api
    from unauthorized access from other apps.
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        appid = request.args.get('app_id')
        if appid is None:
            # Unauthorized
            print("No app id in header")
            return unauthorized()
        print("Checking token...")
        if appid != "secret123":
            print("Check returned FAIL!")
            # Unauthorized
	    return unauthorized()

        return fn(*args, **kwargs)
    return wrapper

