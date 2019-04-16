from django.urls import path

from safefileshare.file.views import (
    file_list_view,
    file_upload_view,
    file_detail_view,
    file_details_api_view,
    file_create_api_view,
)

app_name = "file"
urlpatterns = [
    path("", view=file_list_view, name="list"),
    path("~upload/", view=file_upload_view, name="upload"),
    path("~api/<slug:secret_link>/", view=file_details_api_view, name="getapi"),
    path("~api/~upload/", view=file_create_api_view, name="apiupload"),
    path("<slug:secret_link>/", view=file_detail_view, name="detail"),
]
