import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                             QComboBox, QMessageBox, QFrame, QStackedWidget,
                             QTableWidget, QTableWidgetItem, QHeaderView)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont, QPalette, QColor, QPixmap, QPainter, QBrush
import bcrypt
from database_manager import DatabaseManager

class AuthorizationManager:
    def __init__(self):
        self.db = DatabaseManager()
        
    def verify_user(self, username, password):
        """Kullanıcı doğrulama"""
        try:
            user = self.db.get_user_by_username(username)
            if not user:
                return None
                
            # BCRYPT ile şifre kontrolü
            if bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
                return user
            return None
        except Exception as e:
            print(f"Kullanıcı doğrulama hatası: {str(e)}")
            return None
    
    def get_user_role(self, username):
        """Kullanıcının rolünü getirir"""
        try:
            user = self.db.get_user_by_username(username)
            return user['role'] if user else None
        except Exception as e:
            print(f"Rol getirme hatası: {str(e)}")
            return None

    def check_permission(self, role, page_name):
        """Kullanıcının belirtilen sayfaya erişim izni var mı kontrol eder"""
        # Sayfa izin haritası
        permission_map = {
            'admin': ['all'],  # Tüm sayfalara erişim
            'personnel': ['stock', 'orders', 'imports', 'references'],
            'observer': ['stock', 'orders', 'imports', 'references']  # Salt okunur
        }
        
        # Admin her şeye erişebilir
        if role == 'admin':
            return True
            
        # Diğer roller için kontrol
        allowed_pages = permission_map.get(role, [])
        return page_name in allowed_pages

    def get_readonly_status(self, role):
        """Kullanıcının salt okunur modda olup olmayacağını belirler"""
        return role == 'observer'

if __name__ == "__main__":
    
    auth = AuthorizationManager()
    print("AuthorizationManager test ediliyor...")
    print("Admin için stock izni:", auth.check_permission('admin', 'stock'))
    print("Personel için income izni:", auth.check_permission('personnel', 'income'))