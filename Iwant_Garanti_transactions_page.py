# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                            QTableWidgetItem, QPushButton, QLabel, QComboBox, 
                            QHeaderView, QFrame, QLineEdit, QDateEdit)
from PyQt5.QtCore import QDate, Qt, pyqtSignal
from database_manager import DatabaseManager

class IwantGarantiTransactionsPageWidget(QWidget):
    back_to_main = pyqtSignal()
    balance_updated = pyqtSignal(float)
    
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.setupUi()
        self.load_iwant_garanti_transactions()

    def setupUi(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        self.setStyleSheet("""
            QWidget { background-color: #1a1a1a; color: #ffffff; }
            QFrame { background-color: #2a2a2a; border: 1px solid #404040; border-radius: 10px; }
            QPushButton { 
                padding: 8px; 
                border-radius: 5px; 
                font-weight: bold;
            }
        """)
        
        # Header
        self.create_header(main_layout)
        # Filtre
        self.create_filter_section(main_layout)
        # Tablo
        self.create_table(main_layout)
        # Özet
        self.create_summary_section(main_layout)

    def create_header(self, main_layout):
        header_frame = QFrame()
        header_frame.setStyleSheet("background-color: #2a2a2a; border: 2px solid #4a9eff; border-radius: 15px;")
        header_layout = QHBoxLayout(header_frame)
        
        title_label = QLabel("🏦 IWANT GARANTİ İŞLEMLERİ")
        title_label.setFont(QtGui.QFont('Segoe UI', 20, QtGui.QFont.Bold))
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        # Yenile butonu
        refresh_btn = QPushButton("🔄 Yenile")
        refresh_btn.setStyleSheet("background-color: #4a9eff; color: white;")
        refresh_btn.clicked.connect(self.load_iwant_garanti_transactions)
        header_layout.addWidget(refresh_btn)
        
        main_layout.addWidget(header_frame)

    def create_filter_section(self, main_layout):
        filter_frame = QFrame()
        filter_layout = QHBoxLayout(filter_frame)
        
        # Tarih Filtresi
        filter_layout.addWidget(QLabel("Tarih Aralığı:"))
        self.start_date = QDateEdit()
        self.start_date.setDate(QDate.currentDate().addDays(-30))
        self.end_date = QDateEdit()
        self.end_date.setDate(QDate.currentDate())
        for date_edit in [self.start_date, self.end_date]:
            date_edit.setCalendarPopup(True)
            date_edit.setStyleSheet("padding: 8px; background-color: #1a1a1a; color: white;")
        filter_layout.addWidget(self.start_date)
        filter_layout.addWidget(QLabel("-"))
        filter_layout.addWidget(self.end_date)
        
        # İşlem Türü
        filter_layout.addWidget(QLabel("İşlem Türü:"))
        self.transaction_type_combo = QComboBox()
        self.transaction_type_combo.addItems(["Tümü", "Gider", "Gelir"])
        self.transaction_type_combo.setStyleSheet("padding: 8px; background-color: #1a1a1a; color: white;")
        filter_layout.addWidget(self.transaction_type_combo)
        
        # Filtrele Butonu
        filter_btn = QPushButton("🔍 Filtrele")
        filter_btn.setStyleSheet("background-color: #4a9eff; color: white;")
        filter_btn.clicked.connect(self.load_iwant_garanti_transactions)
        filter_layout.addWidget(filter_btn)
        
        main_layout.addWidget(filter_frame)

    def create_table(self, main_layout):
        self.table = QTableWidget()
        self.table.setColumnCount(7)  # Sil butonu için sütun eklendi
        self.table.setHorizontalHeaderLabels([
            "Tarih", "Açıklama", "Para Birimi", "İşlem Türü", "Miktar", "TL Karşılığı", "Sil"
        ])
        
        self.table.setStyleSheet("""
            QTableWidget { background-color: #2a2a2a; color: white; }
            QHeaderView::section { background-color: #1a1a1a; padding: 12px; }
        """)
        
        # Sütun Ayarları
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)  # Tarih
        header.setSectionResizeMode(1, QHeaderView.Stretch) # Açıklama
        self.table.setColumnWidth(0, 100)
        self.table.setColumnWidth(2, 100)
        self.table.setColumnWidth(6, 80)  # Sil butonu sütunu genişliği
        main_layout.addWidget(self.table)

    def create_summary_section(self, main_layout):
        summary_frame = QFrame()
        summary_layout = QHBoxLayout(summary_frame)
        
        self.total_expense_label = QLabel("Toplam Gider: ₺0.00")
        self.total_expense_label.setStyleSheet("color: #ff6b6b; font-weight: bold;")
        
        self.total_income_label = QLabel("Toplam Gelir: ₺0.00")
        self.total_income_label.setStyleSheet("color: #51cf66; font-weight: bold;")
        
        self.net_amount_label = QLabel("Net: ₺0.00")
        self.net_amount_label.setStyleSheet("color: #4a9eff; font-weight: bold;")
        
        for label in [self.total_expense_label, self.total_income_label, self.net_amount_label]:
            summary_layout.addWidget(label)
            summary_layout.addStretch()
        
        main_layout.addWidget(summary_frame)

    def add_row_to_table(self, data, transaction_type, color):
        row = self.table.rowCount()
        self.table.insertRow(row)
        
        # Önce standart öğeleri ekle
        items = [
            QTableWidgetItem(QDate.fromString(data['tarih'][:10], "yyyy-MM-dd").toString("dd.MM.yyyy")),
            QTableWidgetItem(data['aciklama']),
            QTableWidgetItem(data['para_birimi']),
            QTableWidgetItem(transaction_type),
            QTableWidgetItem(f"{data['miktar']:.2f}"),
            QTableWidgetItem(f"₺{data.get('tl_karsiligi', data['miktar']):.2f}"),
            QTableWidgetItem(str(data.get('id', '')))  # ID'yi 6. sütuna ekle
        ]
        
        # ID sütununu gizle
        items[6].setFlags(QtCore.Qt.NoItemFlags)
        
        for col, item in enumerate(items):
            self.table.setItem(row, col, item)
            if 3 <= col <= 5:  # İşlem türü ve miktarlar
                item.setForeground(QtGui.QColor(color))
                if col >= 4:
                    item.setTextAlignment(Qt.AlignRight|Qt.AlignVCenter)
        
        # Sil butonu ekle
        delete_btn = QPushButton("🗑️ Sil")
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff6b6b;
                color: white;
                padding: 5px;
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #e05555; }
        """)
        delete_btn.clicked.connect(lambda _, r=row: self.delete_transaction(r))
        self.table.setCellWidget(row, 6, delete_btn)

    def delete_transaction(self, row):
        # Kullanıcıdan onay al
        reply = QtWidgets.QMessageBox.question(
            self, 'Onay',
            'Bu işlemi silmek istediğinize emin misiniz?',
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No
        )
        
        if reply == QtWidgets.QMessageBox.Yes:
            try:
                # Gizli ID'yi doğru şekilde al
                transaction_id_item = self.table.item(row, 6)  # 6. sütun gizli ID
                if not transaction_id_item:
                    raise ValueError("İşlem ID'si bulunamadı")
                    
                transaction_id = int(transaction_id_item.text())
                
                # Veritabanından sil
                if self.table.item(row, 3).text() == "Gelir":
                    success = self.db.delete_income(transaction_id, soft=False)
                else:
                    success = self.db.delete_expense(transaction_id, soft=False)
                
                if success:
                    self.table.removeRow(row)
                    self.update_summary()
                    QtWidgets.QMessageBox.information(self, "Başarılı", "İşlem başarıyla silindi.")
                else:
                    QtWidgets.QMessageBox.warning(self, "Hata", "Silme işlemi başarısız oldu.")
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Hata", f"Bir hata oluştu:\n{str(e)}")

    def load_iwant_garanti_transactions(self):
        try:
            start_date = self.start_date.date().toString("yyyy-MM-dd")
            end_date = self.end_date.date().toString("yyyy-MM-dd")
            transaction_type = self.transaction_type_combo.currentText()
            
            expenses = []
            incomes = []
            
            if transaction_type in ["Tümü", "Gider"]:
                all_expenses = self.db.get_expenses_by_date_range(start_date, end_date)
                expenses = [exp for exp in all_expenses if exp['odeme_turu'] == 'Iwant Garanti']
            
            if transaction_type in ["Tümü", "Gelir"]:
                all_incomes = self.db.get_incomes_by_date_range(start_date, end_date)
                incomes = [inc for inc in all_incomes if inc.get('odeme_turu') == 'Iwant Garanti']
            
            self.table.setRowCount(0)
            
            for expense in expenses:
                self.add_row_to_table(expense, "Gider", "#ff6b6b")
            
            for income in incomes:
                self.add_row_to_table(income, "Gelir", "#51cf66")
            
            self.table.sortItems(0, Qt.DescendingOrder)
            self.update_summary()
            
        except Exception as e:
            print(f"Hata: {str(e)}")
            QtWidgets.QMessageBox.critical(self, "Hata", f"Veri yüklenirken hata oluştu:\n{str(e)}")

    def update_summary(self):
        total_expense = 0
        total_income = 0
        
        for row in range(self.table.rowCount()):
            transaction_type = self.table.item(row, 3).text()
            amount = float(self.table.item(row, 5).text().replace('₺', '').replace(',', '.'))
            
            if transaction_type == "Gider":
                total_expense += amount
            elif transaction_type == "Gelir":
                total_income += amount
        
        net_amount = total_income - total_expense
        
        self.total_expense_label.setText(f"Toplam Gider: ₺{total_expense:.2f}")
        self.total_income_label.setText(f"Toplam Gelir: ₺{total_income:.2f}")
        self.net_amount_label.setText(f"Net: ₺{net_amount:.2f}")
        
        # Net duruma göre renk güncelleme
        color = "#51cf66" if net_amount >= 0 else "#ff6b6b"
        self.net_amount_label.setStyleSheet(f"color: {color}; font-weight: bold;")
        
        # Ana arayüze bakiye bilgisini gönder
        self.balance_updated.emit(net_amount)

    def recalculate_balance(self):
        """Diğer sayfalardan Iwant Garanti işlemi eklendiğinde çağrılır"""
        self.load_iwant_garanti_transactions()

if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    window = IwantGarantiTransactionsPageWidget()
    window.show()
    app.exec_()