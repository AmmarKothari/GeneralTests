MAX_FAILURES = 3


class RequestError(Exception):
    pass


def _check_if_request_successful(success):
    if success:
        raise RequestError('Failed to get data')


def _check_with_retry(request_func):
    failure_counter = 0
    while failure_counter < MAX_FAILURES:
        success, info = request_func()
        try:
            _check_if_request_successful(success)
            # Break if the request was successful
            return info
        except RequestError:
            failure_counter += 1
            print(f"Failed to get data {failure_counter} times.  Retrying.")

