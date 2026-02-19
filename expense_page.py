# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                            QTableWidgetItem, QPushButton, QLabel, QLineEdit, 
                            QComboBox, QDateEdit, QHeaderView, QMessageBox)
from PyQt5.QtCore import QDate, QTimer, Qt
import requests
import json
from database_manager import DatabaseManager

class ExpensePageWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.setupUi()
        self.setup_timer()
        self.load_exchange_rate()
        self.load_expenses()

    def setupUi(self):
        # Ana layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Stil ayarları
        self.setStyleSheet("""
            QWidget {
                background-color: #2c3e50;
                color: white;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QLabel {
                font-size: 14px;
                font-weight: bold;
                margin-bottom: 5px;
            }
            QLineEdit, QDateEdit, QComboBox {
                min-height: 30px;
                background-color: #34495e;
                border: 1px solid #2980b9;
                border-radius: 5px;
                padding: 5px;
                color: white;
            }
            QDateEdit::drop-down, QComboBox::drop-down {
                width: 20px;
                border: none;
                background-color: #2980b9;
            }
            QMessageBox {
                background-color: #34495e;
            }
        """)
        
        # Başlık
        title_label = QLabel("💳 GİDER YÖNETİMİ")
        title_font = QtGui.QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                color: #ecf0f1;
                background-color: #34495e;
                padding: 15px;
                border-radius: 10px;
                border: 2px solid #3498db;
            }
        """)
        main_layout.addWidget(title_label)
        
        # Döviz kuru bölümü
        exchange_frame = QtWidgets.QFrame()
        exchange_frame.setStyleSheet("""
            QFrame {
                background-color: #34495e;
                border: 2px solid #3498db;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        exchange_layout = QHBoxLayout(exchange_frame)
        
        rate_label = QLabel("USD/TL Kuru:")
        self.exchange_rate_input = QLineEdit()
        self.exchange_rate_input.setPlaceholderText("39.89")
        self.exchange_rate_input.setFixedWidth(100)
        self.exchange_rate_input.textChanged.connect(self.update_tl_amounts)
        
        update_rate_btn = QPushButton("🔄 Güncelle")
        update_rate_btn.setFixedWidth(120)
        update_rate_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        update_rate_btn.clicked.connect(self.load_exchange_rate)
        
        self.last_update_label = QLabel("Son güncelleme: -")
        self.last_update_label.setStyleSheet("color: #bdc3c7; font-size: 12px;")
        
        exchange_layout.addWidget(rate_label)
        exchange_layout.addWidget(self.exchange_rate_input)
        exchange_layout.addWidget(update_rate_btn)
        exchange_layout.addWidget(self.last_update_label)
        exchange_layout.addStretch()
        
        main_layout.addWidget(exchange_frame)
        
        # Gider ekleme bölümü - YATAY FORM
        add_frame = QtWidgets.QFrame()
        add_frame.setStyleSheet("""
            QFrame {
                background-color: #3498db;
                border: 2px solid #2980b9;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        form_layout = QHBoxLayout(add_frame)
        form_layout.setSpacing(15)

        # Tarih
        date_container = QVBoxLayout()
        date_label = QLabel("Tarih:")
        self.date_input = QDateEdit()
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        self.date_input.setFixedWidth(120)
        date_container.addWidget(date_label)
        date_container.addWidget(self.date_input)
        form_layout.addLayout(date_container)

        # Açıklama
        desc_container = QVBoxLayout()
        desc_label = QLabel("Açıklama:")
        self.description_input = QLineEdit()
        self.description_input.setPlaceholderText("Gider açıklaması...")
        self.description_input.setFixedWidth(200)
        desc_container.addWidget(desc_label)
        desc_container.addWidget(self.description_input)
        form_layout.addLayout(desc_container)

        # Para Birimi (EUR kaldırıldı)
        currency_container = QVBoxLayout()
        currency_label = QLabel("Para Birimi:")
        self.currency_combo = QComboBox()
        self.currency_combo.addItems(["TL", "USD"])  # EUR kaldırıldı
        self.currency_combo.setFixedWidth(80)
        currency_container.addWidget(currency_label)
        currency_container.addWidget(self.currency_combo)
        form_layout.addLayout(currency_container)

        # Ödeme Türü
        payment_container = QVBoxLayout()
        payment_label = QLabel("Ödeme Türü:")
        self.payment_combo = QComboBox()
        self.payment_combo.addItems(["CASH", "Tonboo Ziraat", "Tonboo Garanti", "Iwant Garanti", "Iwant Ziraat", "Volkan Amount"])
        self.payment_combo.setFixedWidth(120)
        payment_container.addWidget(payment_label)
        payment_container.addWidget(self.payment_combo)
        form_layout.addLayout(payment_container)

        # Miktar
        amount_container = QVBoxLayout()
        amount_label = QLabel("Miktar:")
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("0.00")
        self.amount_input.setFixedWidth(100)
        amount_container.addWidget(amount_label)
        amount_container.addWidget(self.amount_input)
        form_layout.addLayout(amount_container)

        # Ekle Butonu
        add_btn = QPushButton("✚ Ekle")
        add_btn.setFixedSize(100, 60)
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
        """)
        add_btn.clicked.connect(self.add_expense)
        form_layout.addWidget(add_btn)

        main_layout.addWidget(add_frame)
        
        # Tablo
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Tarih", "Açıklama", "Para Birimi", "Ödeme Türü", "Miktar", "USD Kuru", "TL Karşılığı"
        ])
        
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #34495e;
                border: 1px solid #2c3e50;
                border-radius: 10px;
                gridline-color: #2c3e50;
                color: white;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #2c3e50;
            }
            QHeaderView::section {
                background-color: #2c3e50;
                padding: 10px;
                border: 1px solid #34495e;
                font-weight: bold;
            }
        """)
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Fixed)
        header.setSectionResizeMode(3, QHeaderView.Fixed)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)
        
        self.table.setColumnWidth(0, 100)
        self.table.setColumnWidth(2, 100)
        self.table.setColumnWidth(3, 120)
        self.table.setColumnWidth(4, 100)
        self.table.setColumnWidth(5, 100)
        self.table.setColumnWidth(6, 120)
        
        self.table.verticalHeader().setDefaultSectionSize(40)
        
        main_layout.addWidget(self.table)
        
        # Toplam bölümü (Sil ve Düzenle butonları eklendi)
        total_frame = QtWidgets.QFrame()
        total_frame.setStyleSheet("""
            QFrame {
                background-color: #34495e;
                border: 2px solid #3498db;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        total_layout = QHBoxLayout(total_frame)
        
        self.total_usd_label = QLabel("Toplam USD Gider: $0.00")
        self.total_usd_label.setStyleSheet("""
            QLabel {
                font-weight: bold;
                font-size: 16px;
                background-color: #3498db;
                padding: 10px 15px;
                border-radius: 5px;
            }
        """)
        
        # Butonlar için container
        buttons_container = QWidget()
        buttons_layout = QHBoxLayout(buttons_container)
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.setSpacing(10)
        
        # Düzenle butonu
        edit_btn = QPushButton("✏️ Düzenle")
        edit_btn.setFixedSize(100, 40)
        edit_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 15px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover { 
                background-color: #2980b9;
            }
            QPushButton:pressed { 
                background-color: #1f618d;
            }
        """)

        delete_btn = QPushButton("🗑️ Sil")
        delete_btn.setFixedSize(100, 40)
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 10px 15px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover { 
                background-color: #c0392b;
            }
            QPushButton:pressed { 
                background-color: #922b21;
            }
        """)
        delete_btn.clicked.connect(self.delete_selected_row)
        
        buttons_layout.addWidget(edit_btn)
        buttons_layout.addWidget(delete_btn)
        
        self.total_tl_label = QLabel("Toplam TL Gider: ₺0.00")
        self.total_tl_label.setStyleSheet("""
            QLabel {
                font-weight: bold;
                font-size: 16px;
                background-color: #3498db;
                padding: 10px 15px;
                border-radius: 5px;
            }
        """)
        
        total_layout.addWidget(self.total_usd_label)
        total_layout.addStretch()
        total_layout.addWidget(buttons_container)
        total_layout.addStretch()
        total_layout.addWidget(self.total_tl_label)
        
        main_layout.addWidget(total_frame)
        
    def setup_timer(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.load_exchange_rate)
        self.timer.start(300000)
        
    def load_exchange_rate(self):
        try:
            response = requests.get("https://api.exchangerate-api.com/v4/latest/USD", timeout=5)
            if response.status_code == 200:
                data = response.json()
                rate = data['rates'].get('TRY', 39.89)
                self.exchange_rate_input.setText(str(round(rate, 2)))
                self.last_update_label.setText(f"Son güncelleme: {QDate.currentDate().toString('dd.MM.yyyy')}")
            else:
                self.exchange_rate_input.setText("39.89")
        except Exception as e:
            print(f"Kur çekme hatası: {e}")
            self.exchange_rate_input.setText("39.89")
            
    def load_expenses(self):
        expenses = sorted(self.db.get_all_expenses(), key=lambda x: x['id'], reverse=True)
        self.table.setRowCount(0)
        
        for expense in expenses:
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            tarih = QDate.fromString(expense['tarih'][:10], "yyyy-MM-dd").toString("dd.MM.yyyy")
            self.table.setItem(row, 0, QTableWidgetItem(tarih))
            
            self.table.setItem(row, 1, QTableWidgetItem(expense['aciklama']))
            self.table.setItem(row, 2, QTableWidgetItem(expense['para_birimi']))
            self.table.setItem(row, 3, QTableWidgetItem(expense['odeme_turu']))
            
            amount_item = QTableWidgetItem(f"{expense['miktar']:.2f}")
            amount_item.setTextAlignment(Qt.AlignRight|Qt.AlignVCenter)
            self.table.setItem(row, 4, amount_item)
            
            if expense['para_birimi'] == "USD":
                rate_item = QTableWidgetItem(f"{expense['usd_kuru']:.2f}")
            else:
                rate_item = QTableWidgetItem("-")
            rate_item.setTextAlignment(Qt.AlignRight|Qt.AlignVCenter)
            self.table.setItem(row, 5, rate_item)
            
            tl_item = QTableWidgetItem(f"₺{expense['tl_karsiligi']:.2f}")
            tl_item.setTextAlignment(Qt.AlignRight|Qt.AlignVCenter)
            self.table.setItem(row, 6, tl_item)
            
            self.table.item(row, 0).setData(Qt.UserRole, expense['id'])
        
        self.update_totals()
            
    def add_expense(self):
        try:
            date = self.date_input.date().toString("dd.MM.yyyy")
            description = self.description_input.text().strip()
            currency = self.currency_combo.currentText()
            payment_type = self.payment_combo.currentText()
            amount = float(self.amount_input.text().replace(',', '.'))
            
            if not description:
                QMessageBox.warning(self, "Uyarı", "Lütfen açıklama giriniz!")
                return
                
            if amount <= 0:
                QMessageBox.warning(self, "Uyarı", "Lütfen geçerli bir miktar giriniz!")
                return
            
            # Orijinal USD kurunu al ve kaydet
            usd_rate = float(self.exchange_rate_input.text().replace(',', '.')) if currency == "USD" else None
            
            # TL karşılığını hesapla
            if currency == "USD":
                tl_amount = amount * usd_rate
            else:  # TL
                tl_amount = amount

            result = self.db.add_expense(
                tarih=date,
                aciklama=description,
                para_birimi=currency,
                miktar=amount,
                odeme_turu=payment_type,
                usd_kuru=usd_rate,  # Orijinal kuru kaydediyoruz
                tl_karsiligi=tl_amount
            )

            if not result:
                QMessageBox.critical(self, "Hata", "Gider veritabanına kaydedilemedi!")
                return

            self.load_expenses()
            self.description_input.clear()
            self.amount_input.clear()
            
        except ValueError:
            QMessageBox.warning(self, "Uyarı", "Lütfen geçerli bir miktar giriniz!")

    def update_tl_amounts(self):
        try:
            new_rate = float(self.exchange_rate_input.text().replace(',', '.'))
            
            for row in range(self.table.rowCount()):
                # Sadece TL olan veya kuru kaydedilmemiş kayıtları güncelle
                if not self.table.item(row, 5) or self.table.item(row, 5).text() == "-":
                    currency = self.table.item(row, 2).text()
                    amount = float(self.table.item(row, 4).text())
                    
                    if currency == "USD":
                        tl_amount = amount * new_rate
                        self.table.setItem(row, 5, QTableWidgetItem(f"{new_rate:.2f}"))
                        tl_item = QTableWidgetItem(f"₺{tl_amount:.2f}")
                        tl_item.setTextAlignment(Qt.AlignRight|Qt.AlignVCenter)
                        self.table.setItem(row, 6, tl_item)
            
            self.update_totals()
            
        except ValueError:
            pass

    def edit_selected_row(self):
        current_row = self.table.currentRow()
        if current_row >= 0:
            # Seçili satırdaki verileri al
            date_text = self.table.item(current_row, 0).text()
            description = self.table.item(current_row, 1).text()
            currency = self.table.item(current_row, 2).text()
            payment_type = self.table.item(current_row, 3).text()
            amount = self.table.item(current_row, 4).text()
            
            # Veritabanından sil
            expense_id = self.table.item(current_row, 0).data(Qt.UserRole)
            if expense_id:
                self.db.delete_expense(expense_id)
            
            # Form alanlarını doldur
            self.date_input.setDate(QDate.fromString(date_text, "dd.MM.yyyy"))
            self.description_input.setText(description)
            self.currency_combo.setCurrentText(currency)
            self.payment_combo.setCurrentText(payment_type)
            self.amount_input.setText(amount)
            
            # Tablodan satırı sil
            self.table.removeRow(current_row)
            self.update_totals()
        else:
            QMessageBox.information(self, "Bilgi", "Lütfen düzenlemek istediğiniz gider kaydını seçin.")
    
    def delete_selected_row(self):
        current_row = self.table.currentRow()
        if current_row >= 0:
            reply = QMessageBox.question(self, 'Silme Onayı', 
                                       'Bu gider kaydını silmek istediğinizden emin misiniz?',
                                       QMessageBox.Yes | QMessageBox.No, 
                                       QMessageBox.No)
            if reply == QMessageBox.Yes:
                expense_id = self.table.item(current_row, 0).data(Qt.UserRole)
                if expense_id:
                    self.db.delete_expense(expense_id)
                
                self.table.removeRow(current_row)
                self.update_totals()
        else:
            QMessageBox.information(self, "Bilgi", "Lütfen silmek istediğiniz gider kaydını seçin.")
        
    
    
    def update_totals(self):
        total_usd = 0
        total_tl = 0
        
        for row in range(self.table.rowCount()):
            currency = self.table.item(row, 2).text()
            amount = float(self.table.item(row, 4).text())
            
            if currency == "USD":
                total_usd += amount
            
            tl_text = self.table.item(row, 6).text().replace('₺', '').replace(',', '.')
            total_tl += float(tl_text)
        
        self.total_usd_label.setText(f"Toplam USD Gider: ${total_usd:.2f}")
        self.total_tl_label.setText(f"Toplam TL Gider: ₺{total_tl:.2f}")

if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    window = ExpensePageWidget()
    window.show()
    app.exec_()