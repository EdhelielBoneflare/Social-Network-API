import re
from enum import Enum

from app import USERS, POSTS


class Status(Enum):
    ACTIVE = "active"
    DELETED = "deleted"


class User:
    def __init__(self, user_id, first_name, last_name, nickname, email):
        self.id = user_id
        self.first_name = first_name
        self.last_name = last_name
        self.nickname = nickname
        self.email = email
        self.total_reactions = 0
        self.posts = []
        self.status = Status.ACTIVE

    def __lt__(self, other):
        return self.total_reactions < other.total_reactions

    def to_dict(self):
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "nickname": self.nickname,
            "email": self.email,
            "total_reactions": self.total_reactions,
            "posts": self.posts,
            "status": self.status.value,
        }

    @staticmethod
    def is_valid_id(user_id):
        return (user_id in USERS) and (USERS[user_id].status != Status.DELETED)

    @staticmethod
    def is_valid_nickname(nickname):
        return re.match("^[A-Za-z0-9_]*$", nickname) and 2 < len(nickname) < 21

    @staticmethod
    def is_valid_email(email):
        regex = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b")
        return re.match(regex, email)

    @staticmethod
    def get_leaderboard(reverse="asc"):
        leaderboard = [USERS[u_id] for u_id in USERS if USERS[u_id].is_valid_id(u_id)]
        if reverse == "desc":
            leaderboard = sorted(leaderboard, reverse=True)
        else:
            leaderboard = sorted(leaderboard)
        return [user.to_dict() for user in leaderboard]


class Post:
    def __init__(self, post_id, author_id, text):
        self.id = post_id
        self.author_id = author_id
        self.text = text
        self.reactions = []
        self.status = Status.ACTIVE

    def to_dict(self):
        return {
            "id": self.id,
            "author_id": self.author_id,
            "text": self.text,
            "reactions": self.reactions,
            "status": self.status.value,
        }

    @staticmethod
    def is_valid_id(post_id):
        return (post_id in POSTS) and (POSTS[post_id].status != Status.DELETED)
