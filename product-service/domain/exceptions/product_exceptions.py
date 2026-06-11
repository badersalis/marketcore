from shared.base_exception import DomainException


class ProductNotFoundException(DomainException):
    def __init__(self, product_id: str = ""):
        msg = f"Product '{product_id}' not found" if product_id else "Product not found"
        super().__init__(msg, "PRODUCT_NOT_FOUND")


class CategoryNotFoundException(DomainException):
    def __init__(self, category_id: str = ""):
        msg = f"Category '{category_id}' not found" if category_id else "Category not found"
        super().__init__(msg, "CATEGORY_NOT_FOUND")


class SlugAlreadyExistsException(DomainException):
    def __init__(self, slug: str):
        super().__init__(f"Slug '{slug}' already exists", "SLUG_ALREADY_EXISTS")


__all__ = ["ProductNotFoundException", "CategoryNotFoundException", "SlugAlreadyExistsException"]
