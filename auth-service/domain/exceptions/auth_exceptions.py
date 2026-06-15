from shared.base_exception import DomainException


class UserAlreadyExistsException(DomainException):
    def __init__(self, email: str):
        super().__init__(f"User with email '{email}' already exists", "USER_ALREADY_EXISTS")


class UserNotFoundException(DomainException):
    def __init__(self):
        super().__init__("User not found", "USER_NOT_FOUND")


class InvalidCredentialsException(DomainException):
    def __init__(self):
        super().__init__("Invalid email or password", "INVALID_CREDENTIALS")


class InvalidTokenException(DomainException):
    def __init__(self, reason: str = ""):
        msg = "Invalid or expired token" + (f": {reason}" if reason else "")
        super().__init__(msg, "INVALID_TOKEN")


class InvalidOtpException(DomainException):
    def __init__(self) -> None:
        super().__init__("Invalid or expired OTP", "INVALID_OTP")


class EmailAlreadyVerifiedException(DomainException):
    def __init__(self) -> None:
        super().__init__("Email address is already verified", "EMAIL_ALREADY_VERIFIED")


__all__ = [
    "UserAlreadyExistsException",
    "UserNotFoundException",
    "InvalidCredentialsException",
    "InvalidTokenException",
    "InvalidOtpException",
    "EmailAlreadyVerifiedException",
]
