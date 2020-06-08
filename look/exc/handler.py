import json
import inspect

from falcon import HTTPError

class CodeduExceptionHandler(Exception):
    def __init__(self, error):
        print(f"error: {error}")
        if isinstance(error, HTTPError):
            error_info = error.to_dict()
            error_info['type'] = type(error).__name__
            error_info['caller'] = inspect.stack()[1][3]
            self.args = (json.dumps(error_info),)
            for err in error_info:
                setattr(self, err, error_info[err])
            print(error_info)
        elif isinstance(error, Exception):
            print(f"UNKNOWN ERROR IN {inspect.stack()[1][3]}")
        elif isinstance(error, str):
            if error:
                try:
                    error_info = json.loads(error)
                    for err in error_info:
                        setattr(self, err, error_info[err])
                except json.decoder.JSONDecodeError:
                    pass