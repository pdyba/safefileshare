from datetime import datetime, date
from dateutil.tz import tzutc

from django.conf import settings
from django.http import HttpResponseRedirect
from django.test import RequestFactory
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.messages import get_messages

import pytest

from safefileshare.file.forms import GetSecretForm
from safefileshare.file.views import (
    add_secret,
    FileDetailView,
    FileUploadView,
    SecretAPICreateView,
    SecretAPIDetailsView,
    increase_counter,
)
from safefileshare.file.models import SafeSecret, SecretCounter

pytestmark = pytest.mark.django_db


class TestIncreaseCounter:
    def test_increase_counter(
        self, user: settings.AUTH_USER_MODEL, request_factory: RequestFactory
    ):
        increase_counter(link=1)
        today = str(date.today())
        counter = SecretCounter.objects.get(date=today)
        assert counter.links == 1
        assert counter.downloads == 0
        increase_counter(file=1)
        counter = SecretCounter.objects.get(date=today)
        assert counter.downloads == 1
        assert counter.links == 1


class TestAddSecret:
    def test_add_secret_link(
        self, user: settings.AUTH_USER_MODEL, request_factory: RequestFactory
    ):
        request = request_factory.get("/fake-url/")
        request.user = user
        mock_data = {"secret_link": "http://wp.pl", "secret_password": "pass123"}
        resp = add_secret(mock_data, user)
        assert resp.startswith("/file/~api/")
        uuid = resp.lstrip("/file/~api/").rstrip("/")
        print(uuid, resp)
        data = SafeSecret.objects.get(secret_link=uuid)
        assert data.link == mock_data["secret_link"]
        assert data.password_hash != mock_data["secret_password"]

    def test_add_secret_file(
        self, user: settings.AUTH_USER_MODEL, request_factory: RequestFactory
    ):
        request = request_factory.get("/fake-url/")
        request.user = user
        file_name = "xxx.test"
        with open("./" + file_name) as fp:
            mock_data = {"secret_file": fp, "secret_password": "pass123"}
            resp = add_secret(mock_data, user)
            assert resp.startswith("/file/~api/")
            uuid = resp.lstrip("/file/~api/").rstrip("/")
            data = SafeSecret.objects.get(secret_link=uuid)
            assert data.file == "/media/" + file_name
            assert data.password_hash != mock_data["secret_password"]


class TestFileDetailView:
    @pytest.fixture(autouse=True)
    def setUp(self, user: settings.AUTH_USER_MODEL, request_factory: RequestFactory):
        self.mock_data = {"secret_link": "http://wp.pl", "secret_password": "pass123"}
        resp = add_secret(self.mock_data, user)
        self.uuid = resp.lstrip("/file/~api/").rstrip("/")

        request = request_factory.post("/file/{}".format(self.uuid))
        request.user = user

        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()
        messages = FallbackStorage(request)
        setattr(request, "_messages", messages)
        self.request = request

    def test_post_happy(self):
        self.request.POST = {"password": "pass123"}
        resp = FileDetailView.as_view()(self.request, secret_link=self.uuid)
        assert isinstance(resp, HttpResponseRedirect)
        print(dir(resp))
        assert resp.status_code == 302
        assert resp.url == self.mock_data["secret_link"]

    def test_post_unhappy_pass(self):
        self.request.POST = {"password": "aaa123"}
        resp = FileDetailView.as_view()(self.request, secret_link=self.uuid)
        messages = list(get_messages(resp.context_data["view"].request))
        assert len(messages) == 1
        assert messages[0].message == "Wrong Password"

    def test_post_unhappy_date(self):
        self.request.POST = {"password": "aaa123"}
        secret = SafeSecret.objects.get(secret_link=self.uuid)
        secret.upload_date = datetime(year=2010, month=1, day=1, tzinfo=tzutc())
        secret.save()
        resp = FileDetailView.as_view()(self.request, secret_link=self.uuid)
        messages = list(get_messages(resp.context_data["view"].request))
        assert len(messages) == 1
        assert messages[0].message == "Link expired"

    def test_get_context_data(self):
        self.request.GET = ""
        resp = FileDetailView.as_view()(self.request, secret_link=self.uuid)
        print(dir(resp))
        assert resp.context_data["form"] == GetSecretForm


class TestFileUploadView:
    @pytest.fixture(autouse=True)
    def setUp(self, user: settings.AUTH_USER_MODEL, request_factory: RequestFactory):
        self.view = FileUploadView()
        self.mock_data = {"secret_link": "http://wp.pl", "secret_password": "pass123"}
        resp = add_secret(self.mock_data, user)
        self.uuid = resp.lstrip("/file/~api/").rstrip("/")

        request = request_factory.post("/file/{}".format(self.uuid))
        request.user = user

        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()
        messages = FallbackStorage(request)
        setattr(request, "_messages", messages)
        self.request = request

    def test_get_success_url(self):
        assert self.view.get_success_url() == "/file/"

    def test_get_fail_url(self):
        assert self.view.get_fail_url() == "/file/~upload/"


class TestSecretAPICreateView:
    def test_post(
        self, user: settings.AUTH_USER_MODEL, request_factory: RequestFactory
    ):
        request = request_factory.post("/file/~api/~upload")
        request.user = user
        request.method = "post"
        request._dont_enforce_csrf_checks = True

        request.data = {"secret_link": "http://wp.pl", "secret_password": "pass123"}
        resp = SecretAPICreateView().post(request)
        assert resp.data["link"].startswith("http://testserver/file/~api/")

        request.data = {"secret_password": "pass123"}
        resp = SecretAPICreateView().post(request)
        assert resp.data["error"] == "You need to provide file or link, but not both."
        request.data = {
            "secret_link": "http://wp.pl",
            "secret_password": "pass123",
            "secret_file": "./xxx.test",
        }
        resp = SecretAPICreateView().post(request)
        assert resp.data["error"] == "You need to provide file or link, but not both."


class TestSecretAPIDetailsView:
    def test_post(
        self, user: settings.AUTH_USER_MODEL, request_factory: RequestFactory
    ):
        mock_data = {"secret_link": "http://wp.pl", "secret_password": "pass123"}
        resp = add_secret(mock_data, user)
        uuid = resp.lstrip("/file/~api/").rstrip("/")

        request = request_factory.post("/file/~api/{}".format(uuid))
        request.user = user
        request._dont_enforce_csrf_checks = True
        # happy
        request.data = {"password": "pass123"}
        resp = SecretAPIDetailsView().post(request, secret_link=uuid)
        assert resp.data.get("link"), resp.data
        # unhappy
        request.data = {"password": "xxx123"}
        resp = SecretAPIDetailsView().post(request, secret_link=uuid)
        assert resp.data["error"] == "Wrong Password", resp.data
