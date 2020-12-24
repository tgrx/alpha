from selenium.webdriver.common.by import By

from framework.testlib.pages import PageElement
from framework.testlib.pages import PageObject


class MainPage(PageObject):
    h1 = PageElement(By.CSS_SELECTOR, "h1")
    p = PageElement(By.CSS_SELECTOR, "p")
