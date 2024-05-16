'''
db
database file, containing all the logic to interface with the sql database
'''

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from cryptography.fernet import Fernet, InvalidToken
import os
from models import *

from pathlib import Path
from encryption import get_fernet
from sqlalchemy import or_

from datetime import datetime
from sqlalchemy.orm import joinedload



# ENCRYPTION_KEY = Fernet.generate_key()
fernet = get_fernet()


# creates the database directory
Path("database") \
    .mkdir(exist_ok=True)

# "database/main.db" specifies the database file
# change it if you wish
# turn echo = True to display the sql output
engine = create_engine("sqlite:///database/main.db", echo=False)

# initializes the database
Base.metadata.create_all(engine)



def set_user_online(username: str):
    """ Set the user's online status to True """
    with Session(engine) as session:
        user = session.get(User, username)
        if user:
            user.is_online = True
            session.commit()

def set_user_offline(username: str):
    """ Set the user's online status to False """
    with Session(engine) as session:
        user = session.get(User, username)
        if user:
            user.is_online = False
            session.commit()


# inserts a user to the database
def insert_user(username: str, password: str, role: str):
    with Session(engine) as session:
        user = User(username=username, password=password, role=role)
        session.add(user)
        session.commit()

def insert_user(username: str, password: str, role: str):
    with Session(engine) as session:
        user = User(username=username, password=password, role=role)
        session.add(user)
        session.commit()

# gets a user from the database
def get_user(username: str):
    with Session(engine) as session:
        return session.get(User, username)

# def get_friends(username: str):
#     with Session(engine) as session:
#         friends = (
#             session.query(Friend)
#             .filter((Friend.user_id == username) | (Friend.friend_id == username))
#             .filter(Friend.status == True)
#             .all()
#         )
#         return [friend.user.username if friend.user_id != username else friend.friend.username for friend in friends]
    
def get_friends(username: str):
    with Session(engine) as session:
        friends = (
            session.query(User.username, User.is_online, User.role)
            .join(Friend, or_(Friend.user_id == User.username, Friend.friend_id == User.username))
            .filter(or_(Friend.user_id == username, Friend.friend_id == username))
            .filter(Friend.status == True)
            .filter(User.username != username) 
            .all()
        )
        return [{'username': friend[0], 'is_online': friend[1], 'role': friend[2]} for friend in friends]


def get_friend_requests(username: str):
    with Session(engine) as session:
        sent_requests = (
            session.query(Friend)
            .filter(Friend.user_id == username, Friend.status == False)
            .all()
        )
        received_requests = (
            session.query(Friend)
            .filter(Friend.friend_id == username, Friend.status == False)
            .all()
        )
        return (
            [friend.friend.username for friend in sent_requests],
            [friend.user.username for friend in received_requests]
        )


def remove_friend(username: str, friend_username: str):
    with Session(engine) as session:
        friendship = (
            session.query(Friend)
            .filter(
                ((Friend.user_id == username) & (Friend.friend_id == friend_username)) |
                ((Friend.user_id == friend_username) & (Friend.friend_id == username))
            )
            .first()
        )
        
        if friendship:
            session.delete(friendship)
            session.commit()
            return True
        return False


def add_friend_request(username: str, friend_username: str):
    with Session(engine) as session:
        # Check if the friendship already exists
        existing_friendship = (
            session.query(Friend)
            .filter(
                ((Friend.user_id == username) & (Friend.friend_id == friend_username)) |
                ((Friend.user_id == friend_username) & (Friend.friend_id == username))
            )
            .first()
        )
        if existing_friendship:
            return False

        # Create a new friendship request
        friendship = Friend(user_id=username, friend_id=friend_username)
        session.add(friendship)
        session.commit()
        return True

# def approve_friend_request(username: str, friend_username: str):
    # with Session(engine) as session:
    #     friendship = (
    #         session.query(Friend)
    #         .filter((Friend.user_id == username) & (Friend.friend_id == friend_username))
    #         .first()
    #     )
    #     if friendship:
    #         friendship.status = True
    #         session.commit()
    #         return True
    #     return False

def approve_friend_request(username: str, friend_username: str):
    
    with Session(engine) as session:
        friendship = (
            session.query(Friend)
            .filter(
                (Friend.user_id == friend_username) & (Friend.friend_id == username)
            )
            .first()
        )
        
        if friendship:
            friendship.status = True
            session.commit()
            return True
        else:
            return False

def reject_friend_request(username: str, friend_username: str):
    with Session(engine) as session:
        friendship = (
            session.query(Friend)
            .filter((Friend.user_id == username) & (Friend.friend_id == friend_username))
            .first()
        )
        if friendship:
            session.delete(friendship)
            session.commit()
            return True
        return False

def store_message(sender: str, receiver: str, message: str):
    # fernet = Fernet(ENCRYPTION_KEY)
    encrypted_message = fernet.encrypt(message.encode())
    with Session(engine) as session:
        chat_history = ChatHistory(
            sender=sender,
            receiver=receiver,
            message=encrypted_message,
            created_at=datetime.now()
        )
        session.add(chat_history)
        session.commit()


