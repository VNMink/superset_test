import logging
from typing import Optional

from superset.commands.base import BaseCommand
from superset.commands.book.exceptions import (
    BookDeleteFailedError,
    BookNotFoundError,
)
from superset.daos.book import BookDAO
from superset.daos.exceptions import DAODeleteFailedError
from superset.models.book import Book

logger = logging.getLogger(__name__)


class DeleteBookCommand(BaseCommand):
    def __init__(self, model_ids: list[int]):
        self._model_ids = model_ids
        self._models: Optional[list[Book]] = None

    def run(self) -> None:
        self.validate()

        try:
            BookDAO.delete(self._models)
        except DAODeleteFailedError as ex:
            logger.exception(ex.exception)
            raise BookDeleteFailedError() from ex
        
    def validate(self) -> None:
        self._models = BookDAO.find_by_ids(self._model_ids)
        if not self._models:
            raise BookNotFoundError()