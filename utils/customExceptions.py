class CustomHttpException(Exception):
    def __init__(self, message, status_code):
        super().__init__(message)
        Exception.__init__(self, status_code, message)
