from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic import DetailView, ListView, FormView

from safefileshare.file.models import SafeSecret
from safefileshare.file.forms import UploadFileForm


class FileDetailView(LoginRequiredMixin, DetailView):

    model = SafeSecret
    slug_field = "file"
    slug_url_kwarg = "file"


file_detail_view = FileDetailView.as_view()


class FileListView(LoginRequiredMixin, ListView):
    model = SafeSecret
    slug_field = "file"
    slug_url_kwarg = "file"


file_list_view = FileListView.as_view()


class FileUploadView(LoginRequiredMixin, FormView):
    template_name = 'file/safefile_form.html'
    model = SafeSecret
    form_class = UploadFileForm

    def get_success_url(self):
        return reverse("file:list")

    def post(self, request):
        print(request)
        pass


file_upload_view = FileUploadView.as_view()
