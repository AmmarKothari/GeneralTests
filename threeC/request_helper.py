def _check_if_request_successful(success):
    if success:
        raise Exception('Failed to get data')
