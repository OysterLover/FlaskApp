import pydantic
from typing import Type, Optional

import sqlalchemy
from flask import Flask, jsonify, request
from flask.views import MethodView
from sqlalchemy import Column, Integer, String, DateTime, create_engine, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

app = Flask('app')


class HttpError(Exception):

    def __init__(self, status_code: int, message: str | dict | list):
        self.status_code = status_code
        self.message = message


@app.errorhandler(HttpError)
def error_handler(error: HttpError):
    response = jsonify({
        'status': 'error', 'message': error.message
    })
    response.status_code = error.status_code
    return response


DSN = 'postgresql://app:1234@127.0.0.1:5431/netology'

engine = create_engine(DSN)
Base = sqlalchemy.orm.declarative_base()
Session = sessionmaker(bind=engine)


class MessageModel(Base):
    __tablename__ = 'messages'

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False, unique=True)
    text = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    owner_name = Column(String(32), nullable=False)


Base.metadata.create_all(engine)


class CreateMessageSchema(pydantic.BaseModel):
    title: str
    text: str
    owner_name: str

    @pydantic.validator('owner_name')
    def check_owner_name(cls, value: str):
        if len(value) > 32:
            raise ValueError('owner_name must be less then 32 chars')
        return value


class PatchMessageSchema(pydantic.BaseModel):
    title: Optional[str]
    text: Optional[str]
    owner_name: Optional[str]

    @pydantic.validator('owner_name')
    def check_owner_name(cls, value: str):
        if len(value) > 32:
            raise ValueError('owner_name must be less then 32 chars')
        return value


def validate(data_to_validate: dict, validation_class: Type[CreateMessageSchema] | Type[PatchMessageSchema]):
    try:
        return validation_class(**data_to_validate).dict(exclude_none=True)
    except pydantic.ValidationError as err:
        raise HttpError(400, err.errors())


def get_by_id(item_id: int, orm_model: Type[MessageModel], session: Session):
    orm_item = session.query(orm_model).get(item_id)
    if orm_item is None:
        raise HttpError(404, 'item not found')
    return orm_item


class MessageView(MethodView):

    def get(self, message_id: int):
        with Session() as session:
            message = get_by_id(message_id, MessageModel, session)
            return jsonify({
                'message_title': message.title,
                'message_text': message.text,
                'creation_time': message.created_at.isoformat()
            })

    def post(self):
        json_data = request.json
        with Session() as session:
            new_message = MessageModel(**validate(json_data, CreateMessageSchema))
            session.add(new_message)
            session.commit()
            return jsonify({'status': 'message posted',
                            'id': new_message.id,
                            'message_title': new_message.title,
                            'message_text': new_message.text})

    def patch(self, message_id: int):
        data_to_patch = validate(request.json, PatchMessageSchema)
        with Session() as session:
            message = get_by_id(message_id, MessageModel, session)
            for field, value in data_to_patch.items():
                setattr(message, field, value)
            session.commit()
            return jsonify({'status': 'success'})

    def delete(self, message_id: int):
        with Session() as session:
            message = get_by_id(message_id, MessageModel, session)
            session.delete(message)
            session.commit()
            return jsonify({'status': 'deletion success'})


app.add_url_rule('/message/<int:message_id>', view_func=MessageView.as_view('messages_get'), methods=['GET', 'PATCH', 'DELETE'])
app.add_url_rule('/message/', view_func=MessageView.as_view('messages'), methods=['POST'])

app.run()
