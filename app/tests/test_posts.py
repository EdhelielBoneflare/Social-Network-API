from http import HTTPStatus
import requests

from app.tests.utils import (
    create_post_payload,
    create_user,
    delete_user,
    ENDPOINT,
)


def test_post():
    author_id = create_user()

    payload = create_post_payload([author_id])
    create_response = requests.post(
        f"{ENDPOINT}/posts/create",
        json=payload,
    )
    assert create_response.status_code == HTTPStatus.CREATED
    post_data = create_response.json()
    post_id = post_data["id"]
    assert post_data["author_id"] == payload["author_id"]
    assert post_data["text"] == payload["text"]
    assert isinstance(post_data["reactions"], list) and (
        len(post_data["reactions"]) == 0
    )
    assert post_data["status"] == "active"

    get_author_response = requests.get(f"{ENDPOINT}/users/{author_id}")
    assert len(get_author_response.json()["posts"]) == 1
    assert get_author_response.json()["posts"][0] == post_id

    get_response = requests.get(f"{ENDPOINT}/posts/{post_id}")
    assert get_response.json()["author_id"] == payload["author_id"]
    assert get_response.json()["text"] == payload["text"]
    assert isinstance(get_response.json()["reactions"], list) and (
        len(post_data["reactions"]) == 0
    )
    assert get_response.json()["status"] == "active"

    delete_response = requests.post(f"{ENDPOINT}/posts/delete/{post_id}")
    assert delete_response.status_code == HTTPStatus.OK
    assert delete_response.json()["author_id"] == payload["author_id"]
    assert delete_response.json()["text"] == payload["text"]
    assert isinstance(delete_response.json()["reactions"], list)

    delete_user(author_id)
