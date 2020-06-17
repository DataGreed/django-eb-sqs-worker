from django.urls import path

from . import views

urlpatterns = [
    path("sqs/", views.HandleSQSTaskView.as_view(), name="sqs_handle")
]
