from datetime import datetime
from dateutil.tz import tzutc

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files.storage import FileSystemStorage
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import DetailView, ListView, FormView
from django.contrib.auth.hashers import make_password, check_password


from safefileshare.file.models import SafeSecret
from safefileshare.file.forms import UploadFileForm
from safefileshare.file.forms import GetSecretForm


class FileDetailView(DetailView):
    model = SafeSecret
    slug_field = "secret_link"
    slug_url_kwarg = "secret_link"

    def post(self, request, secret_link):
        secret = SafeSecret.objects.get(secret_link=secret_link)
        print(datetime.now(tz=tzutc()), secret.upload_date)
        time_delta = datetime.now(tz=tzutc()) - secret.upload_date
        if time_delta.days > 1:
            messages.error(request, 'Link expired')
        elif check_password(request.POST.get('password'), secret.password_hash):
            secret.downloads += 1
            secret.save()
            return redirect(secret.file or secret.link)
        else:
            messages.error(request, 'Wrong Password')
        return super().get(request, secret_link)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = GetSecretForm
        return context


file_detail_view = FileDetailView.as_view()


class FileListView(LoginRequiredMixin, ListView):
    model = SafeSecret
    slug_field = "file"
    slug_url_kwarg = "file"


file_list_view = FileListView.as_view()


class FileUploadView(LoginRequiredMixin, FormView):
    template_name = 'file/safesecret_form.html'
    model = SafeSecret
    form_class = UploadFileForm

    def get_success_url(self):
        return reverse("file:list")

    def get_fail_url(self):
        return reverse("file:upload")

    def form_invalid(self, form):
        response = super().form_invalid(form)
        messages.error(self.request, "You need to provide file or link, but not both.")
        return response

    def form_valid(self, form):
        data = form.cleaned_data
        secret_file = data.get('secret_file')
        current_user = self.request.user
        if secret_file:
            fs = FileSystemStorage()
            filename = fs.save(secret_file.name, secret_file)
            secret_file = fs.url(filename)
        SafeSecret(
            user=current_user,
            link=data.get('secret_link'),
            file=secret_file,
            password_hash=make_password(data.get('secret_password'))
        ).save()
        return redirect(self.get_success_url())


file_upload_view = FileUploadView.as_view()
