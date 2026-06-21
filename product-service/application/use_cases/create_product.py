import logging
from decimal import Decimal
from typing import Optional

from application.dtos.product_dtos import CreateProductRequest, ProductResponse
from domain.entities.product import Product
from domain.exceptions.product_exceptions import CategoryNotFoundException
from domain.repositories.category_repository import CategoryRepository
from domain.repositories.product_repository import ProductRepository
from domain.value_objects.money import Money
from shared.events.product_events import ProductCreated

logger = logging.getLogger(__name__)


class CreateProduct:
    """Creates a new product and fires ProductCreated so the image worker can start."""

    def __init__(
        self,
        product_repo: ProductRepository,
        category_repo: CategoryRepository,
        publisher=None,  # infrastructure.messaging.EventPublisher — optional so tests stay simple
    ) -> None:
        self._product_repo = product_repo
        self._category_repo = category_repo
        self._publisher = publisher

    async def execute(self, request: CreateProductRequest, merchant_id: str = "") -> ProductResponse:
        if request.category_id:
            category = await self._category_repo.get_by_id(request.category_id)
            if not category:
                raise CategoryNotFoundException(request.category_id)

        product = Product(
            name=request.name,
            description=request.description,
            price=Money(amount=Decimal(str(request.price)), currency=request.currency),
            stock=request.stock,
            category_id=request.category_id,
            image_urls=list(request.image_urls),
        )
        product = await self._product_repo.save(product)

        if self._publisher:
            await self._publisher.publish(
                "product.events",
                ProductCreated(
                    product_id=product.id,
                    merchant_id=merchant_id,
                    name=product.name,
                    raw_image_urls=product.image_urls,
                ),
            )
        else:
            logger.warning("No publisher wired — ProductCreated event not sent for %s", product.id)

        return _to_response(product)


def _to_response(p: Product) -> ProductResponse:
    from application.dtos.product_dtos import ProductResponse
    return ProductResponse(
        id=p.id,
        name=p.name,
        description=p.description,
        price=p.price.amount,
        currency=p.price.currency,
        stock=p.stock,
        category_id=p.category_id,
        is_active=p.is_active,
        status=p.status.value,
        image_urls=p.image_urls,
        created_at=p.created_at,
    )


__all__ = ["CreateProduct"]
