import json
from http import HTTPStatus
from flask import request, Response
import uuid

from app import app, USERS, POSTS, models
from app.models import Status


@app.post("/posts/create")
def post_create():
    data = request.get_json()

    post_id = uuid.uuid4().int
    author_id = data["author_id"]
    text = data["text"]

    if not models.User.is_valid_id(author_id):
        return Response(status=HTTPStatus.NOT_FOUND)

    post = models.Post(post_id, author_id, text)
    USERS[author_id].posts.append(post.id)
    POSTS[post_id] = post
    response = Response(
        json.dumps(post.to_dict()),
        HTTPStatus.CREATED,
        mimetype="application/json",
    )
    return response


@app.get("/posts/<int:post_id>")
def get_post(post_id):
    if not models.Post.is_valid_id(post_id):
        return Response(status=HTTPStatus.NOT_FOUND)

    post = POSTS[post_id]
    response = Response(
        json.dumps(post.to_dict()),
        HTTPStatus.OK,
        mimetype="application/json",
    )
    return response


@app.post("/posts/delete/<int:post_id>")
def delete_post(post_id):
    if not models.Post.is_valid_id(post_id):
        return Response(status=HTTPStatus.NOT_FOUND)

    post = POSTS[post_id]
    post.status = Status.DELETED
    response = Response(
        json.dumps(post.to_dict()),
        HTTPStatus.OK,
        mimetype="application/json",
    )
    return response
