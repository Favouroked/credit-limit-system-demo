class ECSError(Exception):
    code = 500
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message


class AuthError(ECSError):
    code = 401

class CircuitBreakerError(ECSError):
    code = 503

class InvalidValue(ECSError):
    code = 400

class NotFoundError(ECSError):
    code = 404