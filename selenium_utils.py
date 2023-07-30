from selenium.common import TimeoutException, NoSuchElementException, WebDriverException, \
    StaleElementReferenceException
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import re

IGNORED_EXCEPTIONS = (NoSuchElementException, StaleElementReferenceException)


def driver_exception_handler(func):
    def driver_function(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            return result
        except WebDriverException as wde:
            print(wde.msg)
            raise wde

    return driver_function


def wait_for_element_visible(driver: WebDriver, element_locator: str, timeout=2, by: str = By.ID):
    element = WebDriverWait(driver, timeout).until(
        EC.visibility_of_element_located([by, element_locator]))
    return element


@driver_exception_handler
def login_to_demo_blaze(driver, username, password):
    driver.find_element(By.ID, "login2").click()
    wait_for_element_visible(driver, "logInModal")
    wait_for_element_visible(driver, "loginusername").send_keys(username)
    wait_for_element_visible(driver, "loginpassword").send_keys(password)
    driver.find_element(By.XPATH, "//button[contains(text(),'Log in')]").click()
    validate_login_successful(driver, username)


@driver_exception_handler
def sign_up_to_demo_blaze(driver, username, password):
    driver.find_element(By.ID, "signin2").click()
    sign_up_element = wait_for_element_visible(driver, "signInModal", timeout=3)
    user_text_box = wait_for_element_visible(driver, "sign-username")
    password_text_box = wait_for_element_visible(driver, "sign-password")
    user_text_box.send_keys(username)
    password_text_box.send_keys(password)
    sign_up_element.find_element(By.XPATH, "//button[contains(text(),'Sign up')]").click()
    validate_and_accept_alert(driver, "Sign up successful")


def wait_for_element_clickable(driver, element_locator: str, by=By.ID, timeout=2):
    element = WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable([by, element_locator]))
    return element


def validate_login_successful(driver: WebDriver, username: str):
    welcome_text = wait_for_element_visible(driver, "nameofuser").text
    if "Welcome" and username in welcome_text:
        print("Login successful!")
    else:
        raise Exception("Login failed!")


def validate_and_accept_alert(driver: WebDriver, success_message: str, timeout=1):
    WebDriverWait(driver, timeout).until(EC.alert_is_present(),
                                         'Timed out waiting for alert!')
    alert = driver.switch_to.alert
    if success_message in alert.text:
        alert.accept()
    else:
        raise Exception("Operation was not successful")


@driver_exception_handler
def add_product_to_cart(driver, product_name):
    go_to_home(driver)
    while True:
        WebDriverWait(driver, 5).until(EC.visibility_of_all_elements_located((By.CLASS_NAME, 'hrefch')))
        driver.implicitly_wait(5)
        try:
            product_element = WebDriverWait(driver, 3, ignored_exceptions=IGNORED_EXCEPTIONS) \
                .until(EC.presence_of_element_located((By.LINK_TEXT, product_name)))
            product_element.click()
            break
        except TimeoutException:
            try:
                wait_for_element_visible(driver, "next2", timeout=4).click()
            except TimeoutException as wde:
                print("Product not found!")
                raise wde

    wait_for_element_clickable(driver, by=By.XPATH, element_locator="//a[contains(text(),'Add to cart')]").click()
    validate_and_accept_alert(driver, "Product added")


def add_products_to_cart(driver, product_names: []):
    for product_name in product_names:
        add_product_to_cart(driver, product_name)


def go_to_home(driver):
    driver.find_element(By.XPATH, "//a[contains(text(),'Home')]").click()


@driver_exception_handler
def validate_cart(driver, product_names: []) -> int:
    wait_for_element_clickable(driver, "cartur").click()
    WebDriverWait(driver, 3, ignored_exceptions=IGNORED_EXCEPTIONS) \
        .until(EC.presence_of_all_elements_located((By.CLASS_NAME, "success")))
    assert len(product_names) == len(
        driver.find_elements(By.CLASS_NAME, "success")), "Not all expected products found in cart!"
    total_price = 0
    for product in product_names:
        try:
            driver.find_element(By.XPATH, f"//td[text() ='{product}']")
        except WebDriverException as wde:
            print('Product not found!')
            raise wde
        total_price += int(driver.find_element(By.XPATH, f"//tr[td[text()='{product}']]/td[3]").text)
    assert total_price == int(driver.find_element(By.ID, "totalp").text), print("Total price incorrect!")
    return total_price


@driver_exception_handler
def place_order_and_validate_price(driver, total_to_pay: int, name: str, credit_card: str, **kwargs):
    wait_for_element_clickable(driver, element_locator="//button[text()='Place Order']", by=By.XPATH).click()
    wait_for_element_visible(driver, "orderModal")
    if name != '' and credit_card != '':
        driver.find_element(By.ID, "name").send_keys(name)
        driver.find_element(By.ID, "card").send_keys(credit_card)
    else:
        raise Exception('Name and Card values not provided!')
    for key in kwargs:
        if key in ['country', 'city', 'month', 'year']:
            driver.find_element(By.ID, key).send_keys(kwargs[key])
    driver.find_element(By.XPATH, "//button[text()='Purchase']").click()
    purchase_text = driver.find_element(By.CLASS_NAME, "sweet-alert.showSweetAlert.visible").text
    paid_amount = int(re.findall(r'\d+', re.findall(r'Amount: \d+', purchase_text)[0])[0])
    assert total_to_pay == paid_amount, "Total paid amount is incorrect!"
