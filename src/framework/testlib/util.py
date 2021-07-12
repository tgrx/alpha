from datetime import datetime
from functools import wraps

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from framework import dirs
from framework.testlib.pages import PageObject


def screenshot_on_failure(test):
    @wraps(test)
    def decorated_test(browser, request, *args, **kwargs):
        try:
            test(browser, request, *args, **kwargs)
        except Exception:
            ts = datetime.now().strftime(f"%Y.%m.%d.%H.%M.%S")
            test_name = f"{request.module.__name__}.{test.__name__}"
            png = f"{test_name}.{ts}.png"
            html = f"{test_name}.{ts}.html"
            png_path = (dirs.DIR_TEST_ARTIFACTS / png).resolve()
            html_path = (dirs.DIR_TEST_ARTIFACTS / html).resolve()
            with html_path.open("w") as _dst:
                _dst.write(browser.page_source)
            browser.save_screenshot(png_path.as_posix())
            raise

    return decorated_test


def validate_redirect(page: PageObject, url: str):
    try:
        redirected = WebDriverWait(page.browser, 4).until(
            expected_conditions.url_to_be(url)
        )
        assert redirected
    except TimeoutException as err:
        raise AssertionError(
            f"no redirect: {page.browser.current_url}"
        ) from err
