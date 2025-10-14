from typing import Optional


from flask_babel import lazy_gettext as _

from superset.commands.exceptions import (
    CommandException,
    CommandInvalidError,
    CreateFailedError,
    DeleteFailedError,
    ImportFailedError,
    UpdateFailedError,
    ObjectNotFoundError
)

class BookCreateFailedError(CreateFailedError):
    message = _("Gugugaga broken, could not be created.")

class BookNotFoundError(ObjectNotFoundError):
    message = _("No book here")

    # def __init__(
    #     self, id: Optional[str] = None, exception: Optional[str] = None
    # ) -> None:
    #     super().__init__("Book", id, exception)

    def __init__(self):
        super().__init__(object_type="Book")

class BookUpdateFailedError(UpdateFailedError):
    message = _("OH GOD ITS ALL WRONG")

class BookDeleteFailedError(DeleteFailedError):
    message = _("NANOMACHINES SON")