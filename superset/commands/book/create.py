import logging
from typing import Any, Optional

from flask import current_app
from flask_appbuilder.models.sqla import Model

from superset.commands.book.exceptions import (
    BookCreateFailedError,
)

from superset.commands.base import BaseCommand, CreateMixin
from superset.daos.book import BookDAO
from superset.daos.exceptions import DAOCreateFailedError
from superset.extensions import db
from superset.extensions import event_logger

logger = logging.getLogger(__name__)
stats_logger = current_app.config["STATS_LOGGER"]

class CreateBookCommand(BaseCommand, CreateMixin):
    def __init__(self, data: dict[str, Any]):
        self._properties = data.copy()

    def run(self) -> Model:
        try:
            book = BookDAO.create(attributes=self._properties)

        except DAOCreateFailedError as ex:
            db.session.rollback()
            event_logger.log_with_context(
                action=f"book_creation_failed{ex.__class__.__name__}",
                engine=book.db_engine_spec.__name__,
            )
            raise BookCreateFailedError() from ex
        
        return book
    
    def validate(self) -> None:
        exceptions = []


