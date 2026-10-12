# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

QLGV ("Quản lý giáo vụ") is a Django 6 + Django REST Framework API for a university course-management database (faculties, teachers, subjects, prerequisites, classes, students, teaching assignments, exam results). Identifiers, model fields, comments, and API responses are in Vietnamese; keep new code consistent with that naming.

## Commands

Run everything from this directory (where `manage.py` lives).

```bash
pip install -r requirements.txt
cp config.example.ini config.ini       # secrets; git-ignored
python manage.py migrate
python manage.py seed_data             # idempotent; 161 rows + users admin/user1 (pw 12345678)
python manage.py runserver
python manage.py test app_quan_ly      # single test: python manage.py test app_quan_ly.tests.GiaoVuServiceTest.test_quy_luong_khoa
python manage.py makemigrations --check --dry-run
```

Database is SQLite (`db.sqlite3`, git-ignored). No linter is configured.

## Configuration

All config is resolved in `qlgv_project/settings.py`: environment variable first, then `config.ini` (sections `[DJANGO]`, `[GEMINI_API]`), then a dev default. Keys: `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, `DJANGO_ALLOWED_HOSTS`, `GEMINI_API_KEY`, `GEMINI_MODEL`. Other code reads these via `django.conf.settings`, never from files directly.

## Architecture

Each database table is its own Django app with an uppercase label matching the table: `KHOA`, `GIAOVIEN`, `MONHOC`, `DIEUKIEN`, `LOP`, `HOCVIEN`, `GIANGDAY`, `KETQUATHI`. An app owns its `models.py`, `admin.py`, and, when it exposes an API, also `serializers.py` / `services.py` / `views.py` / `urls.py` / `tests.py`. `qlgv_project/urls.py` includes each app's `urls.py`. URL paths don't follow app boundaries: e.g. `/api/hocvien/<ma_hv>/diem-tb/` lives in `KETQUATHI` and `/api/hocvien/<ma_hv>/kiem-tra-dieu-kien/<ma_mh>/` in `DIEUKIEN`, because the logic sits in the app whose table it mostly queries.

- **Models** use explicit uppercase `db_table` names and natural string primary keys (`ma_khoa`, `ma_gv`, `ma_mh`, `ma_lop`, `ma_hv`). Cross-app FKs are string references (`'GIAOVIEN.GiaoVien'`) to avoid import cycles. FK fields are named after the referenced key (FK `ma_khoa` → column `ma_khoa_id`). `Khoa.truong_khoa` ↔ `GiaoVien` and `Lop.truong_lop` ↔ `HocVien` are circular nullable FKs, so seeding inserts rows first and sets these afterwards.
- **Services** (`<APP>/services.py`, e.g. `KhoaService`, `KetQuaThiService`, `DieuKienService`) hold business logic as static methods and return `None` for "not found"; views turn that into 404.
- **Views** are thin DRF `APIView`s. Every response uses `app_quan_ly.responses.success(**payload)` / `error(message, status)` → `{"status": "success"|"error", ...}`. Simple list endpoints subclass `BaseListAPI` and set `queryset` + `serializer_class`.
- **`app_quan_ly`** is now the shared app and has no models: `responses.py`, `utils.format_vnd()` (money display `"2.250.000 VNĐ"`), `services/ai_service.py` (the `/api/tro-ly-ai/` Gemini chatbot; `google.generativeai` is imported lazily and the endpoint returns "chưa được cấu hình" without a key), `management/commands/seed_data.py`, and `testing.SeedDataMixin` (loads the seed data in `setUpTestData`; tests assert against seed values).

### Migration history (important)

The models originally lived in `app_quan_ly`. `app_quan_ly/migrations/0001_initial` still creates every table. All the per-table apps' migrations and `app_quan_ly/0002_tach_model_sang_cac_app` are **state-only** (`SeparateDatabaseAndState` with `database_operations=[]`). They move the models between apps without touching the DB. Don't delete or squash `app_quan_ly/0001`, and keep `app_quan_ly` in `INSTALLED_APPS`. New schema changes go through normal `makemigrations` in the owning app.
