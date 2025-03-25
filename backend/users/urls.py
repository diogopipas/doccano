from django.urls import include, path

from .views import Me, UserCreation, UserDeletion, Users, UserUpdate

urlpatterns = [
    path(route="me", view=Me.as_view(), name="me"),
    path(route="users", view=Users.as_view(), name="user_list"),
    path(route="users/create", view=UserCreation.as_view(), name="user_create"),
    path("users/delete/<int:id>/", UserDeletion.as_view(), name="user_delete"),
    path("users/update/<int:id>", UserUpdate.as_view(), name="user_update"),
    path("auth/", include("dj_rest_auth.urls")),
]
