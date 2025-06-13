from django.contrib import admin
from django.urls import include, path
from users.views import home
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path('', include('users.urls')),
    path('', home, name='home'),
    path('store/', include('store.urls')),  # store
    path('cart/', include('cart.urls')), # carrito
    path('servicios/', include('services.urls')), #servicois
    path('cuentas/', include('accounts.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

#product_list.html