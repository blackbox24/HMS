import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.urls import reverse

User = get_user_model()


@pytest.fixture
def nurse(db):
    user = User.objects.create_user("nurse1", "nurse@test.local", "pass12345")
    user.groups.add(Group.objects.get(name="Nurse"))
    return user


@pytest.fixture
def receptionist(db):
    user = User.objects.create_user("rec1", "rec@test.local", "pass12345")
    user.groups.add(Group.objects.get(name="Receptionist"))
    return user


@pytest.fixture
def logged_in(client):
    def _login(user):
        client.force_login(user)
        return client

    return _login


class TestRoleRequired:
    def test_receptionist_can_view_patients(self, logged_in, receptionist):
        resp = logged_in(receptionist).get(reverse("patient_list"))
        assert resp.status_code == 200

    def test_user_without_role_forbidden(self, logged_in, db):
        nobody = User.objects.create_user("plain", "p@test.local", "pass12345")
        resp = logged_in(nobody).get(reverse("patient_list"))
        assert resp.status_code == 403

    def test_admin_group_bypasses_role_check(self, logged_in, db):
        admin = User.objects.create_user("boss", "b@test.local", "pass12345")
        admin.groups.add(Group.objects.get(name="Administrator"))
        resp = logged_in(admin).get(reverse("patient_list"))
        assert resp.status_code == 200

    def test_superuser_bypasses(self, logged_in, db):
        su = User.objects.create_superuser("root", "r@test.local", "pass12345")
        resp = logged_in(su).get(reverse("patient_list"))
        assert resp.status_code == 200
