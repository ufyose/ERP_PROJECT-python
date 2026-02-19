import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QTableWidget, QTableWidgetItem, 
                           QPushButton, QLineEdit, QLabel, QHeaderView,
                           QMessageBox, QDialog, QFormLayout, QDialogButtonBox,
                           QSpinBox, QDoubleSpinBox, QFrame, QScrollArea)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QPalette, QColor, QIcon
import json
import os
from database_manager import DatabaseManager
import logging

class StockAddPage(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        filename='stock_manager.log'
    )
        self.logger = logging.getLogger(__name__)
        self.setWindowTitle("Yeni Ürün Ekle")
        self.setFixedSize(400, 350)
        self.setWindowTitle("Stok Yönetim Sistemi")
        self.setStyleSheet("""
            QDialog {
                background-color: #2c3e50;
                color: white;
            }
            QLabel {
                color: white;
                font-size: 12px;
                font-weight: bold;
            }
            QLineEdit, QSpinBox, QDoubleSpinBox {
                background-color: #34495e;
                border: 2px solid #3498db;
                border-radius: 5px;
                padding: 8px;
                color: white;
                font-size: 11px;
            }
            QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {
                border-color: #e74c3c;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1abc9c;
            }
        """)
        
        self.setupUI()
    
    def setupUI(self):
        layout = QFormLayout()
        
        self.urun_kodu_edit = QLineEdit()
        self.urun_adi_edit = QLineEdit()
        self.miktar_spin = QSpinBox()
        self.miktar_spin.setRange(0, 999999)
        self.birim_fiyat_spin = QDoubleSpinBox()
        self.birim_fiyat_spin.setRange(0.0, 999999.99)
        self.birim_fiyat_spin.setDecimals(2)
        self.birim_fiyat_spin.setSuffix(" TL")
        
        layout.addRow("Ürün Kodu:", self.urun_kodu_edit)
        layout.addRow("Ürün Adı:", self.urun_adi_edit)
        layout.addRow("Miktar:", self.miktar_spin)
        layout.addRow("Birim Fiyat:", self.birim_fiyat_spin)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        
        layout.addRow(buttons)
        self.setLayout(layout)
    
    def get_data(self):
        return {
            'urun_kodu': self.urun_kodu_edit.text(),
            'urun_adi': self.urun_adi_edit.text(),
            'miktar': self.miktar_spin.value(),
            'birim_fiyat': self.birim_fiyat_spin.value()
        }

