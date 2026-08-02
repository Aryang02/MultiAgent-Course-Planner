class AppError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class NotFoundError(AppError):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status_code=404)


class ConflictError(AppError):
    def __init__(self, message: str = "Resource already exists"):
        super().__init__(message, status_code=409)


class UnauthorizedError(AppError):
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(message, status_code=401)


class NotImplementedFeatureError(AppError):
    def __init__(self, message: str = "Feature not yet implemented"):
        super().__init__(message, status_code=501)
