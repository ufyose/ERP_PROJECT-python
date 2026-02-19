import sys
import bcrypt
import requests
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                             QComboBox, QMessageBox, QFrame, QStackedWidget,
                             QTableWidget, QTableWidgetItem, QHeaderView)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QPalette, QColor, QPixmap, QPainter, QBrush

class DatabaseWorker(QThread):
    """Veritabanı işlemleri için worker thread"""
    finished = pyqtSignal(bool, str, object)
    
    def __init__(self, operation, supabase_client, *args):
        super().__init__()
        self.operation = operation
        self.supabase_client = supabase_client
        self.args = args
    
    def run(self):
        try:
            if self.operation == "delete_user":
                success, message = self.supabase_client.delete_user_direct(self.args[0])
                self.finished.emit(success, message, None)
            elif self.operation == "get_all_users":
                users = self.supabase_client.get_all_users()
                self.finished.emit(True, "", users)
            elif self.operation == "create_user":
                username, password_hash, role = self.args
                success, message, user_id = self.supabase_client.insert_user(username, password_hash, role)
                self.finished.emit(success, message, user_id)
        except Exception as e:
            self.finished.emit(False, str(e), None)

class SupabaseClient:
    def __init__(self, url, anon_key):
        self.url = url
        self.anon_key = anon_key
        self.headers = {
            'apikey': anon_key,
            'Authorization': f'Bearer {anon_key}',
            'Content-Type': 'application/json',
            'Prefer': 'return=representation'
        }
    
    def insert_user(self, username, password_hash, role):
        """Kullanıcı ekleme fonksiyonu"""
        data = {
            'username': username,
            'password_hash': password_hash,
            'role': role.lower()
        }
        
        try:
            response = requests.post(
                f"{self.url}/rest/v1/users",
                headers=self.headers,
                json=data,
                timeout=10  # 10 saniye timeout
            )
            
            if response.status_code in (201, 200):
                try:
                    result = response.json()
                    # Response bir liste ise ilk elemanı al
                    if isinstance(result, list) and len(result) > 0:
                        return True, "Kullanıcı başarıyla oluşturuldu", result[0]['id']
                    # Response bir dict ise direkt kullan
                    elif isinstance(result, dict) and 'id' in result:
                        return True, "Kullanıcı başarıyla oluşturuldu", result['id']
                    else:
                        return True, "Kullanıcı başarıyla oluşturuldu", "ID alınamadı"
                except:
                    return True, "Kullanıcı başarıyla oluşturuldu", "ID alınamadı"
            else:
                try:
                    error_msg = response.json().get('message', response.text) if response.text else "Bilinmeyen hata"
                except:
                    error_msg = response.text if response.text else "Bilinmeyen hata"
                return False, f"Hata {response.status_code}: {error_msg}", None
        except requests.exceptions.RequestException as e:
            return False, f"Bağlantı hatası: {str(e)}", None
        except Exception as e:
            return False, f"Beklenmeyen hata: {str(e)}", None
    
    def get_user(self, username):
        """Kullanıcı getir"""
        try:
            response = requests.get(
                f"{self.url}/rest/v1/users?username=eq.{username}",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                users = response.json()
                return users[0] if users else None
            return None
        except requests.exceptions.RequestException:
            return None
    
    def get_all_users(self):
        """Tüm kullanıcıları getir"""
        try:
            response = requests.get(
                f"{self.url}/rest/v1/users?select=id,username,role",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            return []
        except requests.exceptions.RequestException:
            return []
    
    def delete_user_direct(self, user_id):
        """Kullanıcı silme işlemi (direkt API çağrısı)"""
        try:
            response = requests.delete(
                f"{self.url}/rest/v1/users?id=eq.{user_id}",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code in [200, 204]:
                return True, "Kullanıcı başarıyla silindi"
            else:
                # Response boş olabilir, bu durumda text kullan
                try:
                    error_msg = response.json().get('message', response.text) if response.text else "Bilinmeyen hata"
                except:
                    error_msg = response.text if response.text else "Bilinmeyen hata"
                return False, f"Hata {response.status_code}: {error_msg}"
        except requests.exceptions.RequestException as e:
            return False, f"Bağlantı hatası: {str(e)}"
        except Exception as e:
            return False, f"Beklenmeyen hata: {str(e)}"

class AirbotUserCreation(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Airbot® - Kullanıcı Yönetim Paneli")
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.setFixedSize(900, 700)
        
        # Worker thread referansı
        self.worker = None
        
        try:
            self.init_database()
            self.init_ui()
        except Exception as e:
            QMessageBox.critical(self, "Bağlantı Hatası", 
                               f"Veritabanına bağlanılamadı:\n{str(e)}\n\n"
                               "Lütfen internet bağlantınızı kontrol edin.")
            sys.exit(1)
    
    def init_database(self):
        """Supabase bağlantısını başlat"""
        self.supabase_url = "https://epydvdcmmupwhpoqmvvj.supabase.co"
        self.supabase_anon_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVweWR2ZGNtbXVwd2hwb3FtdnZqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTE2NDc5MDMsImV4cCI6MjA2NzIyMzkwM30.hnRG7JpgPsSGDBHlRk4DbhmP335gpN2Z-1WuxRDzt5Y"
        self.supabase = SupabaseClient(self.supabase_url, self.supabase_anon_key)
    
    def init_ui(self):
        """Ana arayüzü oluştur"""
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        self.stacked_widget = QStackedWidget()
        
        # Ekranları oluştur
        self.user_creation_screen = self.create_user_creation_screen()
        self.main_screen = self.create_main_screen()
        self.user_list_screen = self.create_user_list_screen()
        
        # Ekranları stack'e ekle
        self.stacked_widget.addWidget(self.user_creation_screen)
        self.stacked_widget.addWidget(self.main_screen)
        self.stacked_widget.addWidget(self.user_list_screen)
        
        # Ana layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.stacked_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_widget.setLayout(main_layout)
        
        # Başlangıçta ana ekranı göster
        self.stacked_widget.setCurrentWidget(self.main_screen)
    
    def create_user_creation_screen(self):
        """Kullanıcı oluşturma ekranını oluştur"""
        screen = QWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        
        container = QFrame()
        container.setObjectName("mainContainer")
        container.setFixedSize(500, 500)
        
        container_layout = QVBoxLayout()
        container_layout.setSpacing(20)
        container_layout.setContentsMargins(40, 40, 40, 40)
        
        # Başlık
        title_label = QLabel("Yeni Kullanıcı Oluştur")
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignCenter)
        container_layout.addWidget(title_label)
        
        # Form alanları
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Kullanıcı Adı (en az 3 karakter)")
        self.username_input.setObjectName("inputField")
        container_layout.addWidget(self.username_input)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Şifre (en az 6 karakter)")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setObjectName("inputField")
        container_layout.addWidget(self.password_input)
        
        self.password_confirm_input = QLineEdit()
        self.password_confirm_input.setPlaceholderText("Şifre Tekrar")
        self.password_confirm_input.setEchoMode(QLineEdit.Password)
        self.password_confirm_input.setObjectName("inputField")
        container_layout.addWidget(self.password_confirm_input)
        
        self.authority_combo = QComboBox()
        self.authority_combo.addItems(["Yönetici", "Personel", "Gözlemci"])
        self.authority_combo.setObjectName("comboBox")
        container_layout.addWidget(self.authority_combo)
        
        # Butonlar
        button_layout = QHBoxLayout()
        
        self.create_button = QPushButton("Kullanıcı Oluştur")
        self.create_button.setObjectName("createButton")
        self.create_button.clicked.connect(self.create_user)
        button_layout.addWidget(self.create_button)
        
        cancel_button = QPushButton("İptal")
        cancel_button.setObjectName("cancelButton")
        cancel_button.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.main_screen))
        button_layout.addWidget(cancel_button)
        
        container_layout.addLayout(button_layout)
        container.setLayout(container_layout)
        layout.addWidget(container)
        screen.setLayout(layout)
        
        return screen
    
    def create_main_screen(self):
        """Ana sayfa ekranını oluştur"""
        screen = QWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        
        container = QFrame()
        container.setObjectName("mainContainer")
        container.setFixedSize(600, 400)
        
        container_layout = QVBoxLayout()
        container_layout.setSpacing(20)
        container_layout.setContentsMargins(40, 40, 40, 40)
        
        title_label = QLabel("Airbot® Kullanıcı Yönetimi")
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignCenter)
        container_layout.addWidget(title_label)
        
        # Butonlar
        new_user_btn = QPushButton("Yeni Kullanıcı Oluştur")
        new_user_btn.setObjectName("menuButton")
        new_user_btn.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.user_creation_screen))
        container_layout.addWidget(new_user_btn)
        
        self.list_users_btn = QPushButton("Kullanıcı Listesi")
        self.list_users_btn.setObjectName("menuButton")
        self.list_users_btn.clicked.connect(self.show_user_list)
        container_layout.addWidget(self.list_users_btn)
        
        exit_btn = QPushButton("Çıkış")
        exit_btn.setObjectName("exitButton")
        exit_btn.clicked.connect(self.close)
        container_layout.addWidget(exit_btn)
        
        container.setLayout(container_layout)
        layout.addWidget(container)
        screen.setLayout(layout)
        
        return screen
    
    def create_user_list_screen(self):
        """Kullanıcı listesi ekranını oluştur"""
        screen = QWidget()
        layout = QVBoxLayout()
        
        container = QFrame()
        container.setObjectName("mainContainer")
        
        container_layout = QVBoxLayout()
        container_layout.setContentsMargins(20, 20, 20, 20)
        
        title_label = QLabel("Kayıtlı Kullanıcılar")
        title_label.setObjectName("titleLabel")
        container_layout.addWidget(title_label)
        
        self.user_table = QTableWidget()
        self.user_table.setColumnCount(4)
        self.user_table.setHorizontalHeaderLabels(["ID", "Kullanıcı Adı", "Rol", "İşlemler"])
        self.user_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.user_table.verticalHeader().setVisible(False)
        self.user_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.user_table.setObjectName("userTable")
        container_layout.addWidget(self.user_table)
        
        # Yenile butonu ekle
        button_layout = QHBoxLayout()
        
        refresh_button = QPushButton("Yenile")
        refresh_button.setObjectName("menuButton")
        refresh_button.clicked.connect(self.load_users)
        button_layout.addWidget(refresh_button)
        
        back_button = QPushButton("Ana Menüye Dön")
        back_button.setObjectName("backButton")
        back_button.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.main_screen))
        button_layout.addWidget(back_button)
        
        container_layout.addLayout(button_layout)
        container.setLayout(container_layout)
        layout.addWidget(container)
        screen.setLayout(layout)
        
        return screen
    
    def show_user_list(self):
        """Kullanıcı listesi ekranını göster"""
        self.list_users_btn.setEnabled(False)
        self.list_users_btn.setText("Yükleniyor...")
        self.load_users()
    
    def load_users(self):
        """Kullanıcı listesini yükle - Thread ile"""
        if self.worker and self.worker.isRunning():
            return
        
        self.worker = DatabaseWorker("get_all_users", self.supabase)
        self.worker.finished.connect(self.on_users_loaded)
        self.worker.start()
    
    def on_users_loaded(self, success, message, users):
        """Kullanıcılar yüklendiğinde çağrılır"""
        self.list_users_btn.setEnabled(True)
        self.list_users_btn.setText("Kullanıcı Listesi")
        
        if success and users is not None:
            self.user_table.setRowCount(len(users))
            
            for row, user in enumerate(users):
                self.user_table.setItem(row, 0, QTableWidgetItem(str(user['id'])))
                self.user_table.setItem(row, 1, QTableWidgetItem(user['username']))
                self.user_table.setItem(row, 2, QTableWidgetItem(user['role']))
                
                # Silme butonu
                if user['id'] != 1:  # Admin kullanıcısını hariç tut
                    delete_btn = QPushButton("Sil")
                    delete_btn.setObjectName("deleteButton")
                    delete_btn.clicked.connect(lambda _, uid=user['id']: self.delete_user(uid))
                    self.user_table.setCellWidget(row, 3, delete_btn)
                else:
                    self.user_table.setItem(row, 3, QTableWidgetItem("Silinemez"))
            
            # Ekranı göster
            self.stacked_widget.setCurrentWidget(self.user_list_screen)
        else:
            QMessageBox.warning(self, "Hata", f"Kullanıcılar yüklenirken hata: {message}")
    
    def delete_user(self, user_id):
        """Kullanıcı silme işlemi"""
        confirm = QMessageBox.question(
            self, "Onay", 
            "Bu kullanıcıyı silmek istediğinize emin misiniz?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            # Silme işlemini thread'de yap
            if self.worker and self.worker.isRunning():
                QMessageBox.information(self, "Bilgi", "Lütfen mevcut işlem tamamlanana kadar bekleyiniz.")
                return
            
            self.worker = DatabaseWorker("delete_user", self.supabase, user_id)
            self.worker.finished.connect(self.on_user_deleted)
            self.worker.start()
    
    def on_user_deleted(self, success, message, _):
        """Kullanıcı silme işlemi tamamlandığında çağrılır"""
        if success:
            QMessageBox.information(self, "Başarılı", message)
            # Silme işlemi başarılı olduğunda listeyi otomatik yenile
            self.load_users()
        else:
            QMessageBox.warning(self, "Hata", message)
            # Hata olsa bile listeyi yenile (silme işlemi başarılı olmuş olabilir)
            self.load_users()
    
    def create_user(self):
        """Yeni kullanıcı oluştur"""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        password_confirm = self.password_confirm_input.text().strip()
        authority = self.authority_combo.currentText()
        
        # Doğrulamalar
        if not username or len(username) < 3:
            QMessageBox.warning(self, "Uyarı", "Kullanıcı adı en az 3 karakter olmalıdır!")
            return
        
        if len(password) < 6:
            QMessageBox.warning(self, "Uyarı", "Şifre en az 6 karakter olmalıdır!")
            return
            
        if password != password_confirm:
            QMessageBox.warning(self, "Uyarı", "Şifreler uyuşmuyor!")
            return
        
        # Kullanıcı adı kontrolü
        existing_user = self.supabase.get_user(username)
        if existing_user:
            QMessageBox.warning(self, "Hata", "Bu kullanıcı adı zaten kullanılıyor!")
            return
        
        # Buton durumunu değiştir
        self.create_button.setEnabled(False)
        self.create_button.setText("Oluşturuluyor...")
        
        try:
            # Rol eşleme
            role_mapping = {
                "Yönetici": "admin",
                "Personel": "personnel",
                "Gözlemci": "observer"
            }
            role = role_mapping.get(authority, "observer")
            
            # Şifreyi hashle
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            # Thread ile kullanıcı oluştur
            if self.worker and self.worker.isRunning():
                QMessageBox.information(self, "Bilgi", "Lütfen mevcut işlem tamamlanana kadar bekleyiniz.")
                return
            
            self.worker = DatabaseWorker("create_user", self.supabase, username, hashed_password, role)
            self.worker.finished.connect(self.on_user_created)
            self.worker.start()
                
        except Exception as e:
            self.create_button.setEnabled(True)
            self.create_button.setText("Kullanıcı Oluştur")
            QMessageBox.critical(self, "Hata", f"Kullanıcı oluşturulurken hata: {str(e)}")
    
    def on_user_created(self, success, message, user_id):
        """Kullanıcı oluşturma işlemi tamamlandığında çağrılır"""
        self.create_button.setEnabled(True)
        self.create_button.setText("Kullanıcı Oluştur")
        
        if success:
            QMessageBox.information(self, "Başarılı", 
                f"Kullanıcı '{self.username_input.text()}' başarıyla oluşturuldu!\n"
                f"Yetki: {self.authority_combo.currentText()}\nID: {user_id}")
            
            # Formu temizle
            self.username_input.clear()
            self.password_input.clear()
            self.password_confirm_input.clear()
            self.authority_combo.setCurrentIndex(0)
            
            # Ana ekrana dön
            self.stacked_widget.setCurrentWidget(self.main_screen)
        else:
            QMessageBox.warning(self, "Hata", message)
    
    def closeEvent(self, event):
        """Uygulama kapatılırken worker thread'i temizle"""
        if self.worker and self.worker.isRunning():
            self.worker.terminate()
            self.worker.wait()
        event.accept()
    
    def get_stylesheet(self):
        """Stil dosyasını döndür"""
        return """
        QMainWindow {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                      stop:0 #1e3c72, stop:1 #2a5298);
        }
        
        QFrame#mainContainer {
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 15px;
            padding: 20px;
        }
        
        QLabel#titleLabel {
            font-size: 24px;
            font-weight: bold;
            color: white;
            margin-bottom: 20px;
        }
        
        QLineEdit#inputField, QComboBox#comboBox {
            padding: 10px;
            font-size: 14px;
            border: 1px solid rgba(255, 255, 255, 0.3);
            border-radius: 5px;
            background: rgba(255, 255, 255, 0.1);
            color: white;
            min-height: 40px;
        }
        
        QPushButton#createButton, QPushButton#menuButton {
            background-color: #4CAF50;
            color: white;
            border: none;
            padding: 10px;
            font-size: 14px;
            border-radius: 5px;
            min-height: 40px;
        }
        
        QPushButton#createButton:hover, QPushButton#menuButton:hover {
            background-color: #45a049;
        }
        
        QPushButton#createButton:disabled, QPushButton#menuButton:disabled {
            background-color: #666666;
            color: #cccccc;
        }
        
        QPushButton#cancelButton, QPushButton#backButton {
            background-color: #f44336;
            color: white;
            border: none;
            padding: 10px;
            font-size: 14px;
            border-radius: 5px;
            min-height: 40px;
        }
        
        QPushButton#cancelButton:hover, QPushButton#backButton:hover {
            background-color: #d32f2f;
        }
        
        QPushButton#exitButton {
            background-color: #607d8b;
            color: white;
            border: none;
            padding: 10px;
            font-size: 14px;
            border-radius: 5px;
            min-height: 40px;
        }
        
        QPushButton#exitButton:hover {
            background-color: #455a64;
        }
        
        QPushButton#deleteButton {
            background-color: #ff5252;
            color: white;
            border: none;
            padding: 5px 10px;
            font-size: 12px;
            border-radius: 3px;
        }
        
        QPushButton#deleteButton:hover {
            background-color: #ff1744;
        }
        
        QTableWidget#userTable {
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            color: white;
            gridline-color: rgba(255, 255, 255, 0.1);
        }
        
        QHeaderView::section {
            background-color: #2a5298;
            color: white;
            padding: 5px;
            border: none;
        }
        
        QTableWidget::item {
            padding: 5px;
        }
        """

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(AirbotUserCreation().get_stylesheet())
    window = AirbotUserCreation()
    window.show()
    sys.exit(app.exec_())