class StockPage(QMainWindow):
    def __init__(self, user_role, parent=None):  # user_role parametresi eklendi
        super().__init__(parent)
        self.user_role = user_role
        self.setWindowTitle("Stok Yönetim Sistemi")
        self.setGeometry(100, 100, 1000, 700)
        self.setMinimumSize(800, 500)
        self.db = DatabaseManager()
        self.stok_verileri = self.db.get_all_stock_items()
        
        # Veri dosyası
        
        
        
        self.setupUI()
        self.load_table_data()
        
        # Otomatik kayıt için timer
        self.save_timer = QTimer()
        self.save_timer.timeout.connect(self.save_data)
        self.save_timer.start(30000)  # 30 saniyede bir kaydet
        
    def setupUI(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2c3e50;
            }
            QWidget {
                background-color: #2c3e50;
                color: white;
            }
            QTableWidget {
                background-color: #ecf0f1;
                alternate-background-color: #bdc3c7;
                color: #2c3e50;
                gridline-color: #95a5a6;
                border: 2px solid #3498db;
                border-radius: 10px;
                font-size: 12px;
                font-weight: bold;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #bdc3c7;
                color: #2c3e50;
                background-color: transparent;
                font-weight: bold;
            }
            QTableWidget::item:selected {
                background-color: #3498db;
                color: white;
                font-weight: bold;
            }
            QTableWidget::item:alternate {
                background-color: #bdc3c7;
                color: #2c3e50;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: #ecf0f1;
                padding: 12px;
                border: 1px solid #2c3e50;
                font-weight: bold;
                font-size: 13px;
                text-align: center;
            }
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 10px;
                margin: 2px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #27ae60;
            }
            QPushButton#ekle_btn {
                background-color: #27ae60;
            }
            QPushButton#ekle_btn:hover {
                background-color: #2ecc71;
            }
            QPushButton#guncelle_btn {
                background-color: #f39c12;
            }
            QPushButton#guncelle_btn:hover {
                background-color: #e67e22;
            }
            QLineEdit {
                background-color: #34495e;
                border: 2px solid #3498db;
                border-radius: 5px;
                padding: 8px;
                color: #ecf0f1;
                font-size: 13px;
                font-weight: bold;
                min-height: 20px;
            }
            QLineEdit:focus {
                border-color: #e74c3c;
                background-color: #2c3e50;
            }
            QLineEdit::placeholder {
                color: #bdc3c7;
                font-weight: normal;
            }
            QLabel {
                color: white;
                font-size: 12px;
                font-weight: bold;
                margin: 2px;
            }
            QFrame {
                border: 1px solid #3498db;
                border-radius: 5px;
                background-color: #34495e;
                margin: 2px;
            }
        """)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(5)
        
        # Başlık - daha kompakt
        title_label = QLabel("📦 STOK YÖNETİM SİSTEMİ")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #ecf0f1;
            background-color: #34495e;
            padding: 10px;
            border-radius: 8px;
            margin-bottom: 5px;
        """)
        title_label.setMaximumHeight(50)
        main_layout.addWidget(title_label)
        
        # Arama bölümü - daha kompakt ve okunabilir
        search_frame = QFrame()
        search_layout = QHBoxLayout(search_frame)
        search_layout.setContentsMargins(8, 8, 8, 8)
        
        search_label = QLabel("🔍 Arama:")
        search_label.setMinimumWidth(80)
        search_label.setStyleSheet("""
            font-size: 13px;
            font-weight: bold;
            color: #ecf0f1;
        """)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Ürün kodu veya ürün adı ile ara...")
        self.search_input.textChanged.connect(self.filter_table)
        self.search_input.setMinimumHeight(30)
        
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        
        search_frame.setMaximumHeight(50)
        main_layout.addWidget(search_frame)
        
        # Tablo - ana alan
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Ürün Kodu", "Ürün Adı", "Stok", "Gerçek Stok", "Birim Fiyat", "Toplam Değer"])

        # Tablo ayarları - responsive
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Ürün Kodu
        header.setSectionResizeMode(1, QHeaderView.Stretch)           # Ürün Adı - esnek
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Stok
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Gerçek Stok
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Birim Fiyat
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Toplam Değer
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.verticalHeader().setVisible(False)  # Satır numaralarını gizle
        
        # Tablo boyutunu optimize et
        self.table.setSizePolicy(self.table.sizePolicy().Expanding, self.table.sizePolicy().Expanding)
        
        # Tablo öğelerinin rengini zorla ayarla
        # StockPage sınıfındaki setupUI metodunda tablo stilini şu şekilde güncelleyin:
        self.table.setStyleSheet("""
        QTableWidget {
            background-color: #34495e;
            color: white;
            border: 2px solid #3498db;
            border-radius: 10px;
            gridline-color: #95a5a6;
            font-size: 12px;
            font-weight: bold;
        }
        QTableWidget::item {
            padding: 8px;
            border-bottom: 1px solid #2c3e50;
            color: white;
            background-color: transparent;
            font-weight: bold;
        }
        QTableWidget::item:selected {
            background-color: #3498db;
            color: white;
            font-weight: bold;
        }
        QTableWidget::item:alternate {
            background-color: #2c3e50;
            color: white;
        }
        QHeaderView::section {
            background-color: #1f2937;
            color: white;  /* Sütun başlık yazı rengi beyaz yapıldı */
            padding: 12px;
            border: 1px solid #2c3e50;
            font-weight: bold;
            font-size: 13px;
            text-align: center;
        }
        QTableWidget QTableCornerButton::section {
            background-color: #1f2937;
        }
    """)
        
        main_layout.addWidget(self.table, 1)  # Stretch factor 1 - ana alanı kapla
        
        # Butonlar - kompakt
        button_frame = QFrame()
        button_layout = QHBoxLayout(button_frame)
        button_layout.setContentsMargins(5, 5, 5, 5)
        
        self.ekle_btn = QPushButton("➕ Ekle")
        self.ekle_btn.setObjectName("ekle_btn")
        self.ekle_btn.clicked.connect(self.urun_ekle)
        
        self.guncelle_btn = QPushButton("🔄 Düzenle")
        self.guncelle_btn.setObjectName("guncelle_btn")
        self.guncelle_btn.clicked.connect(self.urun_guncelle)
        
        self.sil_btn = QPushButton("🗑️ Sil")
        self.sil_btn.clicked.connect(self.urun_sil)
        
        self.kaydet_btn = QPushButton("💾 Kaydet")
        self.kaydet_btn.clicked.connect(self.save_data)

        self.yenile_btn = QPushButton("🔄 Yenile")
        self.yenile_btn.setObjectName("yenile_btn")
        self.yenile_btn.clicked.connect(self.verileri_yenile)
        self.yenile_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1abc9c;
            }
        """)

        
        
        button_layout.addWidget(self.ekle_btn)
        button_layout.addWidget(self.guncelle_btn)
        button_layout.addWidget(self.sil_btn)
        button_layout.addWidget(self.kaydet_btn)
        button_layout.addWidget(self.yenile_btn)
        button_layout.addStretch()
        
        button_frame.setMaximumHeight(50)
        main_layout.addWidget(button_frame)
        
        # İstatistikler - kompakt
        stats_frame = QFrame()
        stats_layout = QHBoxLayout(stats_frame)
        stats_layout.setContentsMargins(8, 5, 8, 5)
        
        self.total_items_label = QLabel("Toplam Ürün: 0")
        self.total_value_label = QLabel("Toplam Değer: 0.00 TL")
        
        stats_layout.addWidget(self.total_items_label)
        stats_layout.addWidget(self.total_value_label)
        stats_layout.addStretch()
        
        stats_frame.setMaximumHeight(35)
        main_layout.addWidget(stats_frame)
        
        central_widget.setLayout(main_layout)
        
        # Status bar ekle
        self.statusBar().showMessage("Hazır")
        
        self.update_statistics()
    
    
    
    def save_data(self):
        self.statusBar().showMessage("Veriler Supabase'e kaydedildi ✓", 2000)
    
    def load_table_data(self):
        try:
            self.table.setRowCount(0)  # Önce tabloyu temizle
            if not self.stok_verileri:  # Eğer stok verileri boşsa
                self.stok_verileri = self.db.get_all_stock_items()  # Yeniden yükle
                
            self.table.setRowCount(len(self.stok_verileri))
            
            for row, item in enumerate(self.stok_verileri):
                if not item:  # Eğer item None veya boşsa atla
                    continue
                    
                self.table.setItem(row, 0, QTableWidgetItem(item.get('urun_kodu', '')))
                self.table.setItem(row, 1, QTableWidgetItem(item.get('urun_adi', '')))
                self.table.setItem(row, 2, QTableWidgetItem(str(item.get('miktar', 0))))
                self.table.setItem(row, 3, QTableWidgetItem(str(item.get('gercek_stok', item.get('miktar', 0)))))
                self.table.setItem(row, 4, QTableWidgetItem(f"{item.get('birim_fiyat', 0):.2f} TL"))
                
                # Toplam değer hesaplama (daha güvenli)
                try:
                    miktar = float(item.get('miktar', 0))
                    birim_fiyat = float(item.get('birim_fiyat', 0))
                    toplam_deger = miktar * birim_fiyat
                    self.table.setItem(row, 5, QTableWidgetItem(f"{toplam_deger:.2f} TL"))
                except (TypeError, ValueError) as e:
                    self.table.setItem(row, 5, QTableWidgetItem("0.00 TL"))
                    logging.error(f"Toplam değer hesaplanırken hata: {str(e)}")
            
            self.update_statistics()
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Tablo yüklenirken hata oluştu: {str(e)}")
            logging.exception("Tablo yükleme hatası")
    
    def filter_table(self):
        search_text = self.search_input.text().lower()
        
        for row in range(self.table.rowCount()):
            show_row = False
            for col in range(2):  # Sadece ürün kodu ve ürün adı sütunlarında ara
                item = self.table.item(row, col)
                if item and search_text in item.text().lower():
                    show_row = True
                    break
            self.table.setRowHidden(row, not show_row)
    
    # stock_page.py dosyasında düzeltme
    def urun_ekle(self):
        dialog = StockAddPage(self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            if data['urun_kodu'] and data['urun_adi']:
                # Ürün kodu kontrolü
                for item in self.stok_verileri:
                    if item['urun_kodu'] == data['urun_kodu']:
                        QMessageBox.warning(self, "Hata", "Bu ürün kodu zaten mevcut!")
                        return
                
                try:
                    result = self.db.add_stock_item(
                        urun_kodu=data['urun_kodu'],
                        urun_adi=data['urun_adi'],
                        miktar=data['miktar'],
                        birim_fiyat=data['birim_fiyat']
                    )
                    if result:
                        # Verileri yeniden yükle
                        self.stok_verileri = self.db.get_all_stock_items()
                        self.load_table_data()
                        self.statusBar().showMessage(f"'{data['urun_adi']}' ürünü eklendi ✓", 3000)
                    else:
                        QMessageBox.warning(self, "Hata", "Ürün eklenemedi!")
                except Exception as e:
                    QMessageBox.critical(self, "Hata", f"Ürün eklenirken hata oluştu: {str(e)}")
            else:
                QMessageBox.warning(self, "Hata", "Ürün kodu ve ürün adı boş olamaz!")
    
    def urun_guncelle(self):
        current_row = self.table.currentRow()
        if current_row >= 0:
            dialog = StockAddPage(self)
            dialog.setWindowTitle("Ürün Güncelle")
            
            # Mevcut verileri dialog'a yükle
            current_data = self.stok_verileri[current_row]
            dialog.urun_kodu_edit.setText(current_data['urun_kodu'])
            dialog.urun_adi_edit.setText(current_data['urun_adi'])
            dialog.miktar_spin.setValue(current_data['miktar'])
            dialog.birim_fiyat_spin.setValue(current_data['birim_fiyat'])
            
            if dialog.exec_() == QDialog.Accepted:
                data = dialog.get_data()
                if data['urun_kodu'] and data['urun_adi']:
                    result = self.db.update_stock_item(
                        item_id=self.stok_verileri[current_row]['id'],
                        urun_kodu=data['urun_kodu'],
                        urun_adi=data['urun_adi'],
                        miktar=data['miktar'],
                        birim_fiyat=data['birim_fiyat']
                    )
                    if result:
                        self.stok_verileri = self.db.get_all_stock_items()
                        self.load_table_data()
                        self.statusBar().showMessage(f"'{data['urun_adi']}' ürünü güncellendi ✓", 3000)
                    else:
                        QMessageBox.warning(self, "Hata", "Ürün güncellenemedi!")

                    self.statusBar().showMessage(f"'{data['urun_adi']}' ürünü güncellendi ✓", 3000)
                else:
                    QMessageBox.warning(self, "Hata", "Ürün kodu ve ürün adı boş olamaz!")
        else:
            QMessageBox.information(self, "Bilgi", "Lütfen güncellemek istediğiniz ürünü seçin.")

    def verileri_yenile(self):
        """Veritabanından verileri yeniden yükler ve tabloyu günceller"""
        try:
            self.stok_verileri = self.db.get_all_stock_items()
            self.load_table_data()
            self.statusBar().showMessage("Veriler yenilendi ✓", 2000)
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Veriler yenilenirken hata oluştu: {str(e)}")
            logging.exception("Veri yenileme hatası")        
    
    def urun_sil(self):
        current_row = self.table.currentRow()
        if current_row >= 0 and current_row < len(self.stok_verileri):
            try:
                selected_item = self.stok_verileri[current_row]
                if not selected_item:
                    QMessageBox.warning(self, "Uyarı", "Geçersiz ürün verisi!")
                    return
                    
                urun_adi = selected_item.get('urun_adi', 'Bilinmeyen Ürün')
                
                reply = QMessageBox.question(self, "Onay", 
                                        f"'{urun_adi}' ürünü silinsin mi?",
                                        QMessageBox.Yes | QMessageBox.No)
                
                if reply == QMessageBox.Yes:
                    urun_id = selected_item.get('id')
                    if not urun_id:
                        QMessageBox.warning(self, "Hata", "Ürün ID'si bulunamadı!")
                        return
                        
                    result = self.db.delete_stock_item(urun_id)
                    if result:
                        # Verileri yeniden yükle
                        self.stok_verileri = self.db.get_all_stock_items()
                        self.load_table_data()
                        self.statusBar().showMessage(f"'{urun_adi}' ürünü silindi ✓", 3000)
                    else:
                        QMessageBox.warning(self, "Hata", "Ürün silinemedi!")
                        
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Ürün silinirken hata oluştu:\n{str(e)}")
                logging.exception("Ürün silme hatası")
        else:
            QMessageBox.information(self, "Bilgi", "Lütfen silmek istediğiniz ürünü seçin.")
        
    def update_statistics(self):
        total_items = len(self.stok_verileri)
        total_value = sum(item['miktar'] * item['birim_fiyat'] for item in self.stok_verileri)
        
        self.total_items_label.setText(f"📊 Toplam Ürün: {total_items}")
        self.total_value_label.setText(f"💰 Toplam Değer: {total_value:.2f} TL")
    
    def closeEvent(self, event):
        self.save_data()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # Uygulama stili
    app.setStyle('Fusion')
    
    # Koyu tema
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(44, 62, 80))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(52, 73, 94))
    palette.setColor(QPalette.AlternateBase, QColor(66, 82, 110))
    palette.setColor(QPalette.ToolTipBase, Qt.white)
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(52, 73, 94))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Link, QColor(52, 152, 219))
    palette.setColor(QPalette.Highlight, QColor(52, 152, 219))
    palette.setColor(QPalette.HighlightedText, Qt.black)
    app.setPalette(palette)
    
    window = StockPage()
    window.show()
    
    sys.exit(app.exec_())