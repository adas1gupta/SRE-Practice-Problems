from enum import Enum

class PermanentException(Enum):
    ServerError: 400 

class RetryableException(Enum):

def retry_decorator(func, max_attempts=3):
    attempts = 0
    def retry(*args, **kwargs):
        nonlocal attempts
        while True:
            try:
                attempts += 1
                res = func()
                return res
            except PermanentException: 
                raise
            except RetryableException:
                if attempts >= max_attempts:
                    raise Exception("Max attempts have been reached")

    return retry