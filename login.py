import sys
from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSignal
from ui_login import Ui_loginForm
from ui_userInterface import Ui_MainWindow
from supabase_client import supabase
from database_manager import DatabaseManager
from authorization_page import AuthorizationManager
import bcrypt


class LoginWindow(QtWidgets.QWidget):
    """
    Giriş penceresi sınıfı.
    Başarılı giriş durumunda ana arayüze geçiş sinyali gönderir.
    """
    switch_window = pyqtSignal(dict)
    
    
    def __init__(self):
        super().__init__()
        self.ui = Ui_loginForm()
        self.ui.setupUi(self)
        self.db = DatabaseManager()
        self.auth = AuthorizationManager()

        # Buton bağlantıları
        self.ui.loginL.clicked.connect(self.login)
        
        # Şifre alanını gizle
        self.ui.passwordL.setEchoMode(QtWidgets.QLineEdit.Password)
        
        # Enter tuşu ile giriş yapabilme
        self.ui.passwordL.returnPressed.connect(self.login)
        
    def login(self):
        username = self.ui.usernameL.text().strip()
        password = self.ui.passwordL.text().strip()

        try:
            user = self.auth.verify_user(username, password)
            if user:
                self.switch_window.emit(user)
            else:
                raise Exception("Kullanıcı adı veya şifre hatalı")
                
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Hata", f"Giriş başarısız: {str(e)}")
class MainWindow(QtWidgets.QMainWindow):
    """
    Ana uygulama penceresi sınıfı.
    UI arayüzünü yükler ve yönetir.
    """
    def __init__(self, user_data=None):
        super().__init__()
        self.user_data = user_data
        self.current_user_role = user_data.get('role', 'observer').lower()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setup_permissions()
        
        role = user_data.get('role', 'observer').lower()
        self.ui.setup_permissions(role)  # ← Bu kritik satır!
        
        # Pencere başlığı ve boyutları
        self.setWindowTitle("Finansal Yönetim Sistemi")
        self.setMinimumSize(1240, 969)

    def setup_permissions(self):
            """Kullanıcı rolüne göre yetkileri ayarlar"""
            role = self.user_data.get('role', 'observer').lower()
            
            if role == 'admin':
                # Yönetici - tüm erişim
                pass
            elif role == 'personnel':
                # Personel - sadece belirli sayfalar
                self.disable_restricted_features()
            elif role == 'observer':
                # Gözlemci - sadece görüntüleme
                self.disable_restricted_features()
                self.set_readonly_mode()
                
    def disable_restricted_features(self):
            """Personel için kısıtlı özellikleri devre dışı bırak"""
            # Örnek: Gelir/Gider sayfalarını kapat
            # Bu butonların indexlerini stackedWidget'e göre ayarlayın
            restricted_pages = [8, 9]  # Gelir ve gider sayfaları
            
    def set_readonly_mode(self):
            """Gözlemci modu - sadece okuma"""
            # Tüm düzenleme butonlarını devre dışı bırak
            pass

def run_application():
    """Uygulamayı başlatmak için ana fonksiyon"""
    app = QtWidgets.QApplication(sys.argv)
    
    login_window = LoginWindow()
    main_window = None
    
    def show_main_window(user_data):
        nonlocal main_window
        main_window = MainWindow(user_data)
        login_window.close()
        main_window.show()
    
    login_window.switch_window.connect(show_main_window)
    login_window.show()
    
    sys.exit(app.exec_())


# Eğer login.py doğrudan çalıştırılırsa (test amaçlı)
if __name__ == "__main__":
    run_application()