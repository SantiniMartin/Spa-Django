from django.contrib import admin
from django.urls import include, path
from users.views import home
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path('', include('users.urls')),
    path('', include('appointment.urls')),
    path('', home, name='home'),
    path('store/', include('store.urls')),  # store
    path('cart/', include('cart.urls')), # carrito
    path('service/', include('service.urls')), # service

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

#product_list.html