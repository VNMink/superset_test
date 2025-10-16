import logging
from typing import Any, Optional

from flask_appbuilder.models.sqla import Model
from marshmallow import ValidationError

from superset.models.book import Book
from superset.commands.base import BaseCommand, UpdateMixin
from superset.commands.book.exceptions import (
    BookNotFoundError,
    BookUpdateFailedError
)
from superset.daos.book import BookDAO
from superset.daos.exceptions import DAOUpdateFailedError

logger = logging.getLogger(__name__)

class UpdateBookCommand(UpdateMixin, BaseCommand):
    def __init__(self, model_id: int, data: dict[str, Any]):
        self._model_id = model_id
        self._properties = data.copy()
        self._model: Optional[Book] = None

    def run(self) -> Model:
        self.validate()

        try:
            book = BookDAO.update(self._model, self._properties)
        except DAOUpdateFailedError as ex:
            logger.exception(ex.exception)
            raise BookUpdateFailedError() from ex
        return book
    
    def validate(self) -> None:
        exceptions = []

        self._model = BookDAO.get_by_id(self._model_id)
        if not self._model:
            raise BookNotFoundError()