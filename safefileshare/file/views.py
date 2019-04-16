from datetime import datetime, date
from dateutil.tz import tzutc

from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files.storage import FileSystemStorage
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import DetailView, ListView, FormView

from rest_framework import generics
from rest_framework import serializers
from rest_framework.response import Response

from safefileshare.file.forms import UploadFileForm
from safefileshare.file.forms import GetSecretForm
from safefileshare.file.models import SafeSecret, SecretCounter

UPLOAD_SECRET_ERROR = "You need to provide file or link, but not both."


def increase_counter(link=0, file=0):
    today = str(date.today())
    updated, created = SecretCounter.objects.get_or_create(date=today)
    counter = updated or created
    counter.downloads += file
    counter.links += link
    counter.save()


def add_secret(data, current_user, file=None):
    secret_file = file or data.get("secret_file")
    if secret_file:
        fs = FileSystemStorage()
        filename = fs.save(secret_file.name, secret_file)
        secret_file = fs.url(filename)
    secret = SafeSecret(
        user=current_user,
        link=data.get("secret_link"),
        file=secret_file,
        password_hash=make_password(data.get("secret_password")),
    )
    secret.save()
    return reverse("file:getapi", kwargs={"secret_link": str(secret.secret_link)})


class FileDetailView(DetailView):
    model = SafeSecret
    slug_field = "secret_link"
    slug_url_kwarg = "secret_link"

    def post(self, request, secret_link):
        secret = SafeSecret.objects.get(secret_link=secret_link)
        time_delta = datetime.now(tz=tzutc()) - secret.upload_date
        if time_delta.days >= 1:
            messages.error(request, "Link expired")
        elif check_password(request.POST.get("password"), secret.password_hash):
            secret.downloads += 1
            secret.save()
            count = "link" if secret.link else "file"
            increase_counter(**{count: 1})
            return redirect(secret.file or secret.link)
        else:
            messages.error(request, "Wrong Password")
        return super().get(request, secret_link)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = GetSecretForm
        return context


file_detail_view = FileDetailView.as_view()


class FileListView(LoginRequiredMixin, ListView):
    model = SafeSecret
    slug_field = "file"
    slug_url_kwarg = "file"

    def get_queryset(self):
        return SafeSecret.objects.filter(user=self.request.user)


file_list_view = FileListView.as_view()


class SecretStatisticsView(LoginRequiredMixin, ListView):
    model = SecretCounter


secret_statistcs_list_view = SecretStatisticsView.as_view()


class SecretStatisticsGetSerializer(serializers.Serializer):
    date = serializers.DateField()
    downloads = serializers.IntegerField()
    links = serializers.IntegerField()


class SecretStatisticsAPIView(LoginRequiredMixin, generics.ListAPIView):
    queryset = SecretCounter.objects.all()
    serializer_class = SecretStatisticsGetSerializer


secret_statistcs_api_list_view = SecretStatisticsAPIView.as_view()


class FileUploadView(LoginRequiredMixin, FormView):
    template_name = "file/safesecret_form.html"
    model = SafeSecret
    form_class = UploadFileForm

    def get_success_url(self):
        return reverse("file:list")

    def get_fail_url(self):
        return reverse("file:upload")

    def form_invalid(self, form):
        response = super().form_invalid(form)
        messages.error(self.request, UPLOAD_SECRET_ERROR)
        return response

    def form_valid(self, form):
        add_secret(form.cleaned_data, self.request.user)
        return redirect(self.get_success_url())


file_upload_view = FileUploadView.as_view()


class SecretGetSerializer(serializers.Serializer):
    user = serializers.CharField(max_length=255)
    upload_date = serializers.DateTimeField()


class SecretPostSerializer(serializers.Serializer):
    secret_link = serializers.CharField(max_length=255)
    secret_password = serializers.CharField(max_length=255)
    secret_file = serializers.FileField()


class SecretAPICreateView(LoginRequiredMixin, generics.CreateAPIView):
    queryset = SafeSecret
    lookup_field = "secret_link"
    serializer_class = SecretPostSerializer

    def post(self, request, *args, **kwargs):
        check = [
            request.data.get("secret_link"),
            request.data.get("secret_file", request.FILES.get("file")),
        ]
        print(request.data)
        if all(check) or not any(check):
            return Response({"error": UPLOAD_SECRET_ERROR})
        link = add_secret(request.data, request.user, file=request.FILES.get("file"))
        return Response({"link": request.build_absolute_uri(link)})


file_create_api_view = SecretAPICreateView.as_view()


class SecretAPIDetailsView(generics.RetrieveAPIView):
    queryset = SafeSecret
    lookup_field = "secret_link"
    serializer_class = SecretGetSerializer

    def post(self, request, secret_link):
        secret = SafeSecret.objects.get(secret_link=secret_link)
        time_delta = datetime.now(tz=tzutc()) - secret.upload_date
        password = request.data.get("password", "")
        if time_delta.days > 1:
            return Response({"error": "Link expired"})
        if check_password(password, secret.password_hash):
            secret.downloads += 1
            secret.save()
            count = "link" if secret.link else "file"
            increase_counter(**{count: 1})
            return Response(
                {"link": request.build_absolute_uri(secret.file or secret.link)}
            )
        return Response({"error": "Wrong Password"})


file_details_api_view = SecretAPIDetailsView.as_view()
