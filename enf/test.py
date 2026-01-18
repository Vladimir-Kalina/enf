from django.urls import path
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent
print(BASE_DIR)
print('____________________________________________________')
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
print(STATIC_ROOT)
