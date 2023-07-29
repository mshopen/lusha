from selenium import webdriver

from api_utils import add_product_to_cart
from selenium_utils import add_products_to_cart, \
    validate_cart, place_order_and_validate, sign_up_to_demo_blaze, login_to_demo_blaze
import random
import string


def _generate_random_string() -> str:
    characters = string.ascii_letters
    return ''.join(random.choice(characters) for i in range(8))


def ui_test(driver, username, password):
    try:
        driver.maximize_window()
        driver.get("https://www.demoblaze.com/")
        sign_up_to_demo_blaze(driver, username, password)
        login_to_demo_blaze(driver, username, password)
        products_to_buy = ["Nexus 6", "MacBook Pro"]
        add_products_to_cart(driver, products_to_buy)
        total_price = validate_cart(driver, products_to_buy)
        place_order_and_validate(driver, total_to_pay=total_price, name=username, country='Israel',
                                 credit_card='123456', month='09', year='2026')
        print("UI Test passed!")
    except Exception as ex:
        print('Operation failed!')


if __name__ == "__main__":
    username = _generate_random_string()
    password = _generate_random_string()
    # driver = webdriver.Chrome()
    # ui_test(driver, username, password)
    base_url ="https://api.demoblaze.com"
    product_name = "Nexus 6"
    add_product_to_cart(base_url, "mshopen", "mishmish1", product_name)



