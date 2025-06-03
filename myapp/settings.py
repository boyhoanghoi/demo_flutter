"""
Django settings for myapp project.
"""

from pathlib import Path
import os
import dj_database_url # Thêm dòng này

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# SECURITY WARNING: keep the secret key used in production secret!
# Lấy SECRET_KEY từ biến môi trường, nếu không có thì dùng key mặc định (chỉ cho local dev)
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-dujc-4@r_&osf6n0-1nod9phgyj%x3l6qb^@6(_ryyc4svngj^')

# SECURITY WARNING: don't run with debug turned on in production!
# DEBUG sẽ là True nếu biến môi trường DEBUG=True, ngược lại là False
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

ALLOWED_HOSTS = []
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)
# Thêm 'localhost' và IP local của bạn nếu muốn test với DEBUG=False ở local
# ALLOWED_HOSTS.extend(['localhost', '127.0.0.1', '192.168.50.177'])
# Khi deploy, Render sẽ tự thêm domain *.onrender.com của bạn vào đây.
# Nếu bạn dùng custom domain, hãy thêm nó vào đây hoặc qua biến môi trường.

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic', # Thêm cho Whitenoise, phải đứng trên staticfiles
    'django.contrib.staticfiles',
    # Third-party apps
    'corsheaders',
    'rest_framework',
    'rest_framework.authtoken',
    # Your apps
    'app', # Tên app của bạn
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # Thêm Whitenoise middleware
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'myapp.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'myapp.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

# Cấu hình database từ biến môi trường DATABASE_URL mà Render cung cấp
# Nếu không có DATABASE_URL (ví dụ khi chạy local), dùng cấu hình SQLite mặc định hoặc PostgreSQL local của bạn
DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL', f'sqlite:///{BASE_DIR / "db.sqlite3"}'), # Fallback sang SQLite nếu không có DATABASE_URL
        conn_max_age=600, # Giữ kết nối trong 10 phút
        conn_health_checks=True, # Bật kiểm tra sức khỏe kết nối
    )
}
# Nếu bạn muốn dùng PostgreSQL local khi DATABASE_URL không được set:
# if not os.environ.get('DATABASE_URL'):
#     DATABASES['default'] = {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'quanao',
#         'USER': 'NTH',
#         'PASSWORD': 'NTHao543@',
#         'HOST': 'localhost', # hoặc IP của DB server
#         'PORT': '5432',      # hoặc port của DB server
#     }


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/
LANGUAGE_CODE = 'vi'
TIME_ZONE = 'Asia/Ho_Chi_Minh'
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/
STATIC_URL = 'static/'
# Thư mục mà `collectstatic` sẽ gom các file static vào
# Render khuyến nghị đặt trong thư mục con của `staticfiles_build`
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles_build', 'static')
# STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')] # Nếu bạn có thư mục static ở root project

# Cấu hình Whitenoise để nén file và phục vụ hiệu quả
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# Media files (User uploaded files)
MEDIA_URL = '/media/'
# Đối với Render, file upload lên sẽ bị mất sau mỗi lần deploy nếu không dùng "Disk".
# Nếu dùng Render Disk, bạn mount nó vào một path (ví dụ /var/data/media)
# và đặt MEDIA_ROOT trỏ tới đó qua biến môi trường.
MEDIA_ROOT_RENDER_DISK_PATH = os.environ.get('MEDIA_ROOT_RENDER_DISK_PATH')
if MEDIA_ROOT_RENDER_DISK_PATH:
    MEDIA_ROOT = Path(MEDIA_ROOT_RENDER_DISK_PATH)
else:
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media') # Default cho local dev

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Django REST Framework settings (giữ nguyên cấu hình của bạn)
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
}

# CORS settings
# Thay vì CORS_ALLOW_ALL_ORIGINS = True, hãy chỉ định các origin được phép
CORS_ALLOWED_ORIGINS_ENV = os.environ.get('CORS_ALLOWED_ORIGINS')
if CORS_ALLOWED_ORIGINS_ENV:
    CORS_ALLOWED_ORIGINS = CORS_ALLOWED_ORIGINS_ENV.split(',')
else:
    # Mặc định cho phép localhost khi dev, hoặc domain Render của bạn nếu có
    CORS_ALLOWED_ORIGINS = [
        "http://localhost:3000", # Ví dụ frontend React/Vue dev server
        "http://127.0.0.1:3000",
        # Thêm URL frontend của bạn khi deploy lên Render vào đây (qua biến môi trường là tốt nhất)
    ]
    if RENDER_EXTERNAL_HOSTNAME: # Cho phép API được gọi từ chính domain của nó
        CORS_ALLOWED_ORIGINS.append(f"https://{RENDER_EXTERNAL_HOSTNAME}")


CORS_ALLOW_CREDENTIALS = True # Giữ lại nếu dùng token/session

# CSRF Trusted Origins for HTTPS
CSRF_TRUSTED_ORIGINS = []
if RENDER_EXTERNAL_HOSTNAME:
    CSRF_TRUSTED_ORIGINS.append(f"https://{RENDER_EXTERNAL_HOSTNAME}")
# Thêm các origin mà bạn tin tưởng gửi POST request (thường là domain của frontend)
# CSRF_TRUSTED_ORIGINS.extend([
#     "http://localhost:3000",
#     "https://your-frontend.onrender.com" # Ví dụ
# ])


# Security settings for production (khi DEBUG=False)
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = True # Chuyển hướng HTTP sang HTTPS
    SESSION_COOKIE_SECURE = True # Chỉ gửi cookie session qua HTTPS
    CSRF_COOKIE_SECURE = True    # Chỉ gửi cookie CSRF qua HTTPS
    # SECURE_HSTS_SECONDS = 31536000 # 1 năm, cân nhắc bật sau khi chắc chắn HTTPS hoạt động tốt
    # SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    # SECURE_HSTS_PRELOAD = True
    # SECURE_CONTENT_TYPE_NOSNIFF = True
    # SECURE_BROWSER_XSS_FILTER = True # Django 5.0+ đã bỏ, X-XSS-Protection header không còn được khuyến nghị
    # X_FRAME_OPTIONS = 'DENY' # Đã có trong MIDDLEWARE