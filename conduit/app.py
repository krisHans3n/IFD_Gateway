import flask
import sys
import logging
import json
import uuid
from conduit.settings import ProdConfig, DevConfig, create_redis_connection
from flask import Flask, request, jsonify, session
from functools import wraps
from network.Dispatch import *
from source.ImageParser import ImageParser
from rq import Queue

logging.basicConfig(level=logging.DEBUG)


def required_params(required):
    def decorator(fn):

        @wraps(fn)
        def wrapper(*args, **kwargs):
            print(request.get_json())
            _json = request.get_json()
            missing = [r for r in required.keys()
                       if r not in _json]
            print(missing, _json)
            if missing:
                response = {
                    "status": "error",
                    "message": "Request JSON is missing some required params",
                    "missing": missing
                }
                return jsonify(response), 400
            wrong_types = [r for r in required.keys()
                           if not isinstance(_json[r], required[r])]
            if wrong_types:
                response = {
                    "status": "error",
                    "message": "Data types in the request JSON do not match the required format",
                    "param_types": {k: str(v) for k, v in required.items()}
                }
                return jsonify(response), 400
            return fn(*args, **kwargs)

        return wrapper

    return decorator


def create_app(config_object=DevConfig):
    app = Flask(__name__)
    app.url_map.strict_slashes = False
    app.config.from_object(config_object)

    q = None

    try:
        q = Queue(connection=create_redis_connection())
    except Exception as ex:
        print('problem establishing queue ', ex)

    # TODO: routes will be expanded on

    @app.route('/full_analysis/', methods=['POST', 'GET'])
    @required_params({"urls": list})
    def respond():

        urls = request.get_json()

        redis_ids = [None, str(uuid.uuid4())]  # IDs for where to find JSON responses
        _report = {}
        result_response = {}

        job = None

        if urls is None or len(urls) == 0:
            result_response["Error"] = "no urls were provided"
        elif urls is not None:
            job = q.enqueue_call(
                func=send_to_passive_analysis,
                args=(request.get_json(), redis_ids[1]),
                result_ttl=1800,
                job_id=redis_ids[1]
            )

        if job is not None:
            result = q.fetch_job(job.id)
            if result is None:
                print("Job Incomplete")
            elif result.is_failed:
                print('something went wrong', result.is_failed)
            else:
                print(job.id)
                print('job successful')

        img_p = ImageParser(redis_ids=redis_ids, parent_dict=_report)
        result_response = img_p.merge_api_responses()

        return jsonify(result_response)

    return app
