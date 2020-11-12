from typing import Any, Callable, Dict, Optional, List, Union, Tuple

Py3cw_request_info = Optional[Dict[str, Any]]
Py3cw_request_info_list = List[Optional[Dict[str, Any]]]
Py3cw_request_success = Optional[Dict[str, Any]]
Py3cw_request = Tuple[Py3cw_request_info, Union[Py3cw_request_success, Py3cw_request_info_list]]

MAX_FAILURES = 3


class RequestError(Exception):
    pass


def check_if_request_successful(success: Py3cw_request_success) -> None:
    if success:
        raise RequestError('Failed to get data: {}'.format(success))
    return None


def check_with_retry(request_func: Callable[[], Py3cw_request]) -> Union[Py3cw_request_info, Py3cw_request_info_list]:
    failure_counter: int = 0
    while failure_counter < MAX_FAILURES:
        success, info = request_func()
        try:
            check_if_request_successful(success)
            # Break if the request was successful
            return info
        except RequestError:
            failure_counter += 1
            print(f"Failed to get data {failure_counter} times.  Retrying.")
    return None

