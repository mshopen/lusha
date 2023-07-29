from selenium import webdriver
from selenium.common import WebDriverException

from api_utils import add_product_to_cart
from selenium_utils import add_products_to_cart, \
    validate_cart, place_order_and_validate, sign_up_to_demo_blaze, login_to_demo_blaze
import random
import string
import pytest


def _generate_random_string() -> str:
    characters = string.ascii_letters
    return ''.join(random.choice(characters) for i in range(8))
class TestDemo:

    username: str = _generate_random_string()
    password: str = _generate_random_string()
    basic_url: str = "https://www.demoblaze.com/"
    base_api_url = "https://api.demoblaze.com"

    @pytest.fixture(scope="session")
    def driver(self):
        driver = webdriver.Chrome()
        driver.maximize_window()
        yield driver

    @pytest.fixture(scope="class", autouse=True)
    def sign_up(self, driver):
        # driver = webdriver.Chrome()
        # driver.maximize_window()
        driver.get(self.basic_url)
        sign_up_to_demo_blaze(driver, self.username, self.password)
        yield
        driver.close()

    def test_ui(self, driver):
        try:
            login_to_demo_blaze(driver, self.username, self.password)
            products_to_buy = ["Nexus 6", "MacBook Pro"]
            add_products_to_cart(driver, products_to_buy)
            total_price = validate_cart(driver, products_to_buy)
            place_order_and_validate(driver, total_to_pay=total_price, name=self.username, country='Israel',
                                     credit_card='123456', month='09', year='2026')
            print("UI Test passed!")
        except WebDriverException as wde:
            pytest.fail(wde.msg)

    @pytest.mark.parametrize("product_name", [pytest.param("Nexus 6")])
    def test_api(self, product_name):
        add_product_to_cart(self.base_api_url, self.username, self.password, product_name)



    # if __name__ == "__main__":
    #     username = _generate_random_string()
    #     password = _generate_random_string()
    #     driver = webdriver.Chrome()
    #     ui_test(driver, username, password)
    #     base_url ="https://api.demoblaze.com"
    #     add_product_to_cart(base_url, username, password, "Nexus 6")



