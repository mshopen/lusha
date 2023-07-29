import requests
import json
import base64

def add_product_to_cart(base_url, user, password,product_id):
    login_endpoint = "/login"
    cart_endpoint = "/addtocart"


    login_data = {
        "username": user,
        "password": base64.b64encode(password.encode('ascii')).decode()
    }

    # Replace with the product ID you want to add to the cart
    product_data = {
        "id": product_id
    }

    login_response = requests.post(base_url + login_endpoint, data=json.dumps(login_data), headers={'content-type': 'application/json'})
    if login_response.status_code == 200:
        token = login_response.json().split("Auth_token: ")[1]
    else:
        print("Login failed.")
        return

    # product_data =
    #     {
    #      "prod_id": "2", "flag": "false"
    #     }

    cart_response = requests.post(base_url + cart_endpoint, data=product_data, headers=headers)
    if cart_response.status_code == 201:
        print(f"Product with ID {product_id} added to cart successfully.")
    else:
        print("Failed to add product to cart.")