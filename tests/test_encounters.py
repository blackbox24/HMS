import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.urls import reverse
from django.utils import timezone

from encounters.models import Encounter, ICD10Code
from patients.models import Patient

User = get_user_model()


@pytest.fixture
def patient(db):
    return Patient.objects.create(
        first_name="Ama", last_name="Serwaa", date_of_birth="1990-01-01",
        gender="F", phone="0244000000")


@pytest.fixture
def roles(db):
    def make(username, role):
        u = User.objects.create_user(username, f"{username}@t.local", "pass12345")
        u.groups.add(Group.objects.get(name=role))
        return u
    return make


@pytest.fixture
def encounter(db, patient, roles):
    from django.test import RequestFactory

    from encounters import services
    request = RequestFactory().post('/')
    request.user = roles('rec_t', 'Receptionist')
    return services.check_in(request, patient)


class TestCheckIn:
    def test_creates_encounter_with_queue_token(self, db, patient, roles):
        from django.test import RequestFactory

        from encounters import services
        request = RequestFactory().post('/')
        request.user = roles('rec1', 'Receptionist')
        e = services.check_in(request, patient)
        assert e.status == Encounter.Status.CHECKED_IN
        assert e.queue_token == 'O001'
        assert e.queue_number == 1

    def test_queue_numbers_increment(self, db, patient, roles):
        from django.test import RequestFactory

        from encounters import services
        request = RequestFactory().post('/')
        request.user = roles('rec1', 'Receptionist')
        services.check_in(request, patient)
        services.check_in(request, patient)
        assert Encounter.objects.count() == 2
        assert sorted(Encounter.objects.values_list('queue_number', flat=True)) == [1, 2]

    def test_check_in_view(self, client, patient, roles):
        client.force_login(roles('rec2', 'Receptionist'))
        resp = client.post(reverse('check_in'), {'patient': str(patient.pk)})
        assert resp.status_code == 302
        assert Encounter.objects.count() == 1

    def test_nurse_cannot_check_in_view_denied_or_allowed(self, client, patient, roles):
        # Nurse IS in OPD_ROLES, so allowed; a Billing Clerk is not.
        client.force_login(roles('bill1', 'Billing Clerk'))
        resp = client.post(reverse('check_in'), {'patient': str(patient.pk)})
        assert resp.status_code == 403


class TestFlow:
    def test_full_opd_flow(self, db, encounter, roles):
        from django.test import RequestFactory

        from encounters import services
        factory = RequestFactory()
        nurse = roles('nurse_f', 'Nurse')
        doctor = roles('doc_f', 'Doctor')

        # vitals
        req = factory.post('/')
        req.user = nurse
        services.record_vitals(req, encounter, bp_systolic=120, pulse=72)
        encounter.refresh_from_db()
        assert encounter.status == Encounter.Status.VITALS

        # queue
        req.user = nurse
        services.send_to_queue(req, encounter)
        encounter.refresh_from_db()
        assert encounter.status == Encounter.Status.QUEUED

        # assign
        req.user = nurse
        services.assign_doctor(req, encounter, doctor)
        encounter.refresh_from_db()
        assert encounter.status == Encounter.Status.WITH_DOCTOR
        assert encounter.doctor == doctor

        # consult — starts 24h clock
        icd = ICD10Code.objects.create(code='J00', description='Common cold')
        req.user = doctor
        services.save_consult(req, encounter, subjective='cough',
                              assessment='URI', plan='rest', icd10_ids=[icd.pk])
        encounter.refresh_from_db()
        assert encounter.status == Encounter.Status.CONSULTED
        assert encounter.diagnosis_at is not None

        # disposition
        services.dispose(req, encounter, 'DISCHARGED')
        encounter.refresh_from_db()
        assert encounter.status == Encounter.Status.DISCHARGED
        assert encounter.discharged_at is not None

    def test_invalid_transition_rejected(self, db, encounter, roles):
        from django.test import RequestFactory

        from encounters import services
        request = RequestFactory().post('/')
        request.user = roles('doc_x', 'Doctor')
        with pytest.raises(ValueError):
            services.dispose(request, encounter, 'DISCHARGED')

    def test_24h_overdue_flag(self, db, encounter, roles):
        from django.test import RequestFactory

        from encounters import services
        factory = RequestFactory()
        doctor = roles('doc_o', 'Doctor')

        req = factory.post('/')
        req.user = doctor
        encounter.doctor = doctor
        encounter.status = Encounter.Status.WITH_DOCTOR
        encounter.save()
        services.save_consult(req, encounter, assessment='x')
        encounter.refresh_from_db()
        assert not encounter.is_24h_overdue

        Encounter.objects.filter(pk=encounter.pk).update(
            diagnosis_at=timezone.now() - timezone.timedelta(hours=25))
        encounter.refresh_from_db()
        assert encounter.is_24h_overdue


class TestViews:
    def test_opd_board_requires_role(self, client, db):
        user = User.objects.create_user('plain2', 'p2@t.local', 'pass12345')
        client.force_login(user)
        assert client.get(reverse('opd_board')).status_code == 403

    def test_encounter_detail_renders(self, client, encounter, roles):
        client.force_login(roles('nurse_d', 'Nurse'))
        resp = client.get(reverse('encounter_detail', args=[encounter.pk]))
        assert resp.status_code == 200
        assert encounter.queue_token.encode() in resp.content
