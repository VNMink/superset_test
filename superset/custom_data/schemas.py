from superset import app
from superset.models.book import Book

from marshmallow import fields, Schema
from marshmallow.validate import Length, Range

config = app.config

# Column schema descriptions
id_description = "Book id bruh."
book_name_description = "A description of the book name."
author_name_description = "A description for the author name"
description_description = "Description"

# Schema cho book
class BookSchema(Schema):
    id = fields.Int(required=True)
    book_name = fields.Str(required=True)
    author_name = fields.Str(required=True)

# Schema cho book khi gọi phương thức POST
class BookPostSchema(Schema):
    id = fields.Integer(
        metadata={"description":id_description},
        required=True,
    )
    book_name = fields.String(
        metadata={"description":book_name_description},
        required=True,
        validate=Length(1, 250),
    )
    author_name = fields.String(
        metadata={"description":author_name_description},
        required=False,
        validate=Length(1, 250),
    )
    description = fields.String(
        metadata={"description": description_description}, allow_none=True
    )
    tags = fields.Nested(BookSchema, many=True)

# Schema cho book khi gọi phương thức GET
class BookGetResponseSchema(Schema):
    id = fields.Int()
    book_name = fields.String()
    author_name = fields.String()

# Schema cho book khi gọi phương thức PUT
class BookPutSchema(Schema):
    book_name = fields.String(
        metadata={"description":book_name_description},
        required=True,
        validate=Length(1, 250),
    )
    author_name = fields.String(
        metadata={"description":author_name_description},
        required=False,
        validate=Length(1, 250),
    )
    description = fields.String(
        metadata={"description": description_description},
        allow_none=True
    )
    