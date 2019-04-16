from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from safefileshare.file.views import (
    file_list_view,
    file_upload_view,
    file_detail_view,
    file_details_api_view,
    file_create_api_view,
    secret_statistcs_list_view,
    secret_statistcs_api_list_view,
)

app_name = "file"
urlpatterns = [
    path("", view=file_list_view, name="list"),
    path("~upload/", view=file_upload_view, name="upload"),
    path("~statistics/", view=secret_statistcs_list_view, name="statistics"),
    path(
        "~api/~statistics/", view=secret_statistcs_api_list_view, name="apistatistics"
    ),
    path("~api/<slug:secret_link>/", view=file_details_api_view, name="getapi"),
    path("~api/~upload/", view=csrf_exempt(file_create_api_view), name="apiupload"),
    path("<slug:secret_link>/", view=csrf_exempt(file_detail_view), name="detail"),
]
