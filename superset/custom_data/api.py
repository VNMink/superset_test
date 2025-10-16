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
    datamodel = SQLAInterface(Book)   # Xác định model được sử dụng trong API
    class_permission_name = "Book"   # Định nghĩa tên nhóm quyền
    resource_name = "book"   # Định nghĩa tên endpoint (api/v1/book)
    include_route_methods = RouteMethod.REST_MODEL_VIEW_CRUD_SET   # Bật các route CRUD
    method_permission_name = MODEL_API_RW_METHOD_PERMISSION_MAP   # Map các phương thức HTTP sang các quyền cụ thể (can_read, can_write,...)
    # Định nghĩa các cột xuất hiện khi gọi GET (1)
    show_comlumns = [
        "id",
        "book_name",
        "author_name"
    ]
    # Định nghĩa các cột xuất hiện khi gọi GET (nhiều)
    list_columns = [
        "id",
        "book_name",
        "author_name"
    ]
    # Định nghĩa các cột được phép chỉnh sửa khi gọi PUT
    edit_columns = [
        "book_name",
        "author_name"
    ]
    # Định nghĩa các cột được phép thêm mới khi gọi POST
    add_columns = [
        "id",
        "book_name",
        "author_name"
    ]
    # # Định nghĩa các cột được phép tìm kiếm khi dùng query params
    search_columns = [
        "id",
        "book_name",
        "author_name"
    ]

    add_model_schema = BookPostSchema()   # Định nghĩa schema cho phương thức POST
    book_get_response_schema = BookGetResponseSchema()   # Định nghĩa schema cho phương thức GET
    edit_model_schema = BookPutSchema()   # Định nghĩa schema cho phương thức PUT

    # Định nghĩa decorator lấy book theo id
    def with_book(
        f: Callable[[BaseSupersetModelRestApi, Book], Response]
    ) -> Callable[[BaseSupersetModelRestApi, int], Response]:
        def wraps(self: BaseSupersetModelRestApi, id: int) -> Response:
            try:
                book = BookDAO.get_by_id(id)   # Gọi hàm lấy book theo id của DAO
                return f(self, book)
            except BookNotFoundError:
                return self.response_404()
        return functools.update_wrapper(wraps, f)

    @expose("/", methods=("POST",))   # Định nghĩa endpoint API
    @protect()   # Kiểm tra đăng nhập/quyền của user
    @safe   # Xử lý exception để không bị sập server
    @statsd_metrics   # Log số liệu thống kê khi gọi API
    @requires_json   # Bắt request phải có dạng JSON
    def post(self) -> Response:
        try:
            item = self.add_model_schema.load(request.json)   # Lấy dữ liệu từ request và lọc theo schema Post
        # This validates custom Schema with custom validations
        except ValidationError as error:
            return self.response_400(message=error.messages)
        
        new_book = CreateBookCommand(item).run()   # Chạy command tạo book mới
        return self.response(201, id=new_book.id, result=item)
    
    @expose("/<id>", methods=("GET",))    # Định nghĩa endpoint API
    @protect()   # Kiểm tra đăng nhập/quyền của user
    @safe   # Xử lý exception để không bị sập server
    @statsd_metrics   # Log số liệu thống kê khi gọi API
    @with_book   # Gọi hàm with_book được định nghĩa ở đầu
    def get(
        self,
        book: Book
    ) -> WerkzeugResponse:
        result = self.book_get_response_schema.dump(book)   # Lấy dữ liệu book nhận được từ decorator và dump vào
        return self.response(200, result=result)
    
    @expose("/<id>", methods=("PUT",))    # Định nghĩa endpoint API
    @protect()   # Kiểm tra đăng nhập/quyền của user
    @safe   # Xử lý exception để không bị sập server
    @statsd_metrics   # Log số liệu thống kê khi gọi API
    @event_logger.log_this_with_context(
        action=lambda self, *args, **kwargs: f"{self.__class__.__name__}.put",
        log_to_statsd=False,
    )   # Log lại khi API được gọi, kèm với: endpoint, phương thức, thông tin người dùng
    @requires_json   # Bắt request phải có dạng JSON
    def put(self, id: int) -> Response:
        try:
            book = self.edit_model_schema.load(request.json)   # Lấy dữ liệu từ request và lọc theo schema Update
        except ValidationError as error:
            return self.response_400(message=error.messages)
        try:
            changed_model = UpdateBookCommand(id, book).run()   # Khởi chạy command update book
            response = self.response(200, id=changed_model.id, result=book)
        except BookNotFoundError:
            response = self.response_404()
        return response
    
    @expose("/<id>", methods=("DELETE",))   # Định nghĩa endpoint API
    @protect()   # Kiểm tra đăng nhập/quyền của user
    @safe   # Xử lý exception để không bị sập server
    @statsd_metrics   # Log số liệu thống kê khi gọi API
    @event_logger.log_this_with_context(
        action=lambda self, *args, **kwargs: f"{self.__class__.__name__}.delete",
        log_to_statsd=False,
    )   # Log lại khi API được gọi, kèm với: endpoint, phương thức, thông tin người dùng
    def delete(self, id: int) -> Response:
        try:
            DeleteBookCommand([id]).run()   # Khởi chạy command delete book
            return self.response(200, message="OK")
        except BookNotFoundError:
            return self.response_404()