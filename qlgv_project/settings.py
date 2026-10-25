import configparser
import os
from pathlib import Path

# Thư mục gốc của project
BASE_DIR = Path(__file__).resolve().parent.parent

# Cấu hình bí mật đọc từ biến môi trường, nếu không có thì đọc từ config.ini (không commit file này).
# Xem config.example.ini để biết các khóa cần khai báo.
_config = configparser.ConfigParser()
_config.read(BASE_DIR / 'config.ini', encoding='utf-8')


def _get(env_name, section, key, default=''):
    value = os.environ.get(env_name, '').strip()
    if value:
        return value
    return _config.get(section, key, fallback='').strip() or default


# Khóa bảo mật (giá trị mặc định chỉ dùng cho môi trường phát triển)
SECRET_KEY = _get('DJANGO_SECRET_KEY', 'DJANGO', 'secret_key',
                  'django-insecure-qlgv-du-an-mon-hoc-ie221-nhom-api-key')

DEBUG = _get('DJANGO_DEBUG', 'DJANGO', 'debug', 'true').lower() in ('1', 'true', 'yes')

ALLOWED_HOSTS = [h.strip() for h in _get('DJANGO_ALLOWED_HOSTS', 'DJANGO', 'allowed_hosts', '*').split(',')]

# Trợ lý AI (Google Gemini)
GEMINI_API_KEY = _get('GEMINI_API_KEY', 'GEMINI_API', 'api_key')
# Also accept the setting name used in deployment instructions.
if not GEMINI_API_KEY:
    GEMINI_API_KEY = _get('GEMINI_API_KEY', 'GEMINI_API', 'gemini_api_key')
GEMINI_MODEL = _get('GEMINI_MODEL', 'GEMINI_API', 'model', 'gemini-3.8-flash')
GEMINI_FALLBACK_MODEL = _get(
    'GEMINI_FALLBACK_MODEL', 'GEMINI_API', 'fallback_model', 'gemini-3.5-flash-lite'
)

# Các ứng dụng được cài đặt
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'AI',

    # Phần dùng chung: tiện ích, Trợ lý AI, lệnh seed_data
    'app_quan_ly',

    # Mỗi bảng CSDL là một app riêng
    'KHOA',
    'GIAOVIEN',
    'MONHOC',
    'DIEUKIEN',
    'LOP',
    'HOCVIEN',
    'GIANGDAY',
    'KETQUATHI',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'qlgv_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'qlgv_project.wsgi.application'

# Cấu hình Cơ sở dữ liệu SQLite chuẩn
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.environ.get('QLGV_DB_PATH', str(BASE_DIR / 'db_chuan.sqlite3')),
    }
}

# Kiểm tra độ mạnh của mật khẩu
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ngôn ngữ & GIỜ VN
LANGUAGE_CODE = 'vi'
TIME_ZONE = 'Asia/Ho_Chi_Minh'
USE_I18N = True
USE_TZ = False  # SMALLDATETIME trong SQL không có múi giờ.


STATIC_URL = 'static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ]
}
# 8 bảng BRD được tạo bằng SQL chuẩn, không chạy lại DDL lịch sử cũ.
MIGRATION_MODULES = {name: name + '.canonical_migrations' for name in
                     ['KHOA', 'GIAOVIEN', 'MONHOC', 'DIEUKIEN', 'LOP', 'HOCVIEN', 'GIANGDAY', 'KETQUATHI', 'app_quan_ly']}
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY', '')
AI_MODEL = os.environ.get('AI_MODEL', '')
if os.environ.get('QLGV_DB_ENGINE') == 'mssql':
    DATABASES['default'] = {
        'ENGINE': 'mssql', 'NAME': os.environ.get('DB_NAME', 'QLGV'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '1433'),
        'USER': os.environ.get('DB_USER', ''), 'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'OPTIONS': {'driver': os.environ.get('DB_DRIVER', 'ODBC Driver 18 for SQL Server'),
                    'extra_params': os.environ.get('DB_EXTRA_PARAMS', 'TrustServerCertificate=yes')},
    }

MIGRATION_MODULES['AI'] = 'AI.canonical_migrations'
TEST_RUNNER = 'app_quan_ly.test_runner.QLGVTestRunner'

# Sau đăng nhập, entry chọn trang Admin hoặc cổng API học viên.
LOGIN_URL = "/api-auth/login/"
LOGIN_REDIRECT_URL = "/"
