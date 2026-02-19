import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                             QListWidget, QListWidgetItem, QMessageBox, 
                             QFrame, QTextEdit)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QIcon, QPalette, QColor
from database_manager import DatabaseManager

class ReferencePageItem(QWidget):
    def __init__(self, contact_id, name, phone, description, parent_window):
        super().__init__()
        self.contact_id = contact_id
        self.name = name
        self.phone = phone
        self.description = description
        self.parent_window = parent_window
        self.setup_ui()
        
    def setup_ui(self):
        # Ana layout
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(25, 18, 25, 18)
        main_layout.setSpacing(0)
        
        # Sol taraf - Bilgiler (yatay düzen)
        info_layout = QHBoxLayout()
        info_layout.setSpacing(30)
        info_layout.setAlignment(Qt.AlignLeft)
        
        # İsim
        name_label = QLabel(self.name)
        name_label.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                font-size: 15px;
                font-weight: bold;
                font-family: Arial, sans-serif;
                min-width: 120px;
            }
        """)
        info_layout.addWidget(name_label)
        
        # Ayırıcı çizgi 1
        separator1 = QLabel("|")
        separator1.setStyleSheet("""
            QLabel {
                color: #8A9BAD;
                font-size: 16px;
                font-weight: normal;
                font-family: Arial, sans-serif;
            }
        """)
        info_layout.addWidget(separator1)
        
        # Telefon
        phone_label = QLabel(self.phone)
        phone_label.setStyleSheet("""
            QLabel {
                color: #E8E8E8;
                font-size: 14px;
                font-weight: 500;
                font-family: Arial, sans-serif;
                min-width: 130px;
            }
        """)
        info_layout.addWidget(phone_label)
        
        # Ayırıcı çizgi 2
        separator2 = QLabel("|")
        separator2.setStyleSheet("""
            QLabel {
                color: #8A9BAD;
                font-size: 16px;
                font-weight: normal;
                font-family: Arial, sans-serif;
            }
        """)
        info_layout.addWidget(separator2)
        
        # Açıklama
        desc_label = QLabel(self.description if self.description else "açıklama")
        desc_label.setStyleSheet("""
            QLabel {
                color: #D0D0D0;
                font-size: 14px;
                font-style: italic;
                font-family: Arial, sans-serif;
                min-width: 150px;
            }
        """)
        info_layout.addWidget(desc_label)
        
        # Sol tarafa bilgileri ekle
        main_layout.addLayout(info_layout)
        main_layout.addStretch()
        
        # Sağ taraf - Butonlar
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)
        
        # Düzenle butonu (turuncu)
        edit_btn = QPushButton("✏️")
        edit_btn.setFixedSize(50, 38)
        edit_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                border: none;
                border-radius: 8px;
                color: white;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
            QPushButton:pressed {
                background-color: #E65100;
            }
        """)
        edit_btn.clicked.connect(self.edit_contact)
        button_layout.addWidget(edit_btn)
        
        # Sil butonu (kırmızı)
        delete_btn = QPushButton("🗑️")
        delete_btn.setFixedSize(50, 38)
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #F44336;
                border: none;
                border-radius: 8px;
                color: white;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #D32F2F;
            }
            QPushButton:pressed {
                background-color: #B71C1C;
            }
        """)
        delete_btn.clicked.connect(self.delete_contact)
        button_layout.addWidget(delete_btn)
        
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)
        
        # Widget stili
        self.setStyleSheet("""
            QWidget {
                background-color: #5A6B7D;
                border-radius: 10px;
                margin: 2px;
                border: 1px solid #6A7B8D;
            }
            QWidget:hover {
                background-color: #6A7B8D;
                border: 1px solid #8A9BAD;
            }
        """)
        
    def edit_contact(self):
        self.parent_window.edit_contact(self.contact_id, self.name, self.phone, self.description)
        
    def delete_contact(self):
        self.parent_window.delete_contact(self.contact_id, self.name)

class ReferencePage(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db_manager = DatabaseManager()
        self.setup_ui()
        self.load_contacts()
        
    def setup_ui(self):
        self.setWindowTitle("Referans Sayfası - Kişi Yönetimi")
        self.setGeometry(100, 100, 850, 600)
        
        # Ana widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Ana layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)
        
        # Başlık
        title_label = QLabel("📞 REFERANS KİŞİLER")
        title_label.setAlignment(Qt.AlignLeft)
        title_label.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                           stop:0 #4A90E2, stop:1 #357ABD);
                border-radius: 10px;
                color: white;
                font-size: 18px;
                font-weight: bold;
                font-family: Arial, sans-serif;
                padding: 15px 20px;
                margin: 0px;
            }
        """)
        main_layout.addWidget(title_label)
        
        # Form alanları - Tek satırda
        form_layout = QHBoxLayout()
        form_layout.setSpacing(12)
        
        # İsim alanı
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("👤 İsim")
        self.name_input.setFixedHeight(40)
        self.name_input.setStyleSheet("""
            QLineEdit {
                background-color: white;
                border: 2px solid #E0E0E0;
                border-radius: 8px;
                padding: 0 12px;
                font-size: 14px;
                font-family: Arial, sans-serif;
                color: #333333;
            }
            QLineEdit:focus {
                border-color: #4A90E2;
            }
            QLineEdit::placeholder {
                color: #888888;
            }
        """)
        form_layout.addWidget(self.name_input)
        
        # Telefon alanı
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("📞 Telefon")
        self.phone_input.setFixedHeight(40)
        self.phone_input.setStyleSheet("""
            QLineEdit {
                background-color: white;
                border: 2px solid #E0E0E0;
                border-radius: 8px;
                padding: 0 12px;
                font-size: 14px;
                font-family: Arial, sans-serif;
                color: #333333;
            }
            QLineEdit:focus {
                border-color: #4A90E2;
            }
            QLineEdit::placeholder {
                color: #888888;
            }
        """)
        form_layout.addWidget(self.phone_input)
        
        # Açıklama alanı
        self.description_input = QLineEdit()
        self.description_input.setPlaceholderText("📝 Açıklama")
        self.description_input.setFixedHeight(40)
        self.description_input.setStyleSheet("""
            QLineEdit {
                background-color: white;
                border: 2px solid #E0E0E0;
                border-radius: 8px;
                padding: 0 12px;
                font-size: 14px;
                font-family: Arial, sans-serif;
                color: #333333;
            }
            QLineEdit:focus {
                border-color: #4A90E2;
            }
            QLineEdit::placeholder {
                color: #888888;
            }
        """)
        form_layout.addWidget(self.description_input)
        
        # Kaydet butonu
        self.save_btn = QPushButton("💾 KAYDET")
        self.save_btn.setFixedSize(100, 40)
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #27AE60;
                border: none;
                border-radius: 8px;
                color: white;
                font-size: 12px;
                font-weight: bold;
                font-family: Arial, sans-serif;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:pressed {
                background-color: #1E8449;
            }
        """)
        self.save_btn.clicked.connect(self.save_contact)
        form_layout.addWidget(self.save_btn)
        
        main_layout.addLayout(form_layout)
        
        # Arama ve temizle alanı
        search_layout = QHBoxLayout()
        search_layout.setSpacing(12)
        
        # Arama alanı
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Kişi ara...")
        self.search_input.setFixedHeight(40)
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: white;
                border: 2px solid #E0E0E0;
                border-radius: 8px;
                padding: 0 12px;
                font-size: 14px;
                font-family: Arial, sans-serif;
                color: #333333;
            }
            QLineEdit:focus {
                border-color: #4A90E2;
            }
            QLineEdit::placeholder {
                color: #888888;
            }
        """)
        self.search_input.textChanged.connect(self.search_contacts)
        search_layout.addWidget(self.search_input)
        
        # Temizle butonu
        clear_btn = QPushButton("🗑️ TEMİZLE")
        clear_btn.setFixedSize(100, 40)
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #E74C3C;
                border: none;
                border-radius: 8px;
                color: white;
                font-size: 12px;
                font-weight: bold;
                font-family: Arial, sans-serif;
            }
            QPushButton:hover {
                background-color: #C0392B;
            }
            QPushButton:pressed {
                background-color: #A93226;
            }
        """)
        clear_btn.clicked.connect(self.clear_form)
        search_layout.addWidget(clear_btn)
        
        main_layout.addLayout(search_layout)
        
        # Kişi listesi
        self.contact_list = QListWidget()
        self.contact_list.setStyleSheet("""
            QListWidget {
                background-color: #3A4A5C;
                border: none;
                border-radius: 8px;
                padding: 8px;
            }
            QListWidget::item {
                background-color: transparent;
                border: none;
                padding: 3px;
                margin: 1px 0;
            }
            QListWidget::item:selected {
                background-color: transparent;
            }
        """)
        main_layout.addWidget(self.contact_list)
        
        central_widget.setLayout(main_layout)
        
        # Genel stil
        self.setStyleSheet("""
            QMainWindow {
                background-color: #F0F0F0;
            }
        """)
        
        # Değişkenler
        self.editing_contact_id = None
        
    def load_contacts(self):
        """Tüm kişileri yükle"""
        self.contact_list.clear()
        try:
            contacts = self.db_manager.get_all_contacts()
            for contact in contacts:
                contact_id, name, phone, description = contact
                self.add_contact_to_list(contact_id, name, phone, description)
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Kişiler yüklenirken hata oluştu: {str(e)}")
    
    def add_contact_to_list(self, contact_id, name, phone, description):
        """Listeye kişi ekle"""
        contact_item = ReferencePageItem(contact_id, name, phone, description, self)
        list_item = QListWidgetItem()
        list_item.setSizeHint(QSize(0, 70))
        
        self.contact_list.addItem(list_item)
        self.contact_list.setItemWidget(list_item, contact_item)
    
    def save_contact(self):
        """Kişi kaydet"""
        name = self.name_input.text().strip()
        phone = self.phone_input.text().strip()
        description = self.description_input.text().strip()
        
        if not name or not phone:
            QMessageBox.warning(self, "Uyarı", "İsim ve telefon alanları zorunludur!")
            return
        
        try:
            if self.editing_contact_id:
                # Güncelleme
                success = self.db_manager.update_contact(self.editing_contact_id, name, phone, description)
                if success:
                    QMessageBox.information(self, "Başarılı", "Kişi başarıyla güncellendi!")
                    self.clear_form()
                    self.load_contacts()
                else:
                    QMessageBox.critical(self, "Hata", "Kişi güncellenirken hata oluştu!")
            else:
                # Yeni ekleme
                contact_id = self.db_manager.add_contact(name, phone, description)
                if contact_id:
                    QMessageBox.information(self, "Başarılı", "Kişi başarıyla eklendi!")
                    self.clear_form()
                    self.load_contacts()
                else:
                    QMessageBox.critical(self, "Hata", "Kişi eklenirken hata oluştu!")
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"İşlem sırasında hata oluştu: {str(e)}")
    
    def edit_contact(self, contact_id, name, phone, description):
        """Kişi düzenle"""
        self.editing_contact_id = contact_id
        self.name_input.setText(name)
        self.phone_input.setText(phone)
        self.description_input.setText(description)
        self.save_btn.setText("💾 GÜNCELLE")
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #F39C12;
                border: none;
                border-radius: 8px;
                color: white;
                font-size: 12px;
                font-weight: bold;
                font-family: Arial, sans-serif;
            }
            QPushButton:hover {
                background-color: #E67E22;
            }
            QPushButton:pressed {
                background-color: #D35400;
            }
        """)
    
    def delete_contact(self, contact_id, name):
        """Kişi sil"""
        reply = QMessageBox.question(self, "Silme Onayı", 
                                   f"'{name}' adlı kişiyi silmek istediğinizden emin misiniz?",
                                   QMessageBox.Yes | QMessageBox.No, 
                                   QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            try:
                success = self.db_manager.delete_contact(contact_id)
                if success:
                    QMessageBox.information(self, "Başarılı", "Kişi başarıyla silindi!")
                    self.load_contacts()
                else:
                    QMessageBox.critical(self, "Hata", "Kişi silinirken hata oluştu!")
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Silme işlemi sırasında hata oluştu: {str(e)}")
    
    def search_contacts(self, text):
        """Kişi ara"""
        self.contact_list.clear()
        try:
            if text.strip():
                contacts = self.db_manager.search_contacts(text)
            else:
                contacts = self.db_manager.get_all_contacts()
            
            for contact in contacts:
                contact_id, name, phone, description = contact
                self.add_contact_to_list(contact_id, name, phone, description)
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Arama sırasında hata oluştu: {str(e)}")
    
    def clear_form(self):
        """Formu temizle"""
        self.name_input.clear()
        self.phone_input.clear()
        self.description_input.clear()
        self.search_input.clear()
        self.editing_contact_id = None
        self.save_btn.setText("💾 KAYDET")
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #27AE60;
                border: none;
                border-radius: 8px;
                color: white;
                font-size: 12px;
                font-weight: bold;
                font-family: Arial, sans-serif;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:pressed {
                background-color: #1E8449;
            }
        """)
        self.load_contacts()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Uygulama stili
    app.setStyle("Fusion")
    
    window = ReferencePage()
    window.show()
    
    sys.exit(app.exec_())