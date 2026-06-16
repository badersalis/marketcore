class ProfileNotFoundException(Exception):
    message = "User profile not found"


class KYCDocumentNotFoundException(Exception):
    message = "KYC document not found"


class KYCAlreadySubmittedException(Exception):
    message = "A KYC document is already pending review"


__all__ = [
    "ProfileNotFoundException",
    "KYCDocumentNotFoundException",
    "KYCAlreadySubmittedException",
]