def get_chat_history(user1: str, user2: str, last_seen: datetime = None):
    with Session(engine) as session:
        query = (
            session.query(
                ChatHistory.message,
                User.username.label('sender')
            )
            .join(ChatHistory.sender_user)
            .filter(
                ((ChatHistory.sender == user1) & (ChatHistory.receiver == user2)) |
                ((ChatHistory.sender == user2) & (ChatHistory.receiver == user1))
            )
            .order_by(ChatHistory.created_at)
        )

        if last_seen:
            query = query.filter(ChatHistory.created_at > last_seen)
        
        chat_history = query.all()

        result = []
        for message, sender in chat_history:
            try:
                decrypted_message = fernet.decrypt(message).decode()
                result.append((decrypted_message, sender))
            except (InvalidToken, UnicodeDecodeError):
                continue
        
        return result



def add_friends(username: str, friend_username: str):
    with Session(engine) as session:
        # Check if the friendship already exists
        existing_friendship = (
            session.query(Friend)
            .filter(
                ((Friend.user_id == username) & (Friend.friend_id == friend_username)) |
                ((Friend.user_id == friend_username) & (Friend.friend_id == username))
            )
            .first()
        )
        if existing_friendship:
            return False

        # Create a new friendship
        friendship = Friend(user_id=username, friend_id=friend_username)
        session.add(friendship)
        session.commit()
        return True

def clear_chat_history(sender: str, receiver: str, last_seen: datetime = None):
    with Session(engine) as session:
        query = (
            session.query(ChatHistory)
            .filter(
                ((ChatHistory.sender == sender) & (ChatHistory.receiver == receiver)) |
                ((ChatHistory.sender == receiver) & (ChatHistory.receiver == sender))
            )
        )

        if last_seen:
            query = query.filter(ChatHistory.created_at <= last_seen)
        
        query.delete(synchronize_session=False)
        session.commit()


def clear_Friends_history():
    with Session(engine) as session:
        # Delete all records from the ChatHistory table
        session.query(ChatHistory).delete()
        session.commit()

# clear_chat_history()
def clear_all_data():
    with Session(engine) as session:
        for table in reversed(Base.metadata.sorted_tables):
            session.execute(table.delete())
        session.commit()

# clear_all_data()



def update_last_seen(username: str, friend_username: str, timestamp: datetime):
    with Session(engine) as session:
        friendship = (
            session.query(Friend)
            .filter(
                ((Friend.user_id == username) & (Friend.friend_id == friend_username)) |
                ((Friend.user_id == friend_username) & (Friend.friend_id == username))
            )
            .first()
        )
        if friendship:
            friendship.last_seen = timestamp
            session.commit()

def get_last_seen(username: str, friend_username: str):
    with Session(engine) as session:
        friendship = (
            session.query(Friend.last_seen)
            .filter(
                ((Friend.user_id == username) & (Friend.friend_id == friend_username)) |
                ((Friend.user_id == friend_username) & (Friend.friend_id == username))
            )
            .first()
        )
        return friendship.last_seen if friendship else None



def add_article(title: str, content: str, author: str):
    with Session(engine) as session:
        article = Article(title=title, content=content, author_id=author)
        session.add(article)
        session.commit()

def get_articles():
    with Session(engine) as session:
        return session.query(Article).options(
            joinedload(Article.author),
            joinedload(Article.comments).joinedload(Comment.author)
        ).order_by(Article.created_at.desc()).all()



def add_comment(article_id: str, content: str, author_id: str):
    with Session(engine) as session:
        comment = Comment(article_id=article_id, content=content, author_id=author_id)
        session.add(comment)
        session.commit()

def get_comments(article_id: str):
    with Session(engine) as session:
        return session.query(Comment).options(joinedload(Comment.author)).filter_by(article_id=article_id).order_by(Comment.created_at.asc()).all()
    


# Add functions for muting/unmuting users
def mute_user(username: str):
    with Session(engine) as session:
        user = session.get(User, username)
        if user:
            user.is_muted = True
            session.commit()

def unmute_user(username: str):
    with Session(engine) as session:
        user = session.get(User, username)
        if user:
            user.is_muted = False
            session.commit()

# Add functions for modifying and deleting articles and comments
def update_article(article_id: str, title: str, content: str):
    with Session(engine) as session:
        article = session.get(Article, article_id)
        if article:
            article.title = title
            article.content = content
            session.commit()

def delete_article(article_id: str):
    with Session(engine) as session:
        article = session.get(Article, article_id)
        if article:
            session.delete(article)
            session.commit()

def update_comment(comment_id: str, content: str):
    with Session(engine) as session:
        comment = session.get(Comment, comment_id)
        if comment:
            comment.content = content
            session.commit()

def delete_comment(comment_id: str):
    with Session(engine) as session:
        comment = session.get(Comment, comment_id)
        if comment:
            session.delete(comment)
            session.commit()
