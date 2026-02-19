import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QPushButton, QFrame, QScrollArea, QGridLayout,
                             QDialog, QLineEdit, QSpinBox, QDoubleSpinBox, QDialogButtonBox,
                             QFormLayout, QMessageBox, QComboBox)
from PyQt5.QtCore import Qt, QTimer, QDateTime
from PyQt5.QtGui import QFont, QPalette, QColor, QIcon
from datetime import datetime
import random
from database_manager import DatabaseManager
import logging

class OrderDialog(QDialog):
    def __init__(self, parent=None, order_data=None):
        super().__init__(parent)
        self.db = DatabaseManager()
        self.order_data = order_data
        self.initUI()
        if order_data:
            self.fill_form(order_data)
        
    def initUI(self):
        self.setWindowTitle("Sipariş Ekle/Düzenle")
        self.setFixedSize(400, 300)
        
        layout = QFormLayout()
        
        # Form alanları
        self.order_no_edit = QLineEdit()
        self.customer_edit = QLineEdit()
        self.product_combo = QComboBox()
        self.product_combo.addItems([
            "Laptop", "Mouse", "Klavye", "Monitor", "Kulaklık", 
            "Webcam", "Tablet", "Şarj Aleti", "USB Bellek", "Hoparlör"
        ])
        self.product_combo.setEditable(True)
        self.quantity_spin = QSpinBox()
        self.quantity_spin.setRange(1, 1000)
        self.quantity_spin.setValue(1)
        self.price_spin = QDoubleSpinBox()
        self.price_spin.setRange(0.01, 999999.99)
        self.price_spin.setDecimals(2)
        self.price_spin.setValue(100.00)
        
        # Miktar veya fiyat değiştiğinde toplam güncelleme
        self.quantity_spin.valueChanged.connect(self.update_total)
        self.price_spin.valueChanged.connect(self.update_total)
        
        self.total_label = QLabel("100.00 TL")
        self.total_label.setStyleSheet("font-weight: bold; color: white;")
        
        # Form layout
        layout.addRow("Ürün kodu:", self.order_no_edit)
        layout.addRow("Müşteri:", self.customer_edit)
        layout.addRow("Ürün:", self.product_combo)
        layout.addRow("Adet:", self.quantity_spin)
        layout.addRow("Birim Fiyat:", self.price_spin)
        layout.addRow("Toplam:", self.total_label)
        
        # Butonlar
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addRow(button_box)
        
        self.setLayout(layout)
        
        # Stil
        self.setStyleSheet("""
            QDialog {
                background-color: #1f2937;
                color: white;
            }
            QLabel {
                color: white;
                font-size: 12px;
            }
            QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
                background-color: #374151;
                color: white;
                padding: 8px;
                border: 1px solid #4b5563;
                border-radius: 4px;
                font-size: 12px;
            }
            QComboBox QAbstractItemView {
                background-color: #374151;
                color: white;
                selection-background-color: #4b5563;
            }
            QPushButton {
                padding: 8px 16px;
                font-size: 12px;
                background-color: #374151;
                color: white;
                border: 1px solid #4b5563;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #4b5563;
            }
        """)
        
    def update_total(self):
        total = self.quantity_spin.value() * self.price_spin.value()
        self.total_label.setText(f"{total:.2f} TL")
        
    def fill_form(self, order_data):
        self.order_no_edit.setText(order_data.get('product_code', ''))
        self.customer_edit.setText(order_data.get('customer_name', ''))
        self.product_combo.setCurrentText(order_data.get('product_name', ''))
        self.quantity_spin.setValue(int(order_data.get('quantity', 1)))
        self.price_spin.setValue(float(order_data.get('unit_price', 0)))
        
    def get_order_data(self):
        product_code = self.order_no_edit.text()
        quantity = self.quantity_spin.value()
        
        # Stok kontrolü yap
        stock_item = self.db.get_stock_item_by_code(product_code)
        if stock_item is None:
            QMessageBox.warning(self, "Uyarı", "Bu ürün kodu stokta bulunamadı!")
            return None
            
        stock_quantity = stock_item['miktar']
        real_stock_quantity = stock_item.get('gercek_stok', stock_quantity)
        
        if quantity > stock_quantity:
            reply = QMessageBox.question(self, "Stok Uyarısı",
                                    f"Stokta yeterli ürün yok! Mevcut stok: {stock_quantity}\nYine de sipariş eklemek istiyor musunuz?",
                                    QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.No:
                return None
        
        # Gerçek sipariş mi sorusu
        reply = QMessageBox.question(self, "Sipariş Türü",
                                "Bu gerçek bir sipariş mi? (Stok ve gerçek stok düşülecek)\n\n"
                                "Hayır seçeneği sadece stok düşer (demo/test amaçlı)",
                                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
                                QMessageBox.Yes)
        
        if reply == QMessageBox.Cancel:
            return None
            
        is_real_order = (reply == QMessageBox.Yes)
        
        return {
            'product_code': product_code,
            'customer_name': self.customer_edit.text(),
            'product_name': self.product_combo.currentText(),
            'quantity': quantity,
            'unit_price': self.price_spin.value(),
            'is_real_order': is_real_order,
            'current_stock': stock_quantity,
            'current_real_stock': real_stock_quantity
        }

class DailyOrdersWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.orders_data = []
        self.initUI()
        self.load_orders_from_db()
        
    def initUI(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(25, 25, 25, 25)
        
        # Başlık
        title = QLabel("Günlük Siparişler")
        title.setFont(QFont("Arial", 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                color: white;
                padding: 15px;
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, 
                           stop:0 #1e3a8a, stop:1 #1e40af);
                border-radius: 12px;
                margin-bottom: 10px;
            }
        """)
        
        # Tarih ve özet bilgiler
        info_widget = QWidget()
        info_widget.setStyleSheet("""
            QWidget {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1,
                           stop:0 #374151, stop:1 #1f2937);
                border-radius: 15px;
                border: 1px solid #4b5563;
            }
        """)
        
        info_layout = QHBoxLayout(info_widget)
        info_layout.setSpacing(20)
        info_layout.setContentsMargins(25, 20, 25, 20)
        
        # Tarih kartı
        date_card = QWidget()
        date_card.setFixedSize(200, 80)
        date_card.setStyleSheet("""
            QWidget {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1,
                           stop:0 #3b82f6, stop:1 #1d4ed8);
                border-radius: 12px;
                border: none;
            }
        """)
        
        date_layout = QVBoxLayout(date_card)
        date_layout.setContentsMargins(15, 15, 15, 15)
        
        date_icon = QLabel("📅")
        date_icon.setFont(QFont("Arial", 16))
        date_icon.setAlignment(Qt.AlignCenter)
        
        date_label = QLabel(f"{datetime.now().strftime('%d.%m.%Y')}")
        date_label.setFont(QFont("Arial", 12, QFont.Bold))
        date_label.setAlignment(Qt.AlignCenter)
        date_label.setStyleSheet("color: white;")
        
        date_text = QLabel("Tarih")
        date_text.setFont(QFont("Arial", 10))
        date_text.setAlignment(Qt.AlignCenter)
        date_text.setStyleSheet("color: white;")
        
        date_layout.addWidget(date_icon)
        date_layout.addWidget(date_label)
        date_layout.addWidget(date_text)
        
        # Toplam sipariş kartı
        orders_card = QWidget()
        orders_card.setFixedSize(200, 80)
        orders_card.setStyleSheet("""
            QWidget {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1,
                           stop:0 #10b981, stop:1 #059669);
                border-radius: 12px;
                border: none;
            }
        """)
        
        orders_layout = QVBoxLayout(orders_card)
        orders_layout.setContentsMargins(15, 15, 15, 15)
        
        orders_icon = QLabel("📦")
        orders_icon.setFont(QFont("Arial", 16))
        orders_icon.setAlignment(Qt.AlignCenter)
        
        self.total_orders_label = QLabel("0")
        self.total_orders_label.setFont(QFont("Arial", 14, QFont.Bold))
        self.total_orders_label.setAlignment(Qt.AlignCenter)
        self.total_orders_label.setStyleSheet("color: white;")
        
        orders_text = QLabel("Toplam Sipariş")
        orders_text.setFont(QFont("Arial", 10))
        orders_text.setAlignment(Qt.AlignCenter)
        orders_text.setStyleSheet("color: white;")
        
        orders_layout.addWidget(orders_icon)
        orders_layout.addWidget(self.total_orders_label)
        orders_layout.addWidget(orders_text)
        
        # Toplam tutar kartı
        amount_card = QWidget()
        amount_card.setFixedSize(200, 80)
        amount_card.setStyleSheet("""
            QWidget {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1,
                           stop:0 #f59e0b, stop:1 #d97706);
                border-radius: 12px;
                border: none;
            }
        """)
        
        amount_layout = QVBoxLayout(amount_card)
        amount_layout.setContentsMargins(15, 15, 15, 15)
        
        amount_icon = QLabel("💰")
        amount_icon.setFont(QFont("Arial", 16))
        amount_icon.setAlignment(Qt.AlignCenter)
        
        self.total_amount_label = QLabel("0.00 TL")
        self.total_amount_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.total_amount_label.setAlignment(Qt.AlignCenter)
        self.total_amount_label.setStyleSheet("color: white;")
        
        amount_text = QLabel("Toplam Tutar")
        amount_text.setFont(QFont("Arial", 10))
        amount_text.setAlignment(Qt.AlignCenter)
        amount_text.setStyleSheet("color: white;")
        
        amount_layout.addWidget(amount_icon)
        amount_layout.addWidget(self.total_amount_label)
        amount_layout.addWidget(amount_text)
        
        # Kartları info layout'a ekle
        info_layout.addWidget(date_card)
        info_layout.addStretch()
        info_layout.addWidget(orders_card)
        info_layout.addWidget(amount_card)
        
        # Sipariş işlemleri butonları
        action_layout = QHBoxLayout()
        
        add_btn = QPushButton("Yeni Sipariş Ekle")
        add_btn.clicked.connect(self.add_order)
        add_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1,
                           stop:0 #059669, stop:1 #047857);
                color: white;
                padding: 12px 24px;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1,
                           stop:0 #065f46, stop:1 #064e3b);
                transform: translateY(-2px);
            }
            QPushButton:pressed {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1,
                           stop:0 #054d38, stop:1 #043d2e);
            }
        """)
        
        edit_btn = QPushButton("Düzenle")
        edit_btn.clicked.connect(self.edit_order)
        edit_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1,
                           stop:0 #f59e0b, stop:1 #d97706);
                color: white;
                padding: 12px 24px;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1,
                           stop:0 #d97706, stop:1 #b45309);
                transform: translateY(-2px);
            }
            QPushButton:pressed {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1,
                           stop:0 #b45309, stop:1 #92400e);
            }
        """)
        
        delete_btn = QPushButton("Sil")
        delete_btn.clicked.connect(self.delete_order)
        delete_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1,
                           stop:0 #ef4444, stop:1 #dc2626);
                color: white;
                padding: 12px 24px;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1,
                           stop:0 #dc2626, stop:1 #b91c1c);
                transform: translateY(-2px);
            }
            QPushButton:pressed {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1,
                           stop:0 #b91c1c, stop:1 #991b1b);
            }
        """)
        
        action_layout.addWidget(add_btn)
        action_layout.addWidget(edit_btn)
        action_layout.addWidget(delete_btn)
        action_layout.addStretch()
        
        # Siparişler tablosu
        self.orders_table = QTableWidget()
        self.orders_table.setColumnCount(7)
        self.orders_table.setHorizontalHeaderLabels([
            "Sıra No", "Ürün kodu", "Müşteri", "Ürün", "Adet", "Birim Fiyat", "Toplam"
        ])
        
        # Tablo stilini ayarla
        self.orders_table.setStyleSheet("""
            QTableWidget {
                background-color: #1f2937;
                color: white;
                border: 1px solid #374151;
                border-radius: 12px;
                gridline-color: #374151;
                font-family: Arial;
                font-size: 12px;
            }
            QTableWidget::item {
                padding: 12px;
                border-bottom: 1px solid #374151;
                color: white;
            }
            QTableWidget::item:selected {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1,
                           stop:0 #3b82f6, stop:1 #1d4ed8);
                color: white;
            }
            QHeaderView::section {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1,
                           stop:0 #111827, stop:1 #1f2937);
                color: white;
                padding: 15px 12px;
                border: none;
                border-radius: 8px;
                margin: 2px;
                font-weight: bold;
                font-size: 13px;
            }
            QHeaderView::section:hover {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1,
                           stop:0 #1f2937, stop:1 #111827);
                color: white;
            }
        """)
        
        # Tablo başlıklarını ayarla
        header = self.orders_table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        self.orders_table.setColumnWidth(0, 80)
        
        # Çift tıklama ile düzenleme
        self.orders_table.doubleClicked.connect(self.edit_order)
        
        # Diğer butonlar
        other_button_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("Yenile")
        refresh_btn.clicked.connect(self.refresh_data)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1,
                           stop:0 #3b82f6, stop:1 #2563eb);
                color: white;
                padding: 12px 24px;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1,
                           stop:0 #2563eb, stop:1 #1d4ed8);
                transform: translateY(-2px);
            }
            QPushButton:pressed {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1,
                           stop:0 #1d4ed8, stop:1 #1e40af);
            }
        """)
        
        export_btn = QPushButton("Excel'e Aktar")
        export_btn.clicked.connect(self.export_to_excel)
        export_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1,
                           stop:0 #8b5cf6, stop:1 #7c3aed);
                color: white;
                padding: 12px 24px;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1,
                           stop:0 #7c3aed, stop:1 #6d28d9);
                transform: translateY(-2px);
            }
            QPushButton:pressed {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1,
                           stop:0 #6d28d9, stop:1 #5b21b6);
            }
        """)
        
        other_button_layout.addWidget(refresh_btn)
        other_button_layout.addWidget(export_btn)
        other_button_layout.addStretch()
        
        # Layout'a widget'ları ekle
        main_layout.addWidget(title)
        main_layout.addWidget(info_widget)
        main_layout.addLayout(action_layout)
        main_layout.addWidget(self.orders_table)
        main_layout.addLayout(other_button_layout)
        
        self.setLayout(main_layout)
        
        # Widget'ın genel stil ayarları
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1,
                           stop:0 #1a1a1a, stop:1 #2d2d2d);
                color: white;
            }
        """)
        
    def load_orders_from_db(self):
        """Veritabanından sipariş verilerini yükle"""
        try:
            result = self.db.get_today_orders()
            if result is None:
                raise Exception("Veritabanı bağlantı hatası")
                
            self.orders_data = result
            self.update_table()
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Veritabanından veri yüklenemedi:\n{str(e)}")
            logging.exception("Veritabanı yükleme hatası")
            self.orders_data = []
        
    def update_table(self):
        """Tabloyu güncelle"""
        try:
            self.orders_table.setRowCount(len(self.orders_data))
            
            total_amount = 0
            for row, order in enumerate(self.orders_data):
                # Satır numarasını ekle (ilk sütun)
                row_number_item = QTableWidgetItem(str(row + 1))
                row_number_item.setTextAlignment(Qt.AlignCenter)
                row_number_item.setForeground(QColor("white"))
                row_number_item.setFont(QFont("Arial", 12, QFont.Bold))
                self.orders_table.setItem(row, 0, row_number_item)
                
                # Diğer sütunları ekle - Veritabanı formatına göre
                columns = [
                    order.get('product_code', ''),
                    order.get('customer_name', ''),
                    order.get('product_name', ''),
                    str(order.get('quantity', 0)),
                    f"{float(order.get('unit_price', 0)):.2f}",
                    f"{float(order.get('total_amount', 0)):.2f}"
                ]
                
                for col, value in enumerate(columns):
                    item = QTableWidgetItem(str(value))
                    item.setTextAlignment(Qt.AlignCenter)
                    item.setForeground(QColor("white"))
                    self.orders_table.setItem(row, col + 1, item)
                    
                # Toplam tutarı hesapla
                total_amount += float(order.get('total_amount', 0))
            
            # Özet bilgileri güncelle
            self.total_orders_label.setText(f"{len(self.orders_data)}")
            self.total_amount_label.setText(f"{total_amount:.2f} TL")
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Tablo güncellenirken hata oluştu:\n{str(e)}")
            logging.exception("Tablo güncelleme hatası")
        
    def add_order(self):
        """Yeni sipariş ekle"""
        try:
            dialog = OrderDialog(self)
            if dialog.exec_() == QDialog.Accepted:
                order_data = dialog.get_order_data()
                
                if order_data is None:  # Kullanıcı iptal ettiyse
                    return
                    
                # Validasyon kontrolleri
                if not order_data['product_code']:
                    QMessageBox.warning(self, "Uyarı", "Ürün kodu boş olamaz!")
                    return
                    
                if not order_data['customer_name']:
                    QMessageBox.warning(self, "Uyarı", "Müşteri adı boş olamaz!")
                    return
                    
                if not order_data['product_name']:
                    QMessageBox.warning(self, "Uyarı", "Ürün adı boş olamaz!")
                    return
                    
                if order_data['quantity'] <= 0:
                    QMessageBox.warning(self, "Uyarı", "Miktar 0'dan büyük olmalıdır!")
                    return
                    
                if order_data['unit_price'] <= 0:
                    QMessageBox.warning(self, "Uyarı", "Birim fiyat 0'dan büyük olmalıdır!")
                    return

                # Veritabanına ekle
                result = self.db.add_daily_order(
                    product_code=order_data['product_code'],
                    customer_name=order_data['customer_name'],
                    product_name=order_data['product_name'],
                    quantity=order_data['quantity'],
                    unit_price=order_data['unit_price'],
                    is_real_order=order_data['is_real_order']
                )
                
                if result:
                    self.load_orders_from_db()
                    QMessageBox.information(self, "Başarılı", "Sipariş başarıyla eklendi!")
                else:
                    QMessageBox.critical(self, "Hata", "Sipariş eklenirken bir hata oluştu!")
                    
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Sipariş eklenirken beklenmeyen bir hata oluştu:\n{str(e)}")
            logging.exception("Sipariş ekleme hatası")
                
    def edit_order(self):
        """Seçili siparişi düzenle"""
        try:
            current_row = self.orders_table.currentRow()
            if current_row == -1:
                QMessageBox.warning(self, "Uyarı", "Düzenlemek için bir sipariş seçin!")
                return
                
            order_data = self.orders_data[current_row]
            dialog = OrderDialog(self, order_data)
            if dialog.exec_() == QDialog.Accepted:
                new_order_data = dialog.get_order_data()
                
                # Validasyon kontrolleri
                if not new_order_data['product_code']:
                    QMessageBox.warning(self, "Uyarı", "Ürün kodu boş olamaz!")
                    return
                    
                if not new_order_data['customer_name']:
                    QMessageBox.warning(self, "Uyarı", "Müşteri adı boş olamaz!")
                    return
                    
                if not new_order_data['product_name']:
                    QMessageBox.warning(self, "Uyarı", "Ürün adı boş olamaz!")
                    return
                    
                if new_order_data['quantity'] <= 0:
                    QMessageBox.warning(self, "Uyarı", "Miktar 0'dan büyük olmalıdır!")
                    return
                    
                if new_order_data['unit_price'] <= 0:
                    QMessageBox.warning(self, "Uyarı", "Birim fiyat 0'dan büyük olmalıdır!")
                    return

                # Ürün kodu tekrar kontrolü (kendisi hariç)
                if self.db.check_product_code_exists(new_order_data['product_code'], exclude_id=order_data.get('id')):
                    QMessageBox.warning(self, "Uyarı", "Bu ürün kodu zaten mevcut!")
                    return
                    
                # Veritabanında güncelle
                result = self.db.update_daily_order(
                    order_id=order_data['id'],
                    product_code=new_order_data['product_code'],
                    customer_name=new_order_data['customer_name'],
                    product_name=new_order_data['product_name'],
                    quantity=new_order_data['quantity'],
                    unit_price=new_order_data['unit_price']
                )
                
                if result:
                    self.load_orders_from_db()
                    QMessageBox.information(self, "Başarılı", "Sipariş başarıyla güncellendi!")
                else:
                    QMessageBox.critical(self, "Hata", "Sipariş güncellenirken bir hata oluştu!")
                    
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Sipariş güncellenirken beklenmeyen bir hata oluştu:\n{str(e)}")
            logging.exception("Sipariş güncelleme hatası")
            
    def delete_order(self):
        """Seçili siparişi sil"""
        try:
            current_row = self.orders_table.currentRow()
            if current_row == -1:
                QMessageBox.warning(self, "Uyarı", "Silmek için bir sipariş seçin!")
                return
                
            order_data = self.orders_data[current_row]
            reply = QMessageBox.question(self, "Silme Onayı", 
                                       f"{order_data.get('product_name', 'Bu sipariş')} silinsin mi?",
                                       QMessageBox.Yes | QMessageBox.No, 
                                       QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                result = self.db.delete_daily_order(order_data['id'])
                
                if result:
                    self.load_orders_from_db()
                    QMessageBox.information(self, "Başarılı", "Sipariş başarıyla silindi!")
                else:
                    QMessageBox.critical(self, "Hata", "Sipariş silinirken bir hata oluştu!")
                    
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Sipariş silinirken beklenmeyen bir hata oluştu:\n{str(e)}")
            logging.exception("Sipariş silme hatası")
        
    def refresh_data(self):
        """Veri yenileme fonksiyonu"""
        try:
            self.load_orders_from_db()
            QMessageBox.information(self, "Başarılı", "Veriler yenilendi!")
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Veriler yenilenirken hata oluştu:\n{str(e)}")
            logging.exception("Veri yenileme hatası")
        
    def export_to_excel(self):
        """Excel'e aktarma fonksiyonu"""
        try:
            # Basit bir Excel export işlemi
            from openpyxl import Workbook
            from datetime import datetime
            
            wb = Workbook()
            ws = wb.active
            ws.title = "Siparişler"
            
            # Başlıklar
            headers = ["Ürün Kodu", "Müşteri", "Ürün", "Adet", "Birim Fiyat", "Toplam"]
            ws.append(headers)
            
            # Veriler
            for order in self.orders_data:
                ws.append([
                    order.get('product_code', ''),
                    order.get('customer_name', ''),
                    order.get('product_name', ''),
                    order.get('quantity', 0),
                    order.get('unit_price', 0),
                    order.get('total_amount', 0)
                ])
            
            # Dosyayı kaydet
            filename = f"siparisler_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            wb.save(filename)
            
            QMessageBox.information(self, "Başarılı", f"Siparişler {filename} dosyasına aktarıldı!")
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Excel'e aktarım sırasında hata oluştu:\n{str(e)}")
            logging.exception("Excel export hatası")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle("Finansal Yönetim Sistemi - Günlük Siparişler")
        self.setGeometry(100, 100, 1200, 800)
        
        # Ana widget
        central_widget = DailyOrdersWidget()
        self.setCentralWidget(central_widget)
        
        # Pencere ikonu ve stil
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1,
                           stop:0 #111827, stop:1 #1f2937);
                color: white;
            }
        """)

def main():
    app = QApplication(sys.argv)
    
    # Uygulama stili
    app.setStyle('Fusion')
    
    # Ana pencere
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()