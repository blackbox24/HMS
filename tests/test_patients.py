from datetime import date

import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse

from patients.models import Patient

User = get_user_model()


@pytest.fixture
def admin_user(db):
    return User.objects.create_superuser("admin", "admin@test.local", "pass12345")


@pytest.fixture
def patient(db):
    return Patient.objects.create(
        first_name="Ama",
        last_name="Serwaa",
        date_of_birth=date(1990, 5, 1),
        gender="F",
        phone="0244000000",
    )


class TestPatientModel:
    def test_mrn_generated_on_save(self, patient):
        assert patient.mrn.startswith(f"HMS-{date.today().year}-")

    def test_mrn_unique_and_sequential(self, db):
        p1 = Patient.objects.create(
            first_name="A", last_name="B", date_of_birth=date(2000, 1, 1), gender="M"
        )
        p2 = Patient.objects.create(
            first_name="C", last_name="D", date_of_birth=date(2000, 1, 1), gender="F"
        )
        assert p1.mrn != p2.mrn
        assert int(p2.mrn.rsplit("-", 1)[1]) == int(p1.mrn.rsplit("-", 1)[1]) + 1

    def test_age_calculation(self, patient):
        assert patient.age >= 30

    def test_full_name(self, patient):
        assert patient.full_name == "Ama Serwaa"


class TestAuth:
    def test_login_with_username(self, admin_user):
        c = Client()
        resp = c.post(reverse("login"), {"username": "admin", "password": "pass12345"})
        assert resp.status_code == 302
        assert c.session.get("_auth_user_id")

    def test_login_with_email(self, admin_user):
        c = Client()
        resp = c.post(reverse("login"), {"username": "admin@test.local", "password": "pass12345"})
        assert resp.status_code == 302

    def test_login_wrong_password_rejected(self, admin_user):
        c = Client()
        resp = c.post(reverse("login"), {"username": "admin", "password": "wrong"})
        assert resp.status_code == 200  # re-renders form
        assert not c.session.get("_auth_user_id")

    def test_unauthenticated_redirected(self, client):
        resp = client.get(reverse("patient_list"))
        assert resp.status_code == 302
        assert "/accounts/login/" in resp["Location"]
