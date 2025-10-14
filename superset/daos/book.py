from __future__ import annotations

import logging
import uuid
from typing import Any

from superset.extensions import db
from superset.daos.base import BaseDAO
from superset.databases.filters import DatabaseFilter
from superset.models.book import Book, id_filter
from superset.commands.book.exceptions import BookNotFoundError

logger = logging.getLogger(__name__)

class BookDAO(BaseDAO[Book]):
    base_filter = DatabaseFilter

    # @classmethod
    # def update(
    #     cls,
    #     item: Book | None = None,
    #     attributes: dict[str, Any] | None = None,
    #     commit: bool = True,
    # ) -> Book:
    #     if item and attributes and "encrypted_extra" in attributes:
    #         attributes["encrypted_extra"] = item.db_engine_spec.unmask_encrypted_extra(
    #             item.encrypted_extra,
    #             attributes["encrypted_extra"],
    #         )

    #     return super().update(item, attributes, commit)

    @classmethod
    def get_by_id(cls, id: int) -> Book:
        book = Book.get(id)
        if not book:
            raise BookNotFoundError()
        
        return book
    
    
def is_uuid(value: str | int) -> bool:
    try:
        uuid.UUID(str(value))
        return True
    except ValueError:
        return False