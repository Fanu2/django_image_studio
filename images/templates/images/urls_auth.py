from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from images import views as image_views  # ← import signup view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('images.urls')),  # include all image app routes
    path('accounts/signup/', image_views.signup_view, name='signup'),  # ← add this line
    path('accounts/', include('django.contrib.auth.urls')),  # Django built-in auth (login/logout)
]

# Serve uploaded media during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
