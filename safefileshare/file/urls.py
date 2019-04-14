from django.urls import path

from safefileshare.file.views import (
    file_list_view,
    file_upload_view,
    file_detail_view,
)

app_name = "file"
urlpatterns = [
    path("", view=file_list_view, name="list"),
    path("~upload/", view=file_upload_view, name="upload"),
    path("<slug:secret_link>/", view=file_detail_view, name="detail"),
]
