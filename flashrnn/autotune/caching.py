import hashlib
import os
import json
from functools import wraps

from filelock import FileLock


def cache_decorator(cache_dir):
    def no_op_decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            os.makedirs(cache_dir, exist_ok=True)
            # Create a unique key based on the function's name and the hashed arguments.
            key = hashlib.sha256(
                (func.__name__ + str(args) + str(kwargs)).encode()
            ).hexdigest()
            filepath = os.path.join(cache_dir, key)

            lock = FileLock(filepath + ".lock", mode=0o777)
            res = None
            with lock:
                # If the result is cached, return it.
                if os.path.exists(filepath):
                    with open(filepath, "r") as cache_file:
                        res = json.load(cache_file)
                else:
                    res = func(*args, **kwargs)
                    with open(filepath, "w") as cache_file:
                        json.dump(res, cache_file)

            return res

        return wrapper

    return decorator


if __name__ == "__main__":
    # Example usage:
    @cache_decorator(os.path.join(os.environ["HOME"], ".cache"))
    def expensive_function(a, b):
        # Simulate an expensive operation
        return a * b

    # This call will be cached
    print(expensive_function(3, 3))
