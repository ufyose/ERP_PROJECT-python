import sys
import json
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                            QListWidget, QListWidgetItem, QTextEdit, QMessageBox,
                            QDialog, QFormLayout, QDialogButtonBox, QFrame,
                            QScrollArea, QSizePolicy, QSpacerItem)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap, QIcon, QPalette, QColor, QPainter, QBrush
from database_manager import DatabaseManager

class PasswordCard(QFrame):
    delete_requested = pyqtSignal(object)
    edit_requested = pyqtSignal(object, dict)
    
    def __init__(self, password_id, platform, username, password, description=""):
        super().__init__()
        self.password_id = password_id
        self.platform = platform
        self.username = username
        self.password = password
        self.description = description
        self.setup_ui()
        
    def setup_ui(self):
        self.setFrameStyle(QFrame.NoFrame)
        self.setContentsMargins(0, 0, 0, 0)
        self.setStyleSheet("""
            PasswordCard {
                background-color: #2a2a2a;
                border: 1px solid #404040;
                border-radius: 12px;
                margin: 8px;
            }
            PasswordCard:hover {
                background-color: #333333;
                border: 1px solid #00ff88;
            }
        """)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(8)
        
        platform_label = QLabel(self.platform)
        platform_label.setFont(QFont("Arial", 14, QFont.Bold))
        platform_label.setStyleSheet("""
            QLabel {
                color: #00ff88;
                font-size: 16px;
                font-weight: bold;
                border: none;
                background: transparent;
                padding: 0px;
                margin: 0px;
            }
        """)
        
        info_layout = QVBoxLayout()
        info_layout.setSpacing(4)
        
        username_label = QLabel(f"Kullanıcı: {self.username}")
        username_label.setStyleSheet("""
            QLabel {
                color: #cccccc;
                font-size: 12px;
                border: none;
                background: transparent;
                padding: 0px;
                margin: 0px;
            }
        """)
        
        password_label = QLabel(f"Şifre: {'●' * min(len(self.password), 12)}")
        password_label.setStyleSheet("""
            QLabel {
                color: #cccccc;
                font-size: 12px;
                border: none;
                background: transparent;
                padding: 0px;
                margin: 0px;
            }
        """)
        
        info_layout.addWidget(username_label)
        info_layout.addWidget(password_label)
        
        if self.description:
            desc_label = QLabel(f"Açıklama: {self.description}")
            desc_label.setStyleSheet("""
                QLabel {
                    color: #999999;
                    font-size: 11px;
                    border: none;
                    background: transparent;
                    padding: 0px;
                    margin: 0px;
                }
            """)
            desc_label.setWordWrap(True)
            desc_label.setMaximumHeight(40)
            info_layout.addWidget(desc_label)
        
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)
        
        show_btn = QPushButton("Göster")
        show_btn.setFixedSize(60, 28)
        show_btn.setStyleSheet("""
            QPushButton {
                background-color: #007acc;
                color: white;
                border: none;
                padding: 0px;
                border-radius: 6px;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0099ff;
            }
            QPushButton:pressed {
                background-color: #005999;
            }
        """)
        show_btn.clicked.connect(self.show_password)
        
        copy_btn = QPushButton("Kopyala")
        copy_btn.setFixedSize(60, 28)
        copy_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 0px;
                border-radius: 6px;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #34ce57;
            }
            QPushButton:pressed {
                background-color: #1e7e34;
            }
        """)
        copy_btn.clicked.connect(self.copy_password)
        
        edit_btn = QPushButton("Düzenle")
        edit_btn.setFixedSize(60, 28)
        edit_btn.setStyleSheet("""
            QPushButton {
                background-color: #ffc107;
                color: #000000;
                border: none;
                padding: 0px;
                border-radius: 6px;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ffcd39;
            }
            QPushButton:pressed {
                background-color: #e0a800;
            }
        """)
        edit_btn.clicked.connect(self.edit_password)
        
        delete_btn = QPushButton("Sil")
        delete_btn.setFixedSize(45, 28)
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                padding: 0px;
                border-radius: 6px;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e85663;
            }
            QPushButton:pressed {
                background-color: #c82333;
            }
        """)
        delete_btn.clicked.connect(self.delete_password)
        
        button_layout.addWidget(show_btn)
        button_layout.addWidget(copy_btn)
        button_layout.addWidget(edit_btn)
        button_layout.addWidget(delete_btn)
        button_layout.addStretch()
        
        main_layout.addWidget(platform_label)
        main_layout.addLayout(info_layout)
        main_layout.addSpacing(8)
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)
        self.setMinimumHeight(140)
        self.setMaximumHeight(160)
        
    def show_password(self):
        msg = QMessageBox()
        msg.setWindowTitle("Şifre")
        msg.setText(f"Platform: {self.platform}\nKullanıcı: {self.username}\nŞifre: {self.password}")
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #2a2a2a;
                color: #ffffff;
            }
            QMessageBox QLabel {
                color: #ffffff;
                background-color: transparent;
                border: none;
                font-size: 12px;
            }
            QMessageBox QPushButton {
                background-color: #007acc;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 5px;
                min-width: 60px;
                font-weight: bold;
            }
            QMessageBox QPushButton:hover {
                background-color: #0099ff;
            }
        """)
        msg.exec_()
    
    def copy_password(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.password)
        
        msg = QMessageBox()
        msg.setWindowTitle("Başarılı")
        msg.setText("Şifre panoya kopyalandı!")
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #2a2a2a;
                color: #ffffff;
            }
            QMessageBox QLabel {
                color: #ffffff;
                background-color: transparent;
                border: none;
                font-size: 12px;
            }
            QMessageBox QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 5px;
                min-width: 60px;
                font-weight: bold;
            }
            QMessageBox QPushButton:hover {
                background-color: #34ce57;
            }
        """)
        msg.exec_()
    
    def edit_password(self):
        dialog = AddPasswordDialog(self.platform, self.username, self.password, self.description)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            self.edit_requested.emit(self, data)
    
    def delete_password(self):
        msg = QMessageBox()
        msg.setWindowTitle('Silme Onayı')
        msg.setText(f'{self.platform} için kaydedilen şifre silinecek. Emin misiniz?')
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.No)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #2a2a2a;
                color: #ffffff;
            }
            QMessageBox QLabel {
                color: #ffffff;
                background-color: transparent;
                border: none;
                font-size: 12px;
            }
            QMessageBox QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 5px;
                min-width: 60px;
                font-weight: bold;
            }
            QMessageBox QPushButton:hover {
                background-color: #e85663;
            }
        """)
        
        reply = msg.exec_()
        if reply == QMessageBox.Yes:
            self.delete_requested.emit(self)

class AddPasswordDialog(QDialog):
    def __init__(self, platform="", username="", password="", description=""):
        super().__init__()
        self.platform_edit = QLineEdit(platform)
        self.username_edit = QLineEdit(username)
        self.password_edit = QLineEdit(password)
        self.description_edit = QTextEdit(description)
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("Şifre Ekle/Düzenle")
        self.setFixedSize(400, 300)
        self.setStyleSheet("""
            QDialog {
                background-color: #1a1a1a;
                color: #ffffff;
            }
            QLabel {
                color: #ffffff;
                font-weight: bold;
            }
            QLineEdit, QTextEdit {
                background-color: #2a2a2a;
                border: 1px solid #404040;
                border-radius: 5px;
                padding: 8px;
                color: #ffffff;
                font-size: 11px;
            }
            QLineEdit:focus, QTextEdit:focus {
                border: 1px solid #007acc;
            }
            QPushButton {
                background-color: #007acc;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0099ff;
            }
        """)
        
        layout = QFormLayout()
        
        layout.addRow("Platform:", self.platform_edit)
        layout.addRow("Kullanıcı Adı:", self.username_edit)
        layout.addRow("Şifre:", self.password_edit)
        layout.addRow("Açıklama:", self.description_edit)
        
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        layout.addWidget(button_box)
        self.setLayout(layout)
        
    def get_data(self):
        return {
            'platform': self.platform_edit.text(),
            'username': self.username_edit.text(),
            'password': self.password_edit.text(),
            'description': self.description_edit.toPlainText()
        }

class PasswordManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.setup_ui()
        self.load_passwords()
        
    def setup_ui(self):
        self.setWindowTitle("Şifre Yöneticisi")
        self.setGeometry(100, 100, 1000, 700)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        
        left_panel = QFrame()
        left_panel.setFixedWidth(250)
        left_panel.setStyleSheet("""
            QFrame {
                background-color: #1a1a1a;
                border-right: 1px solid #404040;
            }
        """)
        
        left_layout = QVBoxLayout(left_panel)
        
        title_label = QLabel("Şifre Yöneticisi")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setStyleSheet("""
            QLabel {
                color: #00ff88;
                padding: 20px;
                font-size: 18px;
            }
        """)
        title_label.setAlignment(Qt.AlignCenter)
        
        self.count_label = QLabel("Toplam: 0 şifre")
        self.count_label.setStyleSheet("""
            QLabel {
                color: #cccccc;
                padding: 10px;
                font-size: 12px;
                background-color: #2a2a2a;
                border-radius: 5px;
                margin: 10px;
            }
        """)
        self.count_label.setAlignment(Qt.AlignCenter)
        
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Platform ara...")
        self.search_edit.setStyleSheet("""
            QLineEdit {
                background-color: #2a2a2a;
                border: 1px solid #404040;
                border-radius: 5px;
                padding: 10px;
                color: #ffffff;
                font-size: 12px;
                margin: 10px;
            }
            QLineEdit:focus {
                border: 1px solid #007acc;
            }
        """)
        self.search_edit.textChanged.connect(self.filter_passwords)
        
        add_btn = QPushButton("+ Yeni Şifre Ekle")
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 12px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 12px;
                margin: 10px;
            }
            QPushButton:hover {
                background-color: #34ce57;
            }
            QPushButton:pressed {
                background-color: #218838;
            }
        """)
        add_btn.clicked.connect(self.add_password)
        
        clear_btn = QPushButton("Tümünü Temizle")
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                padding: 12px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 12px;
                margin: 10px;
            }
            QPushButton:hover {
                background-color: #e85663;
            }
            QPushButton:pressed {
                background-color: #c82333;
            }
        """)
        clear_btn.clicked.connect(self.clear_all_passwords)
        
        left_layout.addWidget(title_label)
        left_layout.addWidget(self.count_label)
        left_layout.addWidget(self.search_edit)
        left_layout.addWidget(add_btn)
        left_layout.addStretch()
        left_layout.addWidget(clear_btn)
        
        right_panel = QFrame()
        right_panel.setStyleSheet("""
            QFrame {
                background-color: #1a1a1a;
            }
        """)
        
        right_layout = QVBoxLayout(right_panel)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #1a1a1a;
            }
            QScrollBar:vertical {
                background-color: #2a2a2a;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #555555;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #777777;
            }
        """)
        
        self.password_widget = QWidget()
        self.password_widget.setStyleSheet("""
            QWidget {
                background-color: #1a1a1a;
                border: none;
            }
        """)
        self.password_layout = QVBoxLayout(self.password_widget)
        self.password_layout.setAlignment(Qt.AlignTop)
        self.password_layout.setSpacing(10)
        self.password_layout.setContentsMargins(10, 10, 10, 10)
        
        scroll_area.setWidget(self.password_widget)
        right_layout.addWidget(scroll_area)
        
        main_layout.addWidget(left_panel)
        main_layout.addWidget(right_panel)
        
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1a1a1a;
            }
        """)
    
    def add_password(self):
        dialog = AddPasswordDialog()
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            if data['platform'] and data['username'] and data['password']:
                result = self.db.add_password(
                    platform=data['platform'],
                    username=data['username'],
                    password=data['password'],
                    description=data['description']
                )
                if result:
                    self.load_passwords()
                else:
                    QMessageBox.warning(self, "Hata", "Şifre eklenirken bir hata oluştu!")
            else:
                QMessageBox.warning(self, "Hata", "Lütfen tüm alanları doldurun!")
    
    def refresh_password_list(self, passwords):
        for i in reversed(range(self.password_layout.count())):
            child = self.password_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        for password_data in passwords:
            card = PasswordCard(
                password_id=password_data['id'],
                platform=password_data['platform'],
                username=password_data['username'],
                password=password_data['password'],
                description=password_data.get('description', '')
            )
            card.delete_requested.connect(self.remove_password_card)
            card.edit_requested.connect(self.edit_password_card)
            self.password_layout.addWidget(card)
        
        self.count_label.setText(f"Toplam: {len(passwords)} şifre")
    
    def filter_passwords(self, text):
        passwords = self.db.search_passwords(text) if text else self.db.get_all_passwords()
        self.refresh_password_list(passwords)
    
    def remove_password_card(self, card):
        if self.db.delete_password(card.password_id):
            self.load_passwords()
        else:
            QMessageBox.warning(self, "Hata", "Şifre silinirken bir hata oluştu!")
    
    def edit_password_card(self, card, new_data):
        if self.db.update_password(
            password_id=card.password_id,
            platform=new_data['platform'],
            username=new_data['username'],
            password=new_data['password'],
            description=new_data['description']
        ):
            self.load_passwords()
        else:
            QMessageBox.warning(self, "Hata", "Şifre güncellenirken bir hata oluştu!")
    
    def clear_all_passwords(self):
        msg = QMessageBox()
        msg.setWindowTitle('Tümünü Temizle')
        msg.setText('Tüm şifreler silinecek. Emin misiniz?')
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.No)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #2a2a2a;
                color: #ffffff;
            }
            QMessageBox QLabel {
                color: #ffffff;
                background-color: transparent;
                border: none;
                font-size: 12px;
            }
            QMessageBox QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 5px;
                min-width: 60px;
                font-weight: bold;
            }
            QMessageBox QPushButton:hover {
                background-color: #e85663;
            }
        """)
        
        reply = msg.exec_()
        if reply == QMessageBox.Yes:
            if self.db.delete_all_passwords():
                self.load_passwords()
            else:
                QMessageBox.warning(self, "Hata", "Şifreler silinirken bir hata oluştu!")
    
    def load_passwords(self):
        try:
            passwords = self.db.get_all_passwords()
            self.refresh_password_list(passwords)
        except Exception as e:
            QMessageBox.warning(self, "Hata", f"Şifreler yüklenirken hata oluştu: {str(e)}")

def main():
    app = QApplication(sys.argv)
    
    app.setStyleSheet("""
        QApplication {
            background-color: #1a1a1a;
        }
    """)
    
    window = PasswordManager()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()