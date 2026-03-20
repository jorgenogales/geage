import functions_framework

@functions_framework.http
def generate_exception(request):
    """HTTP Cloud Function that generates an exception based on input parameters.
    Args:
        request (flask.Request): The request object.
    Returns:
        A success message if no exception is triggered.
    """
    request_json = request.get_json(silent=True)
    request_args = request.args

    should_fail = False
    error_message = "A forced exception occurred based on the provided parameters."

    # Check for 'fail' parameter in JSON body
    if request_json and 'fail' in request_json:
        should_fail = request_json.get('fail')
        if 'message' in request_json:
            error_message = request_json.get('message')
    # Check for 'fail' parameter in query string
    elif request_args and 'fail' in request_args:
        should_fail = request_args.get('fail', '').lower() in ['true', '1', 'yes']
        if 'message' in request_args:
            error_message = request_args.get('message')

    if should_fail:
        raise ValueError(error_message)

    return "Success! No exception was triggered. Pass ?fail=true or {\"fail\": true} to trigger one."
