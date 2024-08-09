from http import HTTPStatus
from flask import request, Response

from app import app, USERS, POSTS
from app import models


@app.post("/posts/<int:post_id>/reaction")
def set_reaction(post_id):
    if not (models.Post.is_valid_id(post_id)):
        return Response(status=HTTPStatus.NOT_FOUND)

    data = request.get_json()
    user_id = data["user_id"]
    reaction = data["reaction"]

    if not models.User.is_valid_id(user_id):
        return Response(status=HTTPStatus.NOT_FOUND)

    if reaction == "":
        reaction = "like"

    USERS[user_id].total_reactions += 1
    POSTS[post_id].reactions.append(reaction)
    return Response(status=HTTPStatus.OK)
