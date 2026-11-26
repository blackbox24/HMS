import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import Client
from django.urls import reverse

from core.models import PasswordResetRequest

User = get_user_model()


@pytest.fixture
def staff(db):
    user = User.objects.create_user("nurse2", "n2@test.local", "oldpass123")
    user.groups.add(Group.objects.get(name="Nurse"))
    return user


@pytest.fixture
def admin_staff(db):
    user = User.objects.create_user("admin2", "a2@test.local", "adminpass123", is_staff=True)
    return user


def _login(client, username, password):
    resp = client.post(reverse("login"), {"username": username, "password": password})
    assert resp.status_code == 302
    return client


class TestPasswordResetRequest:
    def test_forgot_password_creates_request(self, staff):
        c = Client()
        resp = c.post(reverse("password_reset_request"), {"username": "nurse2"})
        assert resp.status_code == 302
        assert PasswordResetRequest.objects.filter(user=staff, status="PENDING").exists()

    def test_forgot_password_unknown_user_no_record(self, db):
        c = Client()
        c.post(reverse("password_reset_request"), {"username": "ghost"})
        assert not PasswordResetRequest.objects.exists()

    def test_duplicate_request_within_window_blocked(self, staff):
        c = Client()
        c.post(reverse("password_reset_request"), {"username": "nurse2"})
        c.post(reverse("password_reset_request"), {"username": "nurse2"})
        assert PasswordResetRequest.objects.filter(user=staff).count() == 1


class TestAdminIssuesTempPassword:
    def test_admin_can_issue_temp_password(self, admin_staff, staff):
        req = PasswordResetRequest.objects.create(user=staff)
        c = _login(Client(), "admin2", "adminpass123")
        resp = c.post(reverse("password_reset_issue", args=[req.pk]))
        assert resp.status_code == 302

        staff.refresh_from_db()
        req.refresh_from_db()
        assert staff.must_change_password is True
        assert req.status == "COMPLETED"
        assert req.handled_by == admin_staff

    def test_non_staff_cannot_issue(self, staff):
        req = PasswordResetRequest.objects.create(user=staff)
        c = _login(Client(), "nurse2", "oldpass123")
        resp = c.post(reverse("password_reset_issue", args=[req.pk]))
        assert resp.status_code == 403


class TestForcePasswordChange:
    def test_flagged_user_redirected_to_change_password(self, staff):
        staff.must_change_password = True
        staff.save(update_fields=["must_change_password"])
        c = _login(Client(), "nurse2", "oldpass123")
        resp = c.get(reverse("dashboard"))
        assert resp.status_code == 302
        assert "/password-change/" in resp["Location"]

    def test_change_password_clears_flag(self, staff):
        staff.must_change_password = True
        staff.save(update_fields=["must_change_password"])
        c = _login(Client(), "nurse2", "oldpass123")
        # middleware allows the change-password page itself
        resp = c.get(reverse("password_change"))
        assert resp.status_code == 200

        resp = c.post(
            reverse("password_change"),
            {
                "old_password": "oldpass123",
                "new_password1": "newpass4567",
                "new_password2": "newpass4567",
            },
        )
        assert resp.status_code == 302
        staff.refresh_from_db()
        assert staff.must_change_password is False
        assert staff.check_password("newpass4567")
