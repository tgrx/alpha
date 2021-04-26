import pytest

from framework.config import settings
from framework.testlib.util import screenshot_on_failure
from tests.functional.pages import MainPage


@pytest.mark.functional
@screenshot_on_failure
def test(browser, request):
    page = MainPage(browser, settings.TEST_SERVICE_URL)

    validate_title(page)
    validate_content(page)


def validate_title(page: MainPage):
    assert page.title == "Alpha"


def validate_content(page: MainPage):
    assert page.h1.tag_name == "h1"
    assert page.h1.text == "Project Alpha"
    assert page.p.tag_name == "p"
    assert page.p.text == "This is a template project."

    html = page.html
    assert "<hr>" in html
