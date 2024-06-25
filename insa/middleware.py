# middleware.py
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseForbidden
from django.conf import settings
import datetime
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import base64
import os
from insa.models import Setting
from django.urls import reverse

class LicenseMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        exempt_urls = [reverse('lockscreen'), reverse('login')]
        # 요청이 오면 라이센스 체크 수행
        #if not self.check_license() and request.path not in exempt_urls:
        if not self.check_license() and request.path not in exempt_urls:
            return redirect('lockscreen')
        return response

    def check_license(self):
        current_date = datetime.date.today()
        #expiry_date = datetime.datetime.strptime(settings.LICENSE_EXPIRY_DATE, '%Y-%m-%d').date()
        try:
            setting = Setting.objects.get(site_name='AD_SETTINGS')
        except Setting.DoesNotExist:
            setting = Setting.objects.create(site_name='AD_SETTINGS', admin_email='admin@example.com')
            setting = Setting.objects.get(site_name='AD_SETTINGS')
        license_key = setting.license_key
        shift=3

        # Base64 디코딩
        try:
            base64_bytes = license_key.encode('utf-8')
            encrypted_date_bytes = base64.b64decode(base64_bytes)
            encrypted_date = encrypted_date_bytes.decode('utf-8')

            parts = encrypted_date.split('-')
            decrypted_date = ''

            # 암호화된 년, 월, 일을 복호화
            for part in parts:
                decrypted_part = ''
                for char in part:
                    decrypted_part += chr((ord(char) - ord('0') - shift) % 10 + ord('0'))
                decrypted_date += decrypted_part + '-'

            # 복호화된 문자열을 날짜 객체로 변환 후 다시 문자열로 변환하여 반환
            decrypted_date = decrypted_date.rstrip('-')
            #decrypted_date_obj = datetime.datetime.strptime(decrypted_date, '%Y-%m-%d').date()
            expiry_date = datetime.datetime.strptime(decrypted_date, '%Y-%m-%d').date()
            #expiry_date=decrypted_date_obj.strftime('%Y-%m-%d').date()
            print(current_date, expiry_date)
            # 라이센스 만료일이 지났는지 확인
            if current_date > expiry_date:
                return False

            return True
        except:
            return False
