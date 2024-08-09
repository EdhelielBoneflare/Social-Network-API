import json
from http import HTTPStatus
from flask import request, Response, url_for
import matplotlib.pyplot as plt
import uuid

from app import app, USERS, POSTS, models
from app.models import Status


@app.post("/users/create")
def user_create():
    data = request.get_json()

    user_id = uuid.uuid4().int
    first_name = data["first_name"]
    last_name = data["last_name"]
    nickname = data["nickname"].lower()
    email = data["email"].lower()
    if not models.User.is_valid_nickname(nickname):
        return Response(status=HTTPStatus.BAD_REQUEST)
    if not models.User.is_valid_email(email):
        return Response(status=HTTPStatus.BAD_REQUEST)

    for u_id in USERS:
        if (USERS[u_id].email == email) and (USERS[u_id].status != Status.DELETED):
            return Response(
                "User with this email already exists", status=HTTPStatus.BAD_REQUEST
            )
        if (USERS[u_id].nickname == nickname) and (
            USERS[u_id].status != Status.DELETED
        ):
            return Response(
                "User with this nickname already exists", status=HTTPStatus.BAD_REQUEST
            )

    user = models.User(user_id, first_name, last_name, nickname, email)
    USERS[user_id] = user
    response = Response(
        json.dumps(user.to_dict()),
        HTTPStatus.CREATED,
        mimetype="application/json",
    )
    return response


@app.get("/users/<int:user_id>")
def get_user(user_id):
    if not (models.User.is_valid_id(user_id)):
        return Response(status=HTTPStatus.NOT_FOUND)

    user = USERS[user_id]
    response = Response(
        json.dumps(user.to_dict()),
        HTTPStatus.OK,
        mimetype="application/json",
    )
    return response


@app.get("/users/<int:user_id>/posts")
def get_users_posts(user_id):
    data = request.get_json()
    if not (models.User.is_valid_id(user_id)):
        return Response(status=HTTPStatus.NOT_FOUND)

    user = USERS[user_id]
    sort_style = data["sort"]
    if sort_style == "asc":
        user.posts = sorted(
            user.posts, key=lambda post_id: len(POSTS[post_id].reactions)
        )
    elif sort_style == "desc":
        user.posts = sorted(
            user.posts,
            reverse=True,
            key=lambda post_id: len(POSTS[post_id].reactions),
        )
    else:
        return Response(status=HTTPStatus.BAD_REQUEST)

    response = Response(
        json.dumps(
            {"posts": [POSTS[post_id].to_dict() for post_id in USERS[user_id].posts]}
        ),
        HTTPStatus.OK,
        mimetype="application/json",
    )
    return response


@app.get("/users/leaderboard")
def get_leaderboard():
    data = request.get_json()

    leaderboard_type = data["type"]

    if leaderboard_type == "list":
        sort_style = data["sort"]
        if (sort_style == "asc") or (sort_style == "desc"):
            leaderboard = models.User.get_leaderboard(sort_style)
        else:
            return Response(status=HTTPStatus.BAD_REQUEST)
        response = Response(
            json.dumps({"users": leaderboard}),
            HTTPStatus.OK,
            mimetype="application/json",
        )
        return response
    elif leaderboard_type == "graph":
        leaderboard = models.User.get_leaderboard()
        fig, ax = plt.subplots()
        fig.subplots_adjust(left=0.18)
        user_names = [f'{user["nickname"]}' for user in leaderboard]
        reacts = [user["total_reactions"] for user in leaderboard]
        ax.barh(user_names, reacts, align="center")
        ax.set_xlabel("total reactions")
        ax.set_title("Leaderboard")
        plt.savefig("app/static/users_leaderboard.png")
        return Response(
            f"""<img src= {url_for('static', filename='users_leaderboard.png')}">""",
            status=HTTPStatus.OK,
            mimetype="text/html",
        )
    else:
        return Response(status=HTTPStatus.BAD_REQUEST)


@app.post("/users/delete/<int:user_id>")
def delete_user(user_id):
    if not models.User.is_valid_id(user_id):
        return Response(status=HTTPStatus.NOT_FOUND)

    user = USERS[user_id]
    user.status = Status.DELETED
    response = Response(
        json.dumps(user.to_dict()),
        HTTPStatus.OK,
        mimetype="application/json",
    )
    return response
