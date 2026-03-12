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


def test_mandatory_field_error_shown_on_blur(
    selenium, live_server, required_name_form
):
    # ── Given ──────────────────────────────────────────────────────────
    selenium.get(f"{live_server.url}/forms/{required_name_form.slug}/")

    field = selenium.find_element(By.ID, f"question_{required_name_form.questions.first().id}")
    error = selenium.find_element(By.CSS_SELECTOR, ".error-message")

    assert not error.is_displayed()

    # ── When ───────────────────────────────────────────────────────────
    field.click()
    field.send_keys(Keys.TAB)  # triggers the blur event

    # ── Then ───────────────────────────────────────────────────────────
    WebDriverWait(selenium, 3).until(EC.visibility_of(error))
    assert error.is_displayed()
    assert error.text == "Mandatory field"

def test_mandatory_field_error_hidden_after_typing(
    selenium, live_server, required_name_form
):
    """Regression: once the user types something, the error disappears."""
    selenium.get(f"{live_server.url}/forms/{required_name_form.slug}/")

    field = selenium.find_element(By.ID, f"question_{required_name_form.questions.first().id}")
    error = selenium.find_element(By.CSS_SELECTOR, ".error-message")

    # Trigger the error first
    field.click()
    field.send_keys(Keys.TAB)
    WebDriverWait(selenium, 3).until(EC.visibility_of(error))
    assert error.is_displayed()

    # Type something → error must vanish
    field.click()
    field.send_keys("Alice")
    WebDriverWait(selenium, 3).until(EC.invisibility_of_element(error))
    assert not error.is_displayed()
