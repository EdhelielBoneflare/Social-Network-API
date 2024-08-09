from faker import Faker
from http import HTTPStatus
import random
import requests

ENDPOINT = "http://127.0.0.1:5000"


def create_user_payload():
    first_name = Faker().first_name()
    last_name = Faker().last_name()
    nickname = (first_name + last_name)[:20]
    email = Faker().ascii_email()
    payload_result = {
        "first_name": first_name,
        "last_name": last_name,
        "nickname": nickname.lower(),
        "email": email.lower(),
    }
    return payload_result


def create_user():
    create_response = requests.post(
        f"{ENDPOINT}/users/create",
        json=create_user_payload(),
    )
    assert create_response.status_code == HTTPStatus.CREATED
    return create_response.json()["id"]


def delete_user(user_id):
    delete_response = requests.post(f"{ENDPOINT}/users/delete/{user_id}")
    assert delete_response.status_code == HTTPStatus.OK


def create_post_payload(users_id):
    author_id = random.choice(users_id)
    text = ""
    payload_result = {
        "author_id": author_id,
        "text": text,
    }
    return payload_result


# authors_id - list of user_id that can be used as authors in current situation
def create_post(authors_id):
    payload = create_post_payload(authors_id)
    create_response = requests.post(
        f"{ENDPOINT}/posts/create",
        json=payload,
    )
    assert create_response.status_code == HTTPStatus.CREATED
    return create_response.json()["id"]


def delete_post(post_id):
    delete_response = requests.post(f"{ENDPOINT}/posts/delete/{post_id}")
    assert delete_response.status_code == HTTPStatus.OK


def reaction_setting(user_id, post_id, reaction):
    payload = {"user_id": user_id, "reaction": reaction}
    set_response = requests.post(
        f"{ENDPOINT}/posts/{post_id}/reaction",
        json=payload,
    )
    assert set_response.status_code == HTTPStatus.OK
