from dataclasses import dataclass

import requests
import json
import base64
import uuid


@dataclass
class ProductData:
    id: int
    name: str
    price: int


def login(base_url, user, password) -> str:
    login_endpoint = "/login"
    login_data = {
        "username": user,
        "password": base64.b64encode(password.encode('ascii')).decode()
    }

    login_response = requests.post(base_url + login_endpoint, data=json.dumps(login_data),
                                   headers={'content-type': 'application/json'})
    if login_response.status_code == 200:
        try:
            token = login_response.json().split("Auth_token: ")[1]
            return token
        except Exception as ex:
            print("Could not extract token!")
            raise ex
    else:
        print("Login failed.")
        return None


def add_product_to_cart(base_url, token, product_name):
    add_to_cart_endpoint = "/addtocart"
    if not token:
        print("Could not get token!")
        return
    try:
        product_id = get_product_data_by_name(base_url, product_name)['id']
    except Exception as ex:
        print(f"Product Id not found for product: {product_name}")
        raise ex

    request_data = {
        "id": str(uuid.uuid4()),
        "cookie": token,
        "prod_id": product_id,
        "flag": True
    }

    cart_response = requests.post(base_url + add_to_cart_endpoint, data=json.dumps(request_data),
                                  headers={'content-type': 'application/json'})
    if cart_response.status_code == 200:
        print(f"Product with ID {product_id} added to cart successfully.")
    else:
        print(f"Failed to add product to cart. Message was:  {cart_response.text}")
        return


def get_product_data_by_name(base_url, produce_name: str) -> dict:
    entries_endpoint = "/entries"
    entries_response = requests.get(base_url + entries_endpoint)
    if entries_response.status_code != 200:
        print(f"Failed to get items! Message was: {entries_response.text}")
        return None
    for item in entries_response.json()["Items"]:
        if item['title'] == produce_name:
            return item
    return None


def get_product_data_by_id(base_url, produce_id: int) -> dict:
    entries_endpoint = "/entries"
    entries_response = requests.get(base_url + entries_endpoint)
    if entries_response.status_code != 200:
        print(f"Failed to get items! Message was: {entries_response.text}")
        return None
    for item in entries_response.json()["Items"]:
        if item['id'] == produce_id:
            return item
    return None


def validate_cart_product_content(base_url: str, token: str, expected_num_items: int,
                                  expected_product_data: ProductData) -> bool:
    cart_endpoint = "/viewcart"
    request_data = {
        "id": str(uuid.uuid4()),
        "cookie": token,
        "flag": True
    }
    cart_response = requests.post(base_url + cart_endpoint, data=json.dumps(request_data),
                                  headers={'content-type': 'application/json'})

    if cart_response.status_code != 200:
        print(f"Failed to get cart. Message was: {cart_response.text}")
        return False

    items = cart_response.json()['Items']
    assert expected_num_items == len(items), \
        f"Number of items in cart does not equal expected number: {expected_num_items}"

    for item in items:
        if item['prod_id'] == expected_product_data.id:
            product = get_product_data_by_id(base_url, expected_product_data.id)
            if product['price'] != expected_product_data.price:
                print(f"Product price is {product['price']}, expected {expected_product_data.price}")
                return False
            if product['title'] != expected_product_data.name:
                print(f"Product name is {product['title']}, expected {expected_product_data.name}")
                return False
            print(f"Cart validation successful for product: {expected_product_data.name}")
            return True
    print(f"Product {expected_product_data.name} was not found in cart!")
    return False
