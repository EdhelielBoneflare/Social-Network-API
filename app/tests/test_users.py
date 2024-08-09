import random
from http import HTTPStatus
import pytest
import requests

from app.models import Status
from app.tests.utils import (
    create_user_payload,
    create_user,
    delete_user,
    create_post,
    reaction_setting,
    delete_post,
    ENDPOINT,
)


# create, get, delete user test
def test_user_create():
    payload = create_user_payload()
    create_response = requests.post(
        f"{ENDPOINT}/users/create",
        json=payload,
    )
    assert create_response.status_code == HTTPStatus.CREATED
    user_data = create_response.json()
    user_id = user_data["id"]
    assert user_data["first_name"] == payload["first_name"]
    assert user_data["last_name"] == payload["last_name"]
    assert user_data["nickname"] == payload["nickname"].lower()
    assert user_data["email"] == payload["email"].lower()
    assert user_data["status"] == Status.ACTIVE.value

    get_response = requests.get(f"{ENDPOINT}/users/{user_id}")
    get_data = get_response.json()
    assert get_data["first_name"] == payload["first_name"]
    assert get_data["last_name"] == payload["last_name"]
    assert get_data["nickname"] == payload["nickname"].lower()
    assert get_data["email"] == payload["email"].lower()
    assert get_data["status"] == Status.ACTIVE.value

    delete_response = requests.post(f"{ENDPOINT}/users/delete/{user_id}")
    delete_data = delete_response.json()
    assert delete_response.status_code == HTTPStatus.OK
    assert delete_data["first_name"] == payload["first_name"]
    assert delete_data["last_name"] == payload["last_name"]
    assert delete_data["nickname"] == payload["nickname"].lower()
    assert delete_data["email"] == payload["email"].lower()
    assert delete_data["status"] == Status.DELETED.value


def test_user_create_wrong_data():
    payload_nickname = create_user_payload()
    payload_nickname["nickname"] = "super@human"
    create_response = requests.post(
        f"{ENDPOINT}/users/create",
        json=payload_nickname,
    )
    assert create_response.status_code == HTTPStatus.BAD_REQUEST

    payload_email = create_user_payload()
    payload_email["email"] = "email.com"
    create_response = requests.post(
        f"{ENDPOINT}/users/create",
        json=payload_email,
    )
    assert create_response.status_code == HTTPStatus.BAD_REQUEST


@pytest.mark.parametrize("sort_style", ["asc", "desc", ""])
def test_get_users_posts(sort_style):
    user_id = create_user()

    number_of_posts = random.randint(0, 5)
    test_posts = []
    for _ in range(number_of_posts):
        post_id = create_post([user_id])
        test_posts.append(post_id)

    get_response = requests.get(
        f"{ENDPOINT}/users/{user_id}/posts",
        json={"sort": sort_style},
    )

    if (sort_style != "asc") and (sort_style != "desc"):
        assert get_response.status_code == HTTPStatus.BAD_REQUEST
    else:
        assert get_response.status_code == HTTPStatus.OK
        assert isinstance(get_response.json()["posts"], list)
        assert len(get_response.json()["posts"]) == number_of_posts
        if sort_style == "asc":
            for i in range(1, number_of_posts):
                assert len(get_response.json()["posts"][i - 1]["reactions"]) <= len(
                    get_response.json()["posts"][i]["reactions"]
                )
        else:
            for i in range(1, number_of_posts):
                assert len(get_response.json()["posts"][i - 1]["reactions"]) >= len(
                    get_response.json()["posts"][i]["reactions"]
                )
    delete_user(user_id)
    for p_id in test_posts:
        delete_post(p_id)


@pytest.mark.parametrize(
    "board_type, sort_style",
    [("list", "asc"), ("list", "desc"), ("graph", ""), ("text", ""), ("list", "")],
)
def test_get_user_leaderboard(board_type, sort_style):
    number_of_users = random.randint(2, 5)
    test_users = []
    for _ in range(number_of_users):
        user_id = create_user()
        test_users.append(user_id)

    post_id = create_post(test_users)
    number_of_reactions = random.randint(2, 20)
    for _ in range(number_of_reactions):
        reaction_setting(random.choice(test_users), post_id, "react")

    payload = {"type": board_type}
    if board_type == "list":
        payload["sort"] = sort_style

    leaderboard_response = requests.get(
        f"{ENDPOINT}/users/leaderboard",
        json=payload,
    )

    if board_type == "list":
        if sort_style == "asc" or sort_style == "desc":
            assert leaderboard_response.status_code == HTTPStatus.OK
            assert isinstance(leaderboard_response.json()["users"], list)
            assert len(leaderboard_response.json()["users"]) == number_of_users
            if sort_style == "desc":
                for i in range(1, number_of_users):
                    assert (
                        leaderboard_response.json()["users"][i - 1]["total_reactions"]
                        >= leaderboard_response.json()["users"][i]["total_reactions"]
                    )
            elif sort_style == "asc":
                for i in range(1, number_of_users):
                    assert (
                        leaderboard_response.json()["users"][i - 1]["total_reactions"]
                        <= leaderboard_response.json()["users"][i]["total_reactions"]
                    )
        else:
            assert leaderboard_response.status_code == HTTPStatus.BAD_REQUEST
    elif board_type == "graph":
        # leaderboard creation and right sorting is checked in "list" test, so here we just check that this is a graph
        assert leaderboard_response.status_code == HTTPStatus.OK
        assert (
            leaderboard_response.content == b'<img src= /static/users_leaderboard.png">'
        )
    else:
        assert leaderboard_response.status_code == HTTPStatus.BAD_REQUEST

    for user_id in test_users:
        delete_user(user_id)
    delete_post(post_id)
