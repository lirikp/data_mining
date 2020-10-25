from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship


from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Table,
)

"""
one to one
one to many
many to one
many to many
"""

Base = declarative_base()

tag_post = Table(
    'tag_post',
    Base.metadata,
    Column('post_id', Integer, ForeignKey('post.id')),
    Column('tag_id', Integer, ForeignKey('tag.id'))
)

class Post(Base):
    __tablename__ = 'post'
    id = Column(Integer, autoincrement=True, primary_key=True)
    url = Column(String, unique=True, nullable=False)
    img_url = Column(String, unique=False, nullable=True)
    datetime_post = Column(DateTime, unique=False, nullable=False)
    writer_id = Column(Integer, ForeignKey('writer.id'))
    writer = relationship("Writer", back_populates='posts')
    tag = relationship('Tag', secondary=tag_post, back_populates='posts')


class Writer(Base):
    __tablename__ = 'writer'
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String, unique=False, nullable=False)
    url = Column(String, unique=True, nullable=False)
    posts = relationship("Post")
    comments = relationship("Comment")


class Tag(Base):
    __tablename__ = 'tag'
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String, unique=False, nullable=False)
    url = Column(String, unique=True, nullable=False)
    posts = relationship('Post', secondary=tag_post)

class Comment(Base):
    __tablename__ = 'comment'
    id = Column(Integer, autoincrement=True, primary_key=True)
    datetime_comment = Column(DateTime, unique=False, nullable=False)
    body_comment = Column(String, unique=False, nullable=False)
    writer_id = Column(Integer, ForeignKey('writer.id'))
    writer = relationship("Writer", back_populates='comments')

