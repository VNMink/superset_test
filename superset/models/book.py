import logging
from typing import Any, Callable

from flask_appbuilder import Model

import sqlalchemy as sqla
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    MetaData
)
from sqlalchemy.sql.elements import BinaryExpression

from superset import app, db
# from superset.models.helpers import AuditMixinNullable, ImportExportMixin

config = app.config   # khai báo file config
metadata = Model.metadata   # ¯\_(ツ)_/¯
logger = logging.getLogger(__name__)   # ¯\_(ツ)_/¯

class Book(Model):
    """ testing table for books """

    __tablename__ = "books"
    id = Column(Integer, primary_key=True)   # ID
    book_name = Column(String(250), nullable=False)   # Tên sách
    author_name = Column(String(250), nullable=False)   # Tên tác giả
    
    # def __repr__(self) -> str:
    #     return f"Book<{self.id}>"

    # Định nghĩa phương thức "get" cho model Book
    @classmethod
    def get(cls, id: int):
        qry = db.session.query(Book).filter(id_filter(id))   # Lấy Book (lọc theo ID)
        return qry.one_or_none()

def id_filter(id: int) -> BinaryExpression:   # Định nghĩa bộ lọc theo ID
    return Book.id == int(id)

