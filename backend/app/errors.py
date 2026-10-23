"""Stable error codes; never return database internals or submitted secrets."""


class AppError(Exception):
    def __init__(self, status: int, code: str, message: str):
        self.status = status
        self.code = code
        self.message = message
        super().__init__(code)


def fail(status: int, code: str, message: str) -> None:
    raise AppError(status, code, message)
