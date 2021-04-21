import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class Favourites(SqlAlchemyBase):
    __tablename__ = 'favourites'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)

    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"))
    post_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("news.id"))

    def __repr__(self):
        return str(self.post_id)
