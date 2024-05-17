'''
models
defines sql alchemy data models
also contains the definition for the room class used to keep track of socket.io rooms

Just a sidenote, using SQLAlchemy is a pain. If you want to go above and beyond, 
do this whole project in Node.js + Express and use Prisma instead, 
Prisma docs also looks so much better in comparison

or use SQLite, if you're not into fancy ORMs (but be mindful of Injection attacks :) )
'''

from sqlalchemy import Column, String, ForeignKey, DateTime, Boolean, Enum as SQLEnum, Date
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from typing import Dict
import uuid
from datetime import datetime
# from .base import Base

# from sqlalchemy import Enum as PyEnum

from enum import Enum as PyEnum


# data models
class Base(DeclarativeBase):
    pass

class UserRole(PyEnum):
    STUDENT = "student"
    ACADEMICS = "academics"
    ADMINISTRATIVE = "administrative"
    ADMIN = "admin"

def is_valid_role(role):
    print(role, UserRole.__members__)
    return role in UserRole.__members__


class User(Base):
    __tablename__ = "user"
    
    username: Mapped[str] = mapped_column(String, primary_key=True)
    password: Mapped[str] = mapped_column(String)
    role: Mapped[UserRole] = mapped_column(SQLEnum(UserRole, name="user_roles"))
    email: Mapped[str] = mapped_column(String)
    full_name: Mapped[str] = mapped_column(String)
    is_online: Mapped[bool] = mapped_column(Boolean, default=False)
    is_muted: Mapped[bool] = mapped_column(Boolean, default=False)



    

# stateful counter used to generate the room id
class Counter():
    def __init__(self):
        self.counter = 0
    
    def get(self):
        self.counter += 1
        return self.counter

# Room class, used to keep track of which username is in which room
class Room():
    def __init__(self):
        self.counter = Counter()
        # dictionary that maps the username to the room id
        # for example self.dict["John"] -> gives you the room id of 
        # the room where John is in
        self.dict: Dict[str, int] = {}

    def create_room(self, sender: str, receiver: str) -> int:
        room_id = self.counter.get()
        self.dict[sender] = room_id
        self.dict[receiver] = room_id
        return room_id
    
    def join_room(self,  sender: str, room_id: int) -> int:
        self.dict[sender] = room_id

    def leave_room(self, user):
        if user not in self.dict.keys():
            return
        del self.dict[user]

    # gets the room id from a user
    def get_room_id(self, user: str):
        if user not in self.dict.keys():
            return None
        return self.dict[user]
    
    

class Article(Base):
    __tablename__ = "articles"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String)
    content = Column(String)
    author_id = Column(String, ForeignKey("user.username"))
    created_at = Column(DateTime, default=datetime.now)
    anonymous = Column(Boolean, default=False)

    author = relationship("User", foreign_keys=[author_id])
    comments = relationship("Comment", back_populates="article", cascade="all, delete-orphan")


class Comment(Base):
    __tablename__ = "comments"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    article_id = Column(String, ForeignKey("articles.id"))
    author_id = Column(String, ForeignKey("user.username"))
    content = Column(String)
    created_at = Column(DateTime, default=datetime.now)
    anonymous = Column(Boolean, default=False)

    article = relationship("Article", foreign_keys=[article_id], back_populates="comments")
    author = relationship("User", foreign_keys=[author_id])


    

class Friend(Base):
    __tablename__ = "friends"

    user_id = Column(String, ForeignKey("user.username"), primary_key=True)
    friend_id = Column(String, ForeignKey("user.username"), primary_key=True)
    status = Column(Boolean, default=False)  # False = pending, True = approved
    created_at = Column(DateTime, default=datetime.now)
    last_seen = Column(DateTime, nullable=True)

    user = relationship("User", foreign_keys=[user_id])
    friend = relationship("User", foreign_keys=[friend_id])


class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    sender = Column(String, ForeignKey("user.username"))
    receiver = Column(String, ForeignKey("user.username"))
    message = Column(String)
    created_at = Column(DateTime, default=datetime.now)

    sender_user = relationship("User", foreign_keys=[sender])
    receiver_user = relationship("User", foreign_keys=[receiver])
