#for gmail
import os
EMAIL_BACKEND = os.environ.get("EMAIL_BACKEND", "django.core.mail.backends.smtp.EmailBackend")
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'yourschoolwebsitedonotreply@gmail.com'
EMAIL_HOST_PASSWORD = 'Principal1234!'
EMAIL_PORT = 587
