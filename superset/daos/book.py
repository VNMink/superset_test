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

# Định nghĩa lớp DAO của Book để giao tiếp với DB
class BookDAO(BaseDAO[Book]):
    base_filter = DatabaseFilter   # Định nghĩa filter để hạn chế quyền truy cập của người dùng cho mọi truy vấn

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

    # Định nghĩa phương thức class để lấy dữ liệu Book (gọi phương thức "get" của Book)
    @classmethod
    def get_by_id(cls, id: int) -> Book:
        book = Book.get(id)
        if not book:
            raise BookNotFoundError()
        
        return book
    
# Kiểm tra lại code mình mới thấy hàm này bị thừa ¯\_(ツ)_/¯
# def is_uuid(value: str | int) -> bool:
#     try:
#         uuid.UUID(str(value))
#         return True
#     except ValueError:
#         return False