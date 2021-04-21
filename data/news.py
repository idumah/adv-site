import datetime
import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase

categories = orm.relation("Category",
                          secondary="association",
                          backref="news")


class News(SqlAlchemyBase):
    __tablename__ = 'news'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    content = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now())

    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"))
    user = orm.relation('User')

    def get_news_id(self):
        return self.id

    def __repr__(self):
        return f'<News> {self.user} {self.id} {self.title} {self.content}'