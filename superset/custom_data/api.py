import functools
import logging
from typing import Callable

from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder.api import expose, protect, rison, safe

from marshmallow import ValidationError

from flask import redirect, request, Response, send_file, url_for

from werkzeug.wrappers import Response as WerkzeugResponse


from superset import app
from superset.constants import MODEL_API_RW_METHOD_PERMISSION_MAP, RouteMethod
from superset.commands.book.exceptions import BookNotFoundError

from superset.views.base_api import (
    BaseSupersetModelRestApi,
    RelatedFieldFilter,
    requires_form_data,
    requires_json,
    statsd_metrics,
)

from superset.daos.book import BookDAO
from superset.extensions import event_logger
from superset.commands.book.create import CreateBookCommand
from superset.commands.book.update import UpdateBookCommand
from superset.commands.book.delete import DeleteBookCommand
from superset.custom_data.schemas import (
    BookPostSchema,
    BookGetResponseSchema,
    BookPutSchema
)
from superset.models.book import Book
# from superset.extensions import event_logger

logger = logging.getLogger(__name__)
config = app.config


class BookRestApi(BaseSupersetModelRestApi):
    datamodel = SQLAInterface(Book)
    class_permission_name = "Book"
    resource_name = "book"
    include_route_methods = RouteMethod.REST_MODEL_VIEW_CRUD_SET
    method_permission_name = MODEL_API_RW_METHOD_PERMISSION_MAP
    show_comlumns = [
        "id",
        "book_name",
        "author_name"
    ]
    list_columns = [
        "id",
        "book_name",
        "author_name"
    ]
    edit_columns = [
        "book_name",
        "author_name"
    ]
    add_columns = [
        "id",
        "book_name",
        "author_name"
    ]
    search_columns = [
        "id",
        "book_name",
        "author_name"
    ]

    add_model_schema = BookPostSchema()
    book_get_response_schema = BookGetResponseSchema()
    edit_model_schema = BookPutSchema()

    def with_book(
        f: Callable[[BaseSupersetModelRestApi, Book], Response]
    ) -> Callable[[BaseSupersetModelRestApi, int], Response]:
        def wraps(self: BaseSupersetModelRestApi, id: int) -> Response:
            try:
                book = BookDAO.get_by_id(id)
                return f(self, book)
            except BookNotFoundError:
                return self.response_404()
        return functools.update_wrapper(wraps, f)

    @expose("/", methods=("POST",))
    @protect()
    @safe
    @statsd_metrics
    @requires_json
    def post(self) -> Response:
        try:
            item = self.add_model_schema.load(request.json)
        # This validates custom Schema with custom validations
        except ValidationError as error:
            return self.response_400(message=error.messages)
        
        new_book = CreateBookCommand(item).run()
        return self.response(201, id=new_book.id, result=item)
    
    @expose("/<id>", methods=("GET",))
    @protect()
    @safe
    @statsd_metrics
    @with_book
    def get(
        self,
        book: Book
    ) -> WerkzeugResponse:
        result = self.book_get_response_schema.dump(book)    
        return self.response(200, result=result)
    
    @expose("/<id>", methods=("PUT",))
    @protect()
    @safe
    @statsd_metrics
    @event_logger.log_this_with_context(
        action=lambda self, *args, **kwargs: f"{self.__class__.__name__}.put",
        log_to_statsd=False,
    )
    @requires_json
    def put(self, id: int) -> Response:
        try:
            book = self.edit_model_schema.load(request.json)
        except ValidationError as error:
            return self.response_400(message=error.messages)
        try:
            changed_model = UpdateBookCommand(id, book).run()
            response = self.response(200, id=changed_model.id, result=book)
        except BookNotFoundError:
            response = self.response_404()
        return response
    
    @expose("/<id>", methods=("DELETE",))
    @protect()
    @safe
    @statsd_metrics
    @event_logger.log_this_with_context(
        action=lambda self, *args, **kwargs: f"{self.__class__.__name__}.delete",
        log_to_statsd=False,
    )
    def delete(self, id: int) -> Response:
        try:
            DeleteBookCommand([id]).run()
            return self.response(200, message="OK")
        except BookNotFoundError:
            return self.response_404()