from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                            QTableWidgetItem, QPushButton, QLabel, QLineEdit, 
                            QComboBox, QDateEdit, QHeaderView, QMessageBox)
from PyQt5.QtCore import QDate, QTimer, Qt
import requests
from database_manager import DatabaseManager  
from datetime import datetime

class IncomePageWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.setupUi()
        self.setup_timer()
        self.load_exchange_rate()
        self.load_incomes_from_db()

    def setupUi(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        self.setStyleSheet("""
            QWidget { background-color: #2c3e50; color: white; font-family: 'Segoe UI', Arial; }
            QLabel { color: white; }
        """)
        
        # Başlık
        title_label = QLabel("💼 GELİR YÖNETİMİ")
        title_font = QtGui.QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                background-color: #34495e;
                padding: 15px;
                border-radius: 10px;
                border: 2px solid #e74c3c;
            }
        """)
        main_layout.addWidget(title_label)
        
        self.create_exchange_rate_section(main_layout)
        self.create_add_income_section(main_layout)
        self.create_table(main_layout)
        self.create_total_section(main_layout)

    def create_exchange_rate_section(self, main_layout):
        exchange_frame = QtWidgets.QFrame()
        exchange_frame.setStyleSheet("""
            QFrame {
                background-color: #34495e;
                border: 2px solid #e74c3c;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        exchange_layout = QHBoxLayout(exchange_frame)
        
        rate_label = QLabel("USD/TL Kuru:")
        rate_label.setStyleSheet("font-weight: bold; font-size: 14px; min-width: 100px;")
        
        self.exchange_rate_input = QLineEdit()
        self.exchange_rate_input.setPlaceholderText("39.89")
        self.exchange_rate_input.setFixedWidth(120)
        self.exchange_rate_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #e74c3c;
                border-radius: 5px;
                background-color: #2c3e50;
                font-size: 14px;
                min-height: 20px;
            }
            QLineEdit:focus { border: 2px solid #e74c3c; }
        """)
        self.exchange_rate_input.textChanged.connect(self.update_tl_amounts)
        
        update_rate_btn = QPushButton("🔄 Güncelle")
        update_rate_btn.setFixedSize(100, 36)
        update_rate_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover { background-color: #c0392b; }
            QPushButton:pressed { background-color: #a93226; }
        """)
        update_rate_btn.clicked.connect(self.load_exchange_rate)
        
        self.last_update_label = QLabel("Son güncelleme: -")
        self.last_update_label.setStyleSheet("color: #bdc3c7; font-size: 12px; min-width: 150px;")
        
        exchange_layout.addWidget(rate_label)
        exchange_layout.addWidget(self.exchange_rate_input)
        exchange_layout.addWidget(update_rate_btn)
        exchange_layout.addWidget(self.last_update_label)
        exchange_layout.addStretch()
        
        main_layout.addWidget(exchange_frame)

    def create_add_income_section(self, main_layout):
        add_frame = QtWidgets.QFrame()
        add_frame.setStyleSheet("""
            QFrame {
                background-color: #e74c3c;
                border: 2px solid #c0392b;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        add_layout = QVBoxLayout(add_frame)
        
        add_title = QLabel("+ Yeni Gelir Ekle")
        add_title.setStyleSheet("font-weight: bold; font-size: 16px; margin-bottom: 10px;")
        
        form_layout = QHBoxLayout()
        form_layout.setSpacing(10)
        
        # Tarih
        date_container = QVBoxLayout()
        date_label = QLabel("Tarih:")
        date_label.setStyleSheet("font-weight: bold; font-size: 12px; margin-bottom: 5px;")
        
        self.date_input = QDateEdit()
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        self.date_input.setFixedSize(120, 35)
        self.date_input.setStyleSheet("""
            QDateEdit {
                padding: 8px;
                border: 1px solid #c0392b;
                border-radius: 5px;
                background-color: #34495e;
                font-size: 14px;
            }
            QDateEdit::drop-down {
                border: none;
                background-color: #c0392b;
            }
        """)
        
        date_container.addWidget(date_label)
        date_container.addWidget(self.date_input)
        form_layout.addLayout(date_container)
        
        # Açıklama
        desc_container = QVBoxLayout()
        desc_label = QLabel("Açıklama:")
        desc_label.setStyleSheet("font-weight: bold; font-size: 12px; margin-bottom: 5px;")
        
        self.description_input = QLineEdit()
        self.description_input.setPlaceholderText("Gelir açıklaması...")
        self.description_input.setFixedSize(200, 35)
        self.description_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #c0392b;
                border-radius: 5px;
                background-color: #34495e;
                font-size: 14px;
            }
            QLineEdit:focus { border: 2px solid #c0392b; }
        """)
        
        desc_container.addWidget(desc_label)
        desc_container.addWidget(self.description_input)
        form_layout.addLayout(desc_container)
        
        # Para birimi
        currency_container = QVBoxLayout()
        currency_label = QLabel("Para Birimi:")
        currency_label.setStyleSheet("font-weight: bold; font-size: 12px; margin-bottom: 5px;")
        
        self.currency_combo = QComboBox()
        self.currency_combo.addItems(["TL", "USD"])
        self.currency_combo.setFixedSize(100, 35)
        self.currency_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 1px solid #c0392b;
                border-radius: 5px;
                background-color: #34495e;
                font-size: 14px;
            }
            QComboBox::drop-down {
                border: none;
                background-color: #c0392b;
            }
            QComboBox QAbstractItemView {
                background-color: #34495e;
                color: white;
                selection-background-color: #c0392b;
            }
        """)
        
        currency_container.addWidget(currency_label)
        currency_container.addWidget(self.currency_combo)
        form_layout.addLayout(currency_container)
        
        # Ödeme türü
        payment_container = QVBoxLayout()
        payment_label = QLabel("Ödeme Türü:")
        payment_label.setStyleSheet("font-weight: bold; font-size: 12px; margin-bottom: 5px;")
        
        self.payment_combo = QComboBox()
        self.payment_combo.addItems(["CASH", "Tonboo Ziraat", "Tonboo Garanti", "Iwant Garanti", "Iwant Ziraat", "Volkan Amount"])
        self.payment_combo.setFixedSize(150, 35)  # Genişliği artırdık
        self.payment_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 1px solid #c0392b;
                border-radius: 5px;
                background-color: #34495e;
                font-size: 14px;
            }
            QComboBox::drop-down {
                border: none;
                background-color: #c0392b;
            }
            QComboBox QAbstractItemView {
                background-color: #34495e;
                color: white;
                selection-background-color: #c0392b;
                min-width: 200px;  # Açılır menü genişliği
            }
        """)
        
        payment_container.addWidget(payment_label)
        payment_container.addWidget(self.payment_combo)
        form_layout.addLayout(payment_container)
        
        # Miktar
        amount_container = QVBoxLayout()
        amount_label = QLabel("Miktar:")
        amount_label.setStyleSheet("font-weight: bold; font-size: 12px; margin-bottom: 5px;")
        
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("0.00")
        self.amount_input.setFixedSize(120, 35)
        self.amount_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #c0392b;
                border-radius: 5px;
                background-color: #34495e;
                font-size: 14px;
            }
            QLineEdit:focus { border: 2px solid #c0392b; }
        """)
        self.amount_input.textChanged.connect(self.on_amount_changed)
        
        amount_container.addWidget(amount_label)
        amount_container.addWidget(self.amount_input)
        form_layout.addLayout(amount_container)
        
        # Ekle butonu
        add_btn_container = QVBoxLayout()
        add_btn_container.addWidget(QLabel(""))
        
        add_btn = QPushButton("✚ Ekle")
        add_btn.setFixedSize(100, 35)
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 10px 15px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover { background-color: #229954; }
            QPushButton:pressed { background-color: #1e8449; }
        """)
        add_btn.clicked.connect(self.add_income)
        
        add_btn_container.addWidget(add_btn)
        form_layout.addLayout(add_btn_container)
        
        add_layout.addLayout(form_layout)
        main_layout.addWidget(add_frame)

    def create_table(self, main_layout):
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Tarih", "Açıklama", "Para Birimi", "Miktar", "Ödeme Türü", "USD Kuru", "TL Karşılığı"
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
                color: white;
                font-size: 13px;
            }
            QTableWidget::item:selected {
                background-color: #e74c3c;
                color: white;
            }
            QHeaderView::section {
                background-color: #2c3e50;
                padding: 10px;
                border: 1px solid #34495e;
                font-weight: bold;
                color: #ecf0f1;
                font-size: 13px;
            }
        """)
        
        self.table.setAlternatingRowColors(False)
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)
        
        self.table.setColumnWidth(0, 100)
        self.table.setColumnWidth(2, 90)
        self.table.setColumnWidth(4, 110)
        
        main_layout.addWidget(self.table)

    def create_total_section(self, main_layout):
        total_frame = QtWidgets.QFrame()
        total_frame.setStyleSheet("""
            QFrame {
                background-color: #34495e;
                border: 2px solid #e74c3c;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        total_layout = QHBoxLayout(total_frame)
        
        self.total_usd_label = QLabel("Toplam USD: $0.00")
        self.total_usd_label.setStyleSheet("""
            QLabel {
                font-weight: bold;
                font-size: 18px;
                background-color: #e74c3c;
                padding: 10px 15px;
                border-radius: 5px;
            }
        """)
        
        # Butonlar için container oluşturalım
        buttons_container = QWidget()
        buttons_layout = QHBoxLayout(buttons_container)
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.setSpacing(10)
        
        # Düzenle butonu - Boyutları sabitlendi
        edit_btn = QPushButton("✏️ Düzenle")
        edit_btn.setFixedSize(100, 40)  # Genişlik: 100, Yükseklik: 40
        edit_btn.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                border: none;
                padding: 10px 15px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover { background-color: #e67e22; }
            QPushButton:pressed { background-color: #d35400; }
        """)
        edit_btn.clicked.connect(self.edit_selected_row)
        
        # Silme butonu - Boyutları sabitlendi
        delete_btn = QPushButton("🗑️ Sil")
        delete_btn.setFixedSize(100, 40)  # Genişlik: 100, Yükseklik: 40
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
            QPushButton:hover { background-color: #c0392b; }
            QPushButton:pressed { background-color: #a93226; }
        """)
        delete_btn.clicked.connect(self.delete_selected_row)
        
        buttons_layout.addWidget(edit_btn)
        buttons_layout.addWidget(delete_btn)
        
        self.total_tl_label = QLabel("Toplam TL: ₺0.00")
        self.total_tl_label.setStyleSheet("""
            QLabel {
                font-weight: bold;
                font-size: 18px;
                background-color: #e74c3c;
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
        self.timer.start(300000)  # 5 dakikada bir

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

    def on_amount_changed(self):
        pass

    def update_tl_amounts(self):
        try:
            new_rate = float(self.exchange_rate_input.text().replace(',', '.'))
            
            for row in range(self.table.rowCount()):
                currency = self.table.item(row, 2).text()
                amount = float(self.table.item(row, 3).text())
                
                if currency == "USD":
                    # Sadece yeni eklenenler için orijinal kuru koru
                    if not self.table.item(row, 5) or self.table.item(row, 5).text() == "-":
                        self.table.setItem(row, 5, QTableWidgetItem(f"{new_rate:.2f}"))
                        tl_amount = amount * new_rate
                        self.table.setItem(row, 6, QTableWidgetItem(f"₺{tl_amount:.2f}"))
        except ValueError:
            pass

    def recalculate_row(self, row):
        try:
            currency = self.table.item(row, 2).text()
            amount = float(self.table.item(row, 3).text().replace(',', '.'))
            
            try:
                usd_rate = float(self.exchange_rate_input.text().replace(',', '.'))
            except:
                usd_rate = 39.89
            
            if currency == "USD":
                tl_amount = amount * usd_rate
                self.table.setItem(row, 5, QTableWidgetItem(f"{usd_rate:.2f}"))
            elif currency == "TL":
                tl_amount = amount
                self.table.setItem(row, 5, QTableWidgetItem("-"))
            
            self.table.setItem(row, 6, QTableWidgetItem(f"₺{tl_amount:.2f}"))
        except (ValueError, AttributeError):
            pass

    def update_totals(self):
        total_usd = 0
        total_tl = 0
        
        for row in range(self.table.rowCount()):
            try:
                currency = self.table.item(row, 2).text()
                amount = float(self.table.item(row, 3).text())
                
                if currency == "USD":
                    total_usd += amount
                
                tl_text = self.table.item(row, 6).text().replace('₺', '').replace(',', '.')
                total_tl += float(tl_text)
            except (ValueError, AttributeError):
                continue
        
        self.total_usd_label.setText(f"Toplam USD: ${total_usd:.2f}")
        self.total_tl_label.setText(f"Toplam TL: ₺{total_tl:.2f}")

    def add_income(self):
        try:
            date = self.date_input.date().toString("dd.MM.yyyy")
            description = self.description_input.text().strip()
            currency = self.currency_combo.currentText()
            amount = float(self.amount_input.text().replace(',', '.'))
            payment_type = self.payment_combo.currentText()
            usd_rate = float(self.exchange_rate_input.text().replace(',', '.')) if currency != "TL" else None
            
            if not description:
                QMessageBox.warning(self, "Uyarı", "Lütfen açıklama giriniz!")
                return
                
            if amount <= 0:
                QMessageBox.warning(self, "Uyarı", "Lütfen geçerli bir miktar giriniz!")
                return
            
            # TL karşılığını hesapla
            if currency == "USD":
                tl_amount = amount * usd_rate
            else:  # TL
                tl_amount = amount
            
            db_result = self.db.add_income(
                tarih=date,
                aciklama=description,
                para_birimi=currency,
                miktar=amount,
                odeme_turu=payment_type,
                usd_kuru=usd_rate,
                tl_karsiligi=tl_amount
            )

            if not db_result:
                QMessageBox.warning(self, "Hata", "Veritabanına kaydedilirken hata oluştu!")
                return
            
            self.table.insertRow(0)
            row = 0
            
            self.table.setItem(row, 0, QTableWidgetItem(date))
            self.table.setItem(row, 1, QTableWidgetItem(description))
            self.table.setItem(row, 2, QTableWidgetItem(currency))
            self.table.setItem(row, 3, QTableWidgetItem(f"{amount:.2f}"))
            self.table.setItem(row, 4, QTableWidgetItem(payment_type))
            self.table.setItem(row, 5, QTableWidgetItem(f"{usd_rate:.2f}" if usd_rate else "-"))
            self.table.setItem(row, 6, QTableWidgetItem(f"₺{tl_amount:.2f}"))
            
            self.description_input.clear()
            self.amount_input.clear()
            
            self.update_totals()
        except ValueError:
            QMessageBox.warning(self, "Uyarı", "Lütfen geçerli bir miktar giriniz!")

    def load_incomes_from_db(self):
  
        incomes = sorted(self.db.get_all_incomes(), key=lambda x: x['id'], reverse=True)
        self.table.setRowCount(0)

        for income in incomes:
            row = self.table.rowCount()
            self.table.insertRow(row)

            date_obj = datetime.strptime(income['tarih'], "%Y-%m-%d")
            date_str = date_obj.strftime("%d.%m.%Y")
            
            self.table.setItem(row, 0, QTableWidgetItem(date_str))
            self.table.setItem(row, 1, QTableWidgetItem(income['aciklama']))
            self.table.setItem(row, 2, QTableWidgetItem(income['para_birimi']))
            self.table.setItem(row, 3, QTableWidgetItem(f"{income['miktar']:.2f}"))
            self.table.setItem(row, 4, QTableWidgetItem(income.get('odeme_turu', 'Nakit')))

            if income['usd_kuru']:
                self.table.setItem(row, 5, QTableWidgetItem(f"{income['usd_kuru']:.2f}"))
            else:
                self.table.setItem(row, 5, QTableWidgetItem("-"))
            if income['tl_karsiligi']:
                self.table.setItem(row, 6, QTableWidgetItem(f"₺{income['tl_karsiligi']:.2f}"))
            else:
                self.recalculate_row(row)
        
        self.update_totals()

        

    def delete_selected_row(self):
        current_row = self.table.currentRow()
        if current_row >= 0:
            reply = QMessageBox.question(self, 'Silme Onayı', 
                                    'Bu gelir kaydını silmek istediğinizden emin misiniz?',
                                    QMessageBox.Yes | QMessageBox.No, 
                                    QMessageBox.No)
            if reply == QMessageBox.Yes:
                # Veritabanından silme işlemi
                income_data = []
                for col in range(self.table.columnCount()):
                    item = self.table.item(current_row, col)
                    if item:
                        income_data.append(item.text())

                if len(income_data) > 1:
                    incomes = self.db.search_incomes(income_data[1])
                    if incomes:
                        self.db.delete_income(incomes[0]['id'])  # veya update_income ile aktif=False
                
                self.table.removeRow(current_row)
                self.update_totals()
        else:
            QMessageBox.information(self, "Bilgi", "Lütfen silmek istediğiniz gelir kaydını seçin.")

    def edit_selected_row(self):
        current_row = self.table.currentRow()
        if current_row >= 0:
            # Seçili satırdaki verileri al
            date_text = self.table.item(current_row, 0).text()
            description = self.table.item(current_row, 1).text()
            currency = self.table.item(current_row, 2).text()
            amount = self.table.item(current_row, 3).text()
            payment_type = self.table.item(current_row, 4).text()
            
            # Veritabanından sil (veya pasif hale getir)
            income_data = []
            for col in range(self.table.columnCount()):
                item = self.table.item(current_row, col)
                if item:
                    income_data.append(item.text())
            
            if len(income_data) > 1:
                incomes = self.db.search_incomes(income_data[1])
                if incomes:
                    self.db.delete_income(incomes[0]['id'])  # veya update_income ile aktif=False
            
            # Form alanlarını doldur
            self.date_input.setDate(QDate.fromString(date_text, "dd.MM.yyyy"))
            self.description_input.setText(description)
            self.currency_combo.setCurrentText(currency)
            self.amount_input.setText(amount)
            self.payment_combo.setCurrentText(payment_type)
            
            # Tablodan satırı sil
            self.table.removeRow(current_row)
            self.update_totals()
        else:
            QMessageBox.information(self, "Bilgi", "Lütfen düzenlemek istediğiniz gelir kaydını seçin.")

    def on_table_item_changed(self, item):
        if item.column() == 3:
            self.recalculate_row(item.row())
            self.update_totals()

if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    window = IncomePageWidget()
    window.show()
    app.exec_()