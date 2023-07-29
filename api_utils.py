import requests
import json
import base64
import uuid


def add_product_to_cart(base_url, user, password, product_name):
    login_endpoint = "/login"
    cart_endpoint = "/addtocart"

    login_data = {
        "username": user,
        "password": base64.b64encode(password.encode('ascii')).decode()
    }

    login_response = requests.post(base_url + login_endpoint, data=json.dumps(login_data),
                                   headers={'content-type': 'application/json'})
    if login_response.status_code == 200:
        token = login_response.json().split("Auth_token: ")[1]
    else:
        print("Login failed.")
        return

    product_id = get_product_id(base_url, product_name)
    if not product_id:
        print("Failed to get product id!")
        return

    request_data = {
        "id": str(uuid.uuid4()),
        "cookie": token,
        "prod_id": product_id,
        "flag": True
    }

    cart_response = requests.post(base_url + cart_endpoint, data=json.dumps(request_data),
                                  headers={'content-type': 'application/json'})
    if cart_response.status_code == 200:
        print(f"Product with ID {product_id} added to cart successfully.")
    else:
        print("Failed to add product to cart.")


def get_product_id(base_url, produce_name: str) -> int:
    entries_endpoint ="/entries"
    entries_response = requests.get(base_url + entries_endpoint)
    if entries_response.status_code != 200:
        print("Failed to get items!")
        return None
    for item in entries_response.json()["Items"]:
        if item['title'] == "Nexus 6":
            return item['id']

    return None

