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
        check_passs = check_password(request.POST.get('password'), secret.password_hash)
        if check_passs:
            secret.downloads += 1
            secret.save()
            return redirect(secret.file or secret.link)
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

    def post(self, request):
        secret_file = request.FILES.get('secret_file')
        secret_link = request.POST.get('secret_link')
        secret_pass = request.POST.get('secret_password')
        current_user = request.user
        if secret_file:
            fs = FileSystemStorage()
            filename = fs.save(secret_file.name, secret_file)
            secret_file = fs.url(filename)
        new_secret = SafeSecret(
            user=current_user,
            link=secret_link,
            file=secret_file,
            password_hash=make_password(secret_pass)
        )
        new_secret.save()
        return redirect(self.get_success_url())

    def form_valid(self, form):
        print('yey')
        valid = super().form_valid(form)
        print(valid)
        if not valid:
            messages.error("You need to provide file or link")
        return valid



file_upload_view = FileUploadView.as_view()
