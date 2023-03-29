from dataclasses import dataclass
from datetime import datetime
from json import dumps

from aiohttp.web import (
    Request,
    StreamResponse,
    HTTPBadRequest,
    HTTPCreated,
    json_response,
)
from apischema import ValidationError, deserialize, serialize, validator

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
        raise HTTPBadRequest(reason=dumps(err.errors))
    print(f"New user to add: {user_request}")

    session = request["session"]
    user = User(
        email=user_request.email, name=user_request.name, lastname=user_request.lastname
    )
    session.add(user)
    await session.commit()
    print(f"New user added: {user}")
    user_json = dumps(serialize(CreateUserResponse, user))
    return json_response(data=user_json, status=HTTPCreated.status_code)
