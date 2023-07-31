from selenium import webdriver
from selenium.common import WebDriverException
from api_utils import add_product_to_cart, validate_cart_product_content, login, ProductData
from selenium_utils import add_products_to_cart, \
    validate_cart, place_order_and_validate_price, sign_up_to_demo_blaze, login_to_demo_blaze, log_out, OrderData
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
        driver.delete_all_cookies()
        driver.maximize_window()
        yield driver
        driver.quit()

    @pytest.fixture(scope="class", autouse=True)
    def sign_up(self, driver):
        driver.get(self.basic_url)
        sign_up_to_demo_blaze(driver, self.username, self.password)
        yield

    def test_ui(self, driver):
        try:
            login_to_demo_blaze(driver, self.username, self.password)
            products_to_buy = ["Nexus 6", "MacBook Pro"]
            add_products_to_cart(driver, products_to_buy)
            total_price = validate_cart(driver, products_to_buy)
            order_data = OrderData(name=self.username, country='Israel', card='123456', month='09', year='2026')
            place_order_and_validate_price(driver, total_price, order_data)
            print("UI Test passed!")
        except WebDriverException as wde:
            pytest.fail(wde.msg)

    @pytest.mark.parametrize("product_data", [pytest.param(ProductData(3, "Nexus 6", 650), id="Nexus 6")])
    def test_api(self, product_data):
        token = login(self.base_api_url, self.username, self.password)
        add_product_to_cart(self.base_api_url, token, product_data.name)
        assert validate_cart_product_content(self.base_api_url, token, 1, product_data)
