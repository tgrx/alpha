import abc

from selenium import webdriver

from framework import config

_browser_factories = {}


class _BrowserFactoryMeta(abc.ABCMeta):
    def __new__(mcs, name, bases, attrs):
        cls = super().__new__(mcs, name, bases, attrs)
        browser = attrs.get("BROWSER")
        if browser:
            global _browser_factories
            _browser_factories[browser] = cls

        return cls


class BrowserFactory(metaclass=_BrowserFactoryMeta):
    @abc.abstractmethod
    def build(self):
        raise NotImplementedError

    @classmethod
    def get_factory(cls) -> "BrowserFactory":
        browser_name = config.TEST_BROWSER
        factory_cls = _browser_factories.get(browser_name)
        if not factory_cls:
            raise RuntimeError(
                f'no factory for test browser "{browser_name}" implemented'
            )
        factory = factory_cls()
        return factory


class _ChromeFactory(BrowserFactory):
    BROWSER = "chrome"

    def build(self):
        options = webdriver.ChromeOptions()
        if config.TEST_BROWSER_HEADLESS:
            options.add_argument("headless")

        browser = webdriver.Chrome(options=options)
        browser.implicitly_wait(4)

        return browser


class _FirefoxFactory(BrowserFactory):
    BROWSER = "firefox"

    def build(self):
        options = webdriver.FirefoxOptions()
        options.headless = config.TEST_BROWSER_HEADLESS

        browser = webdriver.Firefox(options=options)
        browser.implicitly_wait(4)

        return browser


__all__ = [
    BrowserFactory.__name__,
]
