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
    id = Column(Integer, primary_key=True)
    book_name = Column(String(250), nullable=False)
    author_name = Column(String(250), nullable=False)
    
    # def __repr__(self) -> str:
    #     return f"Book<{self.id}>"

    @classmethod
    def get(cls, id: int):
        qry = db.session.query(Book).filter(id_filter(id))
        return qry.one_or_none()

def id_filter(id: int) -> BinaryExpression:
    return Book.id == int(id)

