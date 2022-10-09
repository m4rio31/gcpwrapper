SEVERITIES = ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'NOTSET']


class IllegalArgumentException(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class InvalidSeverityException(IllegalArgumentException):
    "Rised when an invalid severity is passed to a logger"
    def __init__(self, severity: str):
        super().__init__(f'{severity} severity is invalid. Use {SEVERITIES}')
    