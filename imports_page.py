import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QTableWidget, QTableWidgetItem, 
                             QPushButton, QComboBox, QLineEdit, QLabel, 
                             QHeaderView, QMessageBox, QDialog, QFormLayout,
                             QDateEdit, QTextEdit)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont, QPalette, QColor
from database_manager import DatabaseManager

class ProductDialog(QDialog):
    def __init__(self, parent=None, product_data=None):
        super().__init__(parent)
        self.setWindowTitle("Ürün Bilgileri")
        self.setFixedSize(400, 300)
        self.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QLabel {
                color: #ffffff;
                font-size: 12px;
                font-weight: bold;
            }
            QLineEdit, QDateEdit, QTextEdit {
                background-color: #3c3c3c;
                border: 1px solid #555555;
                border-radius: 5px;
                padding: 5px;
                color: #ffffff;
                font-size: 11px;
            }
            QPushButton {
                background-color: #4a4a4a;
                border: 1px solid #666666;
                border-radius: 5px;
                padding: 8px;
                color: #ffffff;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5a5a5a;
            }
        """)
        
        self.init_ui()
        if product_data:
            self.load_data(product_data)
    
    def init_ui(self):
        layout = QVBoxLayout()
        form_layout = QFormLayout()
        
        self.urun_adi = QLineEdit()
        self.miktar = QLineEdit()
        self.tarih = QDateEdit()
        self.tarih.setDate(QDate.currentDate())
        self.notlar = QTextEdit()
        self.notlar.setMaximumHeight(60)
        
        form_layout.addRow("Ürün Adı:", self.urun_adi)
        form_layout.addRow("Miktar:", self.miktar)
        form_layout.addRow("Tarih:", self.tarih)
        form_layout.addRow("Notlar:", self.notlar)
        
        layout.addLayout(form_layout)
        
        button_layout = QHBoxLayout()
        self.kaydet_btn = QPushButton("Kaydet")
        self.iptal_btn = QPushButton("İptal")
        
        self.kaydet_btn.clicked.connect(self.accept)
        self.iptal_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(self.kaydet_btn)
        button_layout.addWidget(self.iptal_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def load_data(self, data):
        self.urun_adi.setText(data.get('urun_adi', ''))
        self.miktar.setText(data.get('miktar', ''))
        self.notlar.setText(data.get('notlar', ''))
        if 'tarih' in data:
            try:
                tarih = QDate.fromString(data['tarih'], 'dd.MM.yyyy')
                if tarih.isValid():
                    self.tarih.setDate(tarih)
            except:
                pass
    
    def get_data(self):
        return {
            'urun_adi': self.urun_adi.text(),
            'miktar': self.miktar.text(),
            'tarih': self.tarih.date().toString('dd.MM.yyyy'),
            'notlar': self.notlar.toPlainText()
        }

class ImportsPage(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.setWindowTitle("İthalat Takip Sistemi")
        self.setGeometry(100, 100, 1200, 600)
        
        # Durum renkleri
        self.durum_renkleri = {
            'Gemide': '#FF6B6B',
            'Limanda': '#4ECDC4',
            'Gümrük Sürecinde': '#45B7D1',
            'Vergi Ödendi': '#96CEB4',
            'Tamamlandı': '#6BCF7F'
        }
        
        # Gümrük alt durumları
        self.gumruk_alt_durumlar = [
            'Detaylı muayene yapıldı',
            'TSE ye gitti',
            'Vergi bekliyor'
        ]
        
        self.init_ui()
        self.load_data()
    
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
            }
            QWidget {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QTableWidget {
                background-color: #3c3c3c;
                alternate-background-color: #4a4a4a;
                gridline-color: #555555;
                selection-background-color: #5a5a5a;
                color: #ffffff;
                font-size: 12px;
            }
            QTableWidget::item {
                padding: 10px;
                border: 1px solid #555555;
                font-size: 12px;
            }
            QHeaderView::section {
                background-color: #2b2b2b;
                color: #ffffff;
                font-weight: bold;
                font-size: 13px;
                padding: 12px;
                border: 1px solid #555555;
            }
            QPushButton {
                background-color: #4a4a4a;
                border: 1px solid #666666;
                border-radius: 5px;
                padding: 8px 15px;
                color: #ffffff;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #5a5a5a;
            }
            QComboBox {
                background-color: #3c3c3c;
                border: 1px solid #555555;
                border-radius: 5px;
                padding: 5px;
                color: #ffffff;
                font-size: 12px;
                font-weight: bold;
            }
            QComboBox::drop-down {
                border: none;
                background-color: #4a4a4a;
            }
            QComboBox QAbstractItemView {
                background-color: #3c3c3c;
                color: #ffffff;
                selection-background-color: #5a5a5a;
                border: 1px solid #555555;
                font-size: 12px;
            }
            QLineEdit {
                background-color: #3c3c3c;
                border: 1px solid #555555;
                border-radius: 5px;
                padding: 5px;
                color: #ffffff;
            }
            QLabel {
                color: #ffffff;
                font-size: 12px;
                font-weight: bold;
            }
        """)
        
        # Üst panel - Butonlar ve arama
        top_panel = QWidget()
        top_layout = QHBoxLayout(top_panel)
        
        self.yeni_urun_btn = QPushButton("Yeni Ürün Ekle")
        self.yeni_urun_btn.clicked.connect(self.yeni_urun_ekle)
        
        self.duzenle_btn = QPushButton("Düzenle")
        self.duzenle_btn.clicked.connect(self.secili_urun_duzenle)
        
        self.sil_btn = QPushButton("Sil")
        self.sil_btn.clicked.connect(self.secili_urun_sil)
        self.sil_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                font-weight: bold;
                font-size: 12px;
                border: 1px solid #c82333;
                border-radius: 5px;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        
        self.arama_kutusu = QLineEdit()
        self.arama_kutusu.setPlaceholderText("Ürün ara...")
        self.arama_kutusu.textChanged.connect(self.arama_yap)
        
        top_layout.addWidget(self.yeni_urun_btn)
        top_layout.addWidget(self.duzenle_btn)
        top_layout.addWidget(self.sil_btn)
        top_layout.addStretch()
        top_layout.addWidget(QLabel("Arama:"))
        top_layout.addWidget(self.arama_kutusu)
        
        # Tablo
        self.tablo = QTableWidget()
        self.tablo.setAlternatingRowColors(True)
        self.tablo.setSelectionBehavior(QTableWidget.SelectRows)
        
        self.sutunlar = ['Ürün Adı', 'Miktar', 'Tarih', 'Durum', 'Alt Durum', 'Notlar']
        self.tablo.setColumnCount(len(self.sutunlar))
        self.tablo.setHorizontalHeaderLabels(self.sutunlar)
        
        header = self.tablo.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Fixed)
        header.setSectionResizeMode(2, QHeaderView.Fixed)
        header.setSectionResizeMode(3, QHeaderView.Fixed)
        header.setSectionResizeMode(4, QHeaderView.Fixed)
        header.setSectionResizeMode(5, QHeaderView.Stretch)
        
        self.tablo.setColumnWidth(1, 120)
        self.tablo.setColumnWidth(2, 120)
        self.tablo.setColumnWidth(3, 140)
        self.tablo.setColumnWidth(4, 160)
        
        self.tablo.verticalHeader().setDefaultSectionSize(45)
        
        layout.addWidget(top_panel)
        layout.addWidget(self.tablo)
    
    def yeni_urun_ekle(self):
        dialog = ProductDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            urun_data = dialog.get_data()
            result = self.db.add_import_product(
                urun_adi=urun_data['urun_adi'],
                miktar=urun_data['miktar'],
                tarih=urun_data['tarih'],
                durum='Gümrük Sürecinde',  # Varsayılan durumu "Gümrük Sürecinde" yapıyoruz
                alt_durum='',  # Boş başlangıç değeri
                notlar=urun_data['notlar']
            )
            if result:
                self.load_data()
            else:
                QMessageBox.warning(self, "Hata", "Ürün eklenirken bir hata oluştu!")
    
    def secili_urun_duzenle(self):
        current_row = self.tablo.currentRow()
        if current_row >= 0:
            self.urun_duzenle(current_row)
        else:
            QMessageBox.information(self, "Uyarı", "Lütfen düzenlenecek ürünü seçin.")
    
    def secili_urun_sil(self):
        current_row = self.tablo.currentRow()
        if current_row >= 0:
            self.urun_sil(current_row)
        else:
            QMessageBox.information(self, "Uyarı", "Lütfen silinecek ürünü seçin.")
    
    def urun_duzenle(self, row):
        if row < self.tablo.rowCount():
            urun_id = self.tablo.item(row, 0).data(Qt.UserRole)
            dialog = ProductDialog(self, {
                'urun_adi': self.tablo.item(row, 0).text(),
                'miktar': self.tablo.item(row, 1).text(),
                'tarih': self.tablo.item(row, 2).text(),
                'notlar': self.tablo.item(row, 5).text()
            })
            if dialog.exec_() == QDialog.Accepted:
                urun_data = dialog.get_data()
                result = self.db.update_import(
                    import_id=urun_id,
                    urun_adi=urun_data['urun_adi'],
                    miktar=urun_data['miktar'],
                    tarih=urun_data['tarih'],
                    notlar=urun_data['notlar']
                )
                if result:
                    self.load_data()
                else:
                    QMessageBox.warning(self, "Hata", "Ürün güncellenirken bir hata oluştu!")
    
    def urun_sil(self, row):
        if row < self.tablo.rowCount():
            urun_id = self.tablo.item(row, 0).data(Qt.UserRole)
            urun_adi = self.tablo.item(row, 0).text()
            
            reply = QMessageBox.question(
                self, 'Silme Onayı',
                f'"{urun_adi}" ürününü silmek istediğinizden emin misiniz?',
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                success = self.db.delete_import(urun_id)
                if success:
                    self.load_data()
                else:
                    QMessageBox.warning(self, "Hata", "Ürün silinirken bir hata oluştu!")
    
    def durum_degistir(self, row, yeni_durum):
        urun_id = self.tablo.item(row, 0).data(Qt.UserRole)
        
        # Alt durum combo box'ını güncelle
        alt_durum_combo = self.tablo.cellWidget(row, 4)
        self.update_alt_durum_combo(alt_durum_combo, yeni_durum, '')
        
        result = self.db.update_import(
            import_id=urun_id,
            durum=yeni_durum,
            alt_durum=alt_durum_combo.currentText() if yeni_durum == 'Gümrük Sürecinde' else ''
        )
        if not result:
            QMessageBox.warning(self, "Hata", "Durum güncellenirken bir hata oluştu!")
    
    def alt_durum_degistir(self, row, yeni_alt_durum):
        urun_id = self.tablo.item(row, 0).data(Qt.UserRole)
        result = self.db.update_import(
            import_id=urun_id,
            alt_durum=yeni_alt_durum
        )
        if not result:
            QMessageBox.warning(self, "Hata", "Alt durum güncellenirken bir hata oluştu!")
    
    def tabloyu_guncelle(self):
        self.tablo.setRowCount(len(self.urunler))
        
        for row, urun in enumerate(self.urunler):
            # Ürün bilgileri
            urun_adi_item = QTableWidgetItem(urun['urun_adi'])
            urun_adi_item.setFont(QFont("Arial", 12, QFont.Bold))
            urun_adi_item.setData(Qt.UserRole, urun['id'])  # ID'yi sakla
            self.tablo.setItem(row, 0, urun_adi_item)
            
            miktar_item = QTableWidgetItem(urun['miktar'])
            miktar_item.setFont(QFont("Arial", 11))
            self.tablo.setItem(row, 1, miktar_item)
            
            tarih_item = QTableWidgetItem(urun['tarih'])
            tarih_item.setFont(QFont("Arial", 11))
            self.tablo.setItem(row, 2, tarih_item)
            
            notlar_item = QTableWidgetItem(urun.get('notlar', ''))
            notlar_item.setFont(QFont("Arial", 9))
            self.tablo.setItem(row, 5, notlar_item)
            
            # Durum ComboBox
            durum_combo = QComboBox()
            durum_combo.addItems(list(self.durum_renkleri.keys()))
            durum_combo.setCurrentText(urun['durum'])
            
            # Durum değişikliğinde alt durumun güncellenmesi için bağlantı
            durum_combo.currentTextChanged.connect(lambda text, r=row: self.durum_degistir(r, text))
            
            durum_rengi = self.durum_renkleri.get(urun['durum'], '#666666')
            durum_combo.setStyleSheet(f"""
                QComboBox {{
                    background-color: {durum_rengi};
                    color: white;
                    font-weight: bold;
                    font-size: 11px;
                    padding: 5px;
                    border: 1px solid #333333;
                    border-radius: 3px;
                    min-height: 20px;
                    max-width: 130px;
                }}
                QComboBox::drop-down {{
                    background-color: {durum_rengi};
                    border: none;
                    width: 18px;
                }}
                QComboBox QAbstractItemView {{
                    background-color: #3c3c3c;
                    color: white;
                    selection-background-color: #5a5a5a;
                    font-size: 11px;
                    border: 1px solid #555555;
                }}
            """)
            
            self.tablo.setCellWidget(row, 3, durum_combo)
            
            # Alt Durum ComboBox - Güncellenmiş hali
            alt_durum_combo = QComboBox()
            self.update_alt_durum_combo(alt_durum_combo, urun['durum'], urun.get('alt_durum', ''))
            self.tablo.setCellWidget(row, 4, alt_durum_combo)

    def update_alt_durum_combo(self, combo, durum, current_alt_durum):
        combo.clear()
        if durum == 'Gümrük Sürecinde':
            combo.addItem('')
            combo.addItems(self.gumruk_alt_durumlar)
            combo.setCurrentText(current_alt_durum)
            combo.setEnabled(True)
            combo.setStyleSheet("""
                QComboBox {
                    background-color: #3c3c3c;
                    color: white;
                    font-weight: bold;
                    font-size: 10px;
                    padding: 5px;
                    border: 1px solid #555555;
                    border-radius: 3px;
                    min-height: 20px;
                    max-width: 150px;
                }
                QComboBox::drop-down {
                    background-color: #4a4a4a;
                    border: none;
                    width: 18px;
                }
                QComboBox QAbstractItemView {
                    background-color: #3c3c3c;
                    color: white;
                    selection-background-color: #5a5a5a;
                    font-size: 10px;
                    border: 1px solid #555555;
                }
            """)
        else:
            combo.addItem('')
            combo.setEnabled(False)
            combo.setStyleSheet("""
                QComboBox {
                    background-color: #555555;
                    color: #888888;
                    font-size: 10px;
                    padding: 5px;
                    border: 1px solid #666666;
                    border-radius: 3px;
                    min-height: 20px;
                    max-width: 150px;
                }
            """)
        
    def arama_yap(self, text):
        for row in range(self.tablo.rowCount()):
            urun_adi = self.tablo.item(row, 0).text().lower()
            if text.lower() in urun_adi:
                self.tablo.setRowHidden(row, False)
            else:
                self.tablo.setRowHidden(row, True)
    
    def load_data(self):
        try:
            self.urunler = self.db.get_all_imports()
            self.tabloyu_guncelle()
        except Exception as e:
            QMessageBox.warning(self, "Hata", f"Veri yüklenirken hata oluştu: {str(e)}")
            self.urunler = []

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # Koyu tema ayarları
    app.setStyle('Fusion')
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(30, 30, 30))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(60, 60, 60))
    palette.setColor(QPalette.AlternateBase, QColor(74, 74, 74))
    palette.setColor(QPalette.ToolTipBase, Qt.white)
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(74, 74, 74))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.HighlightedText, Qt.black)
    app.setPalette(palette)
    
    window = ImportsPage()
    window.show()
    
    sys.exit(app.exec_())