from django.contrib.auth.models import User
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


@pytest.fixture
def user(db):
    return User.objects.create_user(username="alice", password="password123")


def test_mandatory_field_error__ok(
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


def test_mandatory_field_error_shown(
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


def test_user_can_create_form_with_question(selenium, live_server, user):
    """
    Given a registered user
    When  they log in and submit the create form page with a question
    Then  the form and its question are persisted in the database
    """
    # ── Given: user logs in ────────────────────────────────────────────
    selenium.get(f"{live_server.url}/accounts/login/")

    selenium.find_element(By.ID, "id_username").send_keys("alice")
    selenium.find_element(By.ID, "id_password").send_keys("password123")
    selenium.find_element(By.CSS_SELECTOR, "button[type=submit]").click()

    WebDriverWait(selenium, 5).until(EC.url_contains("/forms/create/"))

    # ── When: user fills in the form title and one question ────────────
    selenium.find_element(By.ID, "id_title").send_keys("My First Form")

    # The page starts with one question row pre-filled by JS
    selenium.find_element(By.NAME, "question_label").send_keys("What is your name?")

    selenium.find_element(By.CSS_SELECTOR, "button[type=submit]").click()

    WebDriverWait(selenium, 5).until(EC.url_contains("/forms/"))

    # ── Then: form and question exist in the database ──────────────────
    form = Form.objects.get(title="My First Form")
    assert form is not None

    question = Question.objects.get(form=form, label="What is your name?")
    assert question.question_type == "text"
