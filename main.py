import sys
import os
import logging
from PyQt5.QtWidgets import QApplication, QMessageBox, QMainWindow
from login import LoginWindow
from version_check import is_new_version_available
from update import perform_update
from ui_userInterface import Ui_MainWindow

# Log ayarları
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('finance_app.log'),
        logging.StreamHandler()
    ]
)

class FinanceApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.current_version = "1.0.0"  # Uygulamanızın mevcut versiyonu

    def check_and_apply_updates(self):
        """Güncelleme kontrolü ve uygulama"""
        try:
            logging.info("Güncelleme kontrolü başlatıldı")
            update_available, version_data = is_new_version_available()
            
            if update_available:
                response = QMessageBox.question(
                    None,
                    "Yeni Güncelleme",
                    f"Yeni sürüm bulundu: {version_data['version']}\n\nGüncelleme yapılsın mı?",
                    QMessageBox.Yes | QMessageBox.No
                )
                
                if response == QMessageBox.Yes:
                    logging.info(f"Güncelleme başlatılıyor: {version_data['version']}")
                    if perform_update():
                        return True  # Yeniden başlatılacak
            return False
            
        except Exception as e:
            logging.error(f"Güncelleme hatası: {str(e)}", exc_info=True)
            QMessageBox.critical(None, "Hata", f"Güncelleme kontrol edilemedi:\n{str(e)}")
            return False

    def run(self):
        """Uygulama ana döngüsü"""
        try:
            # Önce güncelleme kontrolü
            if not self.check_and_apply_updates():
                # Güncelleme yoksa veya kullanıcı reddettiyse
                self.login_window = LoginWindow()
                
                # Login başarılı sinyalini bağla
                self.login_window.switch_window.connect(self.show_main_window)
                self.login_window.show()
                
                sys.exit(self.app.exec_())
                
        except Exception as e:
            logging.critical(f"Uygulama başlatma hatası: {str(e)}", exc_info=True)
            QMessageBox.critical(
                None, 
                "Kritik Hata", 
                f"Uygulama başlatılamadı:\n{str(e)}\n\nLütfen teknik destekle iletişime geçin."
            )

    def show_main_window(self, user_data):
        """Login başarılı olduğunda ana pencereyi göster"""
        try:
            # Ana pencereyi oluştur
            self.main_window = QMainWindow()
            
            # UI'yı oluştur ve ana pencereye bağla
            self.ui = Ui_MainWindow()
            self.ui.setupUi(self.main_window)
            
            # Kullanıcı yetkilerini ayarla
            role = user_data.get('role', 'observer').lower()
            self.ui.setup_permissions(role)
            
            # Pencere ayarları
            self.main_window.setWindowTitle("Finansal Yönetim Sistemi")
            self.main_window.setMinimumSize(1240, 969)
            
            # Pencereyi göster ve login penceresini kapat
            self.main_window.show()
            self.login_window.close()
            
        except Exception as e:
            logging.error(f"Ana pencere oluşturulamadı: {str(e)}", exc_info=True)
            QMessageBox.critical(
                None,
                "Hata",
                f"Ana pencere açılamadı:\n{str(e)}\n\nLütfen programı yeniden başlatın."
            )

if __name__ == "__main__":
    # PyInstaller için yol ayarı
    if getattr(sys, 'frozen', False):
        os.chdir(os.path.dirname(sys.executable))
    
    # Uygulamayı başlat
    app = FinanceApp()
    app.run()