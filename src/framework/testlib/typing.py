from typing import Union

from selenium.webdriver.android.webdriver import WebDriver as AndroidWebDriver
from selenium.webdriver.blackberry.webdriver import (
    WebDriver as BlackberryWebDriver,
)
from selenium.webdriver.chrome.webdriver import WebDriver as ChromeWebDriver
from selenium.webdriver.edge.webdriver import WebDriver as EdgeWebDriver
from selenium.webdriver.firefox.webdriver import WebDriver as FirefoxWebDriver
from selenium.webdriver.ie.webdriver import WebDriver as IeWebDriver
from selenium.webdriver.opera.webdriver import WebDriver as OperaWebDriver
from selenium.webdriver.phantomjs.webdriver import (
    WebDriver as PhantomJsWebDriver,
)
from selenium.webdriver.remote.webdriver import WebDriver as RemoteWebDriver
from selenium.webdriver.safari.webdriver import WebDriver as SafariWebDriver

WebDriverT = Union[
    AndroidWebDriver,
    BlackberryWebDriver,
    ChromeWebDriver,
    EdgeWebDriver,
    FirefoxWebDriver,
    IeWebDriver,
    OperaWebDriver,
    PhantomJsWebDriver,
    RemoteWebDriver,
    SafariWebDriver,
]
