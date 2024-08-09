from http import HTTPStatus
import pytest
import requests

from app.tests.utils import (
    create_post,
    create_user,
    delete_user,
    delete_post,
    ENDPOINT,
)


@pytest.mark.parametrize(
    "reaction",
    [
        "ok",
        "reaction",
        "",
    ],
)
def test_set_reaction(reaction):
    user_id = create_user()
    post_id = create_post([user_id])
    payload = {"user_id": user_id, "reaction": reaction}
    set_response = requests.post(
        f"{ENDPOINT}/posts/{post_id}/reaction",
        json=payload,
    )
    assert set_response.status_code == HTTPStatus.OK

    get_user_response = requests.get(f"{ENDPOINT}/users/{user_id}")
    assert get_user_response.json()["total_reactions"] == 1

    get_post_response = requests.get(f"{ENDPOINT}/posts/{post_id}")
    assert isinstance(get_post_response.json()["reactions"], list)
    assert len(get_post_response.json()["reactions"]) == 1
    if reaction == "":
        assert get_post_response.json()["reactions"][0] == "like"
    else:
        assert get_post_response.json()["reactions"][0] == reaction

    delete_user(user_id)
    delete_post(post_id)
