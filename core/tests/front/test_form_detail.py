import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from core.models import Form, Question


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def required_name_form(db):
    """A published form with a single required text question."""
    form = Form.objects.create(
        title="Test Form",
        slug="test-required-field",
        is_active=True,
    )
    Question.objects.create(
        form=form,
        label="What is your name?",
        question_type="text",
        is_required=True,
        order=1,
    )
    return form


def test_mandatory_field__ok(
    selenium, live_server, required_name_form
):
    """
    Given a mandatory question "What is your name?"
    When question is replied
    Then no error is shown
    """
    # ── Given ──────────────────────────────────────────────────────────
    selenium.get(f"{live_server.url}/forms/{required_name_form.slug}/")

    # Access field via ID
    field = selenium.find_element(
        By.ID, f"question_{required_name_form.questions.first().id}"
    )

    error = selenium.find_element(By.CSS_SELECTOR, ".error-message")

    # ── When ───────────────────────────────────────────────────────────
    field.send_keys("Alice")
    field.click()

    # ── Then ───────────────────────────────────────────────────────────
    WebDriverWait(selenium, 3).until(EC.invisibility_of_element(error))
    assert not error.is_displayed()


def test_mandatory_field__error_shown(
    selenium, live_server, required_name_form
):
    """
    Given a mandatory question "What is your name?"
    When question is not replied
    Then error message is shown
    """
    # ── Given ──────────────────────────────────────────────────────────
    selenium.get(f"{live_server.url}/forms/{required_name_form.slug}/")

    # Access field by locating label = "What is your name?"
    # Then the next input
    field = selenium.find_element(
        By.XPATH,
        f"//label[normalize-space(text())='What is your name?']/following-sibling::input[1]",
    )
    error = selenium.find_element(By.CSS_SELECTOR, ".error-message")

    # Error is not displayed before user clicked the field
    assert not error.is_displayed()

    # ── When ───────────────────────────────────────────────────────────
    field.click()
    field.send_keys(Keys.TAB)  # triggers the blur event

    # ── Then ───────────────────────────────────────────────────────────
    WebDriverWait(selenium, 3).until(EC.visibility_of(error))
    assert error.is_displayed()
    assert error.text == "Mandatory field"
