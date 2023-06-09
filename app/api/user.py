import json
from dataclasses import dataclass
from datetime import datetime

from aiohttp.web import (
    HTTPBadRequest,
    HTTPCreated,
    Request,
    StreamResponse,
    json_response,
)
from apischema import ValidationError, deserialize, serialize, validator
from sqlalchemy.exc import IntegrityError

from app.models.user import User


@dataclass
class CreateUserRequest:
    name: str
    lastname: str
    email: str

    @validator
    def email_is_email(self):
        if "@" not in self.email:
            yield "Emails should contain '@' sign."


@dataclass
class CreateUserResponse(CreateUserRequest):
    id: int
    created_at: datetime


async def create_user_handler(request: Request) -> StreamResponse:
    try:
        user_request = deserialize(CreateUserRequest, await request.json())
    except ValidationError as err:
        raise HTTPBadRequest(reason=json.dumps(err.errors))
    print(f"New user to add: {user_request}")

    session = request["session"]
    user = User(
        email=user_request.email,
        name=user_request.name,
        lastname=user_request.lastname,
    )
    session.add(user)
    try:
        await session.commit()
    except IntegrityError as err:
        msg = 'duplicate key value violates unique constraint "user_email_key"'
        if msg in str(err.orig):
            print(f"Duplicated email {repr(err)}")
            raise HTTPBadRequest(reason="Email already exists")
        raise
    print(f"New user added: {user}")
    user_json = json.dumps(serialize(CreateUserResponse, user))
    return json_response(data=user_json, status=HTTPCreated.status_code)
