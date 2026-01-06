# نظام التعليم التكميلي - Complementary Education System

نظام تعليمي متكامل يدعم اللغة العربية، يتضمن إدارة الدروس، الجلسات المباشرة، الجلسات المتكررة، ومساعد الواجبات الذكي.

## 📋 المتطلبات الأساسية

- Python 3.10+
- Node.js 18+
- MySQL 8.0+
- Git

## 🏗️ هيكل المشروع

```
Complementary_Education_System/
├── backend/                    # Django REST API
│   └── Education/
│       └── Educational_system/
├── frontend/                   # React + Vite
├── AI/
│   └── smart_homework_helper/  # AI Homework Helper (FastAPI)
└── README.md
```

## 🚀 طريقة التشغيل

### 1️⃣ Backend (Django)

```bash
# الانتقال لمجلد الباك إند
cd backend/Education/Educational_system

# إنشاء بيئة افتراضية
python -m venv venv

# تفعيل البيئة الافتراضية
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# تثبيت المتطلبات
pip install -r ../../../requirements.txt

# إعداد قاعدة البيانات
python manage.py migrate

# إنشاء مستخدم admin
python manage.py createsuperuser

# تشغيل السيرفر
python manage.py runserver
```

السيرفر يعمل على: `http://localhost:8000`

### 2️⃣ Frontend (React + Vite)

```bash
# الانتقال لمجلد الفرونت إند
cd frontend

# تثبيت المتطلبات
npm install

# تشغيل السيرفر التطويري
npm run dev
```

الفرونت إند يعمل على: `http://localhost:5173`

### 3️⃣ AI Homework Helper (FastAPI)

```bash
# الانتقال لمجلد المساعد الذكي
cd AI/smart_homework_helper

# تفعيل البيئة الافتراضية (نفس بيئة الباك إند أو إنشاء واحدة جديدة)
# Windows:
..\..\backend\Education\Educational_system\venv\Scripts\activate

# تشغيل السيرفر
uvicorn main:app --reload --port 8001
```

المساعد الذكي يعمل على: `http://localhost:8001`

## ⚙️ إعدادات البيئة

### Backend (.env)

أنشئ ملف `.env` في `backend/Education/Educational_system/`:

```env
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=mysql://user:password@localhost:3306/education_db
```

### Frontend (.env)

الملف موجود في `frontend/.env`:

```env
VITE_API_URL=http://localhost:8000
```

## 📚 API Endpoints الرئيسية

| الوظيفة          | Endpoint                                      |
| ---------------- | --------------------------------------------- |
| تسجيل الدخول     | `POST /api/accounts/login/`                   |
| التسجيل          | `POST /api/accounts/register/`                |
| الدروس           | `GET/POST /api/lessons/lessons/`              |
| الجلسات المباشرة | `GET/POST /api/live-sessions/`                |
| الجلسات المتكررة | `GET/POST /api/recurring-sessions/templates/` |
| مساعد الواجبات   | `POST /api/ai/homework-helper/`               |

## 👥 أنواع المستخدمين

| الدور   | الصلاحيات                   |
| ------- | --------------------------- |
| Teacher | إنشاء الدروس، إدارة الجلسات |
| Student | عرض الدروس، حضور الجلسات    |
| Advisor | إدارة الطلاب، تعيين الدروس  |
| Admin   | صلاحيات كاملة               |

## 🧪 تشغيل الاختبارات

```bash
cd backend/Education/Educational_system

# تشغيل جميع الاختبارات
python manage.py test tests

# تشغيل مع تقرير التغطية
coverage run --source='.' manage.py test tests
coverage report
coverage html
```

## 🛠️ التقنيات المستخدمة

**Backend:**

- Django 5.2
- Django REST Framework
- MySQL
- JWT Authentication

**Frontend:**

- React 18
- Vite
- Tailwind CSS
- Material UI
- i18next (دعم اللغة العربية)

**AI:**

- FastAPI
- Transformers
- Sentence Transformers
- OpenAI API

## 📝 ملاحظات

- تأكد من تشغيل MySQL قبل تشغيل الباك إند
- الفرونت إند يتصل بالباك إند على البورت 8000
- مساعد الواجبات يعمل بشكل مستقل على البورت 8001

## 📄 License

MIT License
