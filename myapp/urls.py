from django.contrib import admin
from django.urls import path, include
from django.conf import settings # Cho media files
from django.conf.urls.static import static # Cho media files

urlpatterns = [
    path('admin/', admin.site.urls),
    # Bao gồm các URL của app 'app' (nơi chứa models, views API) dưới prefix 'api/'
    path('api/', include('app.urls')),
    # Bạn có thể thêm các URL khác cho project ở đây
]

# Cấu hình để phục vụ media files (ví dụ: ảnh upload qua ImageField)
# trong quá trình development (DEBUG=True).
# Trong production, bạn nên dùng Nginx hoặc một web server khác để phục vụ media files.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) # Cho static files nếu cần
    