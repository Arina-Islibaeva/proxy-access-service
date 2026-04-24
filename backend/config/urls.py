from django.contrib import admin
from django.urls import path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from core.views import HealthCheckView
from users.views import (
    ActivateKeyView,
    ChangePasswordView,
    LoginView,
    ProfileView,
    RefreshKeyView,
    RegisterView,
)


urlpatterns = [
    path("admin/", admin.site.urls),

    path("api/health/", HealthCheckView.as_view()),
    path("api/register/", RegisterView.as_view()),
    path("api/activate-key/", ActivateKeyView.as_view()),
    path("api/login/", LoginView.as_view()),
    path("api/profile/", ProfileView.as_view()),
    path("api/refresh-key/", RefreshKeyView.as_view()),
    path("api/change-password/", ChangePasswordView.as_view()),

    path(
        "api/schema/",
        SpectacularAPIView.as_view(),
        name="schema",
    ),
    path(
        "api/docs/swagger/",
        SpectacularSwaggerView.as_view(url_name="schema"),
    ),
    path(
        "api/docs/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
    ),
]
