import os
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QWidget
from income_page import IncomePageWidget
from expense_page import ExpensePageWidget
from stock_page import StockPage
from reference_page import ReferencePage
from daily_orders_page import DailyOrdersWidget
from passwords_page import PasswordManager
from imports_page import ImportsPage
from cash_transactions_page import CashTransactionsPageWidget
from Tonboo_Ziraat_transactions_page import TonbooZiraatTransactionsPageWidget 
from Tonboo_Garanti_transactions_page import TonbooGarantiTransactionsPageWidget
from Iwant_Ziraat_transaction_page import IwantZiraatTransactionsPageWidget
from Iwant_Garanti_transactions_page import IwantGarantiTransactionsPageWidget
from Volkan_Amount_page import VolkanAmountPageWidget


def resource_path(relative_path):
    """PyInstaller .exe içindeyken dosya yollarını düzeltir."""
    base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    return os.path.join(base_path, relative_path)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1240, 969)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.current_user_role = None
        MainWindow.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        
        # Ana frame (sağ üst - hesap bilgileri)
        self.frame = QtWidgets.QFrame(self.centralwidget)
        self.frame.setGeometry(QtCore.QRect(890, 10, 341, 641))
        self.frame.setStyleSheet("""
            background-color: rgba(37, 37, 65, 0.5);
            border-radius: 20px;
            border: 2px solid #3A3A5C;
            box-shadow: 0px 0px 20px rgba(0, 0, 0, 0.5);
        """)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setObjectName("frame")
        
        # Ana başlık (green area - total balance)
        self.label_2 = QtWidgets.QLabel(self.frame)
        self.label_2.setGeometry(QtCore.QRect(20, 50, 301, 91))
        font = QtGui.QFont()
        font.setPointSize(15)
        font.setBold(True)
        font.setWeight(75)
        self.label_2.setFont(font)
        self.label_2.setStyleSheet("background-color: green; color: white;")
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.label_2.setText("0.00 TL")  # Initialize with 0.00 TL
        
        # Chinese text (red area)
        self.label_4 = QtWidgets.QLabel(self.frame)
        self.label_4.setGeometry(QtCore.QRect(80, 10, 181, 31))
        font = QtGui.QFont()
        font.setPointSize(15)
        font.setBold(True)
        font.setWeight(75)
        self.label_4.setFont(font)
        self.label_4.setStyleSheet("color: yellow; background-color: red; border-radius: 10px;")
        self.label_4.setAlignment(QtCore.Qt.AlignCenter)
        self.label_4.setObjectName("label_4")
        self.label_4.setText("资金")  
        
        # Hesap frame'leri (büyüteç butonları kaldırıldı, frame'ler ortalandı)
        self.account_frames = []
        
        # CASH
        self.frame_2 = self.create_account_frame(40, 150, "💵", "CASH", "348.475 TL")
        
        # Tonboo Ziraat
        self.frame_3 = self.create_account_frame(40, 230, "🏦", "Tonboo Ziraat", "348.475 TL")
        
        # Tonboo Garanti
        self.frame_4 = self.create_account_frame(40, 310, "🏦", "Tonboo Garanti", "348.475 TL")
        
        # Iwant Ziraat
        self.frame_5 = self.create_account_frame(40, 390, "🏦", "Iwant Ziraat", "348.475 TL")
        
        # Iwant Garanti
        self.frame_6 = self.create_account_frame(40, 470, "🏦", "Iwant Garanti", "348.475 TL")
        
        # Volkan Amount
        self.frame_8 = self.create_account_frame(40, 550, "🔁", "Volkan Amount", "348.475 TL")
        
        # Arka plan
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(0, 0, 1240, 969))
        self.label.setText("")
        image_path = resource_path("resources/loginbackground2.png")
        self.label.setPixmap(QtGui.QPixmap(image_path))
        self.label.setObjectName("label")
        
        # Ana içerik alanı (beyaz alan)
        self.frame_7 = QtWidgets.QFrame(self.centralwidget)
        self.frame_7.setGeometry(QtCore.QRect(30, 10, 821, 821))    
        self.frame_7.setStyleSheet("""
            background-color: transparent;
            border-radius: 20px;
            border: 2px solid #3A3A5C;
            box-shadow: 0px 0px 20px rgba(0, 0, 0, 0.5);
        """)
        self.frame_7.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_7.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_7.setObjectName("frame_7")
        
        # StackedWidget (içerik değişimi için)
        self.stackedWidget = QtWidgets.QStackedWidget(self.frame_7)
        self.stackedWidget.setGeometry(QtCore.QRect(0, 0, 821, 821))
        self.stackedWidget.setStyleSheet("background-color: white; border-radius: 20px;")
        self.stackedWidget.setObjectName("stackedWidget")
        
        # Gelecek ödemeler frame'i (sağ alt)
        self.frame_9 = QtWidgets.QFrame(self.centralwidget)
        self.frame_9.setGeometry(QtCore.QRect(890, 660, 331, 301))
        self.frame_9.setStyleSheet("""
            background-color: rgba(37, 37, 65, 0.5);
            border-radius: 20px;
            border: 2px solid #3A3A5C;
            box-shadow: 0px 0px 20px rgba(0, 0, 0, 0.5);
        """)
        self.frame_9.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_9.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_9.setObjectName("frame_9")
        
        # Gelecek ödemeler başlığı
        self.label_40 = QtWidgets.QLabel(self.frame_9)
        self.label_40.setGeometry(QtCore.QRect(85, 10, 161, 31))
        font = QtGui.QFont()
        font.setPointSize(15)
        font.setBold(True)
        font.setWeight(75)
        self.label_40.setFont(font)
        self.label_40.setStyleSheet("color: yellow; background-color: red; border-radius: 10px;")
        self.label_40.setAlignment(QtCore.Qt.AlignCenter)
        self.label_40.setObjectName("label_40")
        
        
        self.create_future_payment_frame(45, 50, "🏦", "Tonboo Trendyol", "348.475 TL")
        self.create_future_payment_frame(45, 110, "🏦", "Tonboo HB", "348.475 TL")
        self.create_future_payment_frame(45, 170, "🏦", "Iwant Trendyol", "348.475 TL")
        self.create_future_payment_frame(45, 230, "🏦", "Iwant HB", "348.475 TL")
        
        # Alt menü (butonlar)
        self.frame_14 = QtWidgets.QFrame(self.centralwidget)
        self.frame_14.setGeometry(QtCore.QRect(30, 840, 841, 111))
        self.frame_14.setStyleSheet("""
            background-color: rgba(37, 37, 65, 0.5);
            border-radius: 20px;
            border: 2px solid #3A3A5C;
            box-shadow: 0px 0px 20px rgba(0, 0, 0, 0.5);
        """)
        self.frame_14.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_14.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_14.setObjectName("frame_14")
        
        # Alt menü butonları
        self.create_bottom_menu_buttons()
        
        # Sayfaları oluştur
        self.create_pages()
            
        # Katman sıralaması
        self.label.raise_()
        self.frame.raise_()
        self.frame_7.raise_()
        self.frame_9.raise_()
        self.frame_14.raise_()
        
        MainWindow.setCentralWidget(self.centralwidget)

        self.PAGE_CASH = 0
        self.PAGE_TONBOO_ZIRAAT = 1
        self.PAGE_TONBOO_GARANTI = 2
        self.PAGE_IWANT_ZIRAAT = 3
        self.PAGE_IWANT_GARANTI = 4
        self.PAGE_VOLKAN = 5
        self.PAGE_STOCK = 6
        self.PAGE_ORDERS = 7
        self.PAGE_INCOME = 8
        self.PAGE_EXPENSE = 9
        self.PAGE_PASSWORDS = 10
        self.PAGE_REFERENCES = 11
        self.PAGE_IMPORTS = 12
        
        # Yetki haritasını ekleyin (setupUi içinde)
        self.page_permissions = {
            'admin': list(range(13)),  # Tüm sayfalar
            'personnel': [0,1,2,3,4,5,6,7,11,12],  # Stok, sipariş, referans, ithalat
            'observer': [0,1,2,3,4,5,6,7,11,12]    # Aynı sayfalar salt okunur
        }
        
        # Bağlantıları kur
        self.setup_connections()
        
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    # setupUi fonksiyonuna bu kısmı ekleyin
    def setup_permissions(self, role):
        """Rol bazlı erişim kontrolleri"""
        from authorization_page import AuthorizationManager
        self.auth = AuthorizationManager()
        
        # Tüm sayfaları devre dışı bırak
        for i in range(self.stackedWidget.count()):
            self.stackedWidget.widget(i).setEnabled(False)
        
        # İzin verilen sayfaları aktif et
        page_mapping = {

            0: 'CASH',
            1: 'Tonboo Ziraat', 
            2: 'Tonboo Garanti',
            3: 'Iwant Ziraat',
            4: 'Iwant Garanti',
            5: 'Volkan Amount',
            6: 'stok',    
            7: 'orders',   
            8: 'income',   # Gelir (sadece admin)
            9: 'expense',  # Gider (sadece admin)
            11: 'passwords', # Şifreler (sadece admin)
            12: 'references', # Referanslar
            13: 'imports'   # İthalat
        }
        
        for page_idx, page_name in page_mapping.items():
            if page_idx < self.stackedWidget.count():
                if self.auth.check_permission(role, page_name):
                    self.stackedWidget.widget(page_idx).setEnabled(True)
                    
                    # Gözlemci modu için salt okunur ayarla
                    if role == 'observer':
                        self.set_readonly_mode(self.stackedWidget.widget(page_idx))

    def set_readonly_mode(self, widget):
        """Widget'ı salt okunur moda al"""
        for child in widget.findChildren(QtWidgets.QLineEdit):
            child.setReadOnly(True)
        for child in widget.findChildren(QtWidgets.QComboBox):
            child.setEnabled(False)
        for child in widget.findChildren(QtWidgets.QPushButton):
            if not child.objectName().startswith('nav_'):  # Gezinme butonları hariç
                child.setEnabled(False)

    def set_user_role(self, role):
        """Kullanıcı rolünü ayarlar ve yetkileri günceller"""
        self.current_user_role = role.lower()
        self.update_permissions()
        
    def update_permissions(self):
        """Kullanıcı rolüne göre arayüzü günceller"""
        if self.current_user_role == 'admin':
            self.enable_all_features()
        elif self.current_user_role == 'personnel':
            self.set_personnel_permissions()
        elif self.current_user_role == 'observer':
            self.set_observer_permissions()
            
    def enable_all_features(self):
        """Tüm özellikleri etkinleştir (yönetici)"""
        pass
        
    def set_personnel_permissions(self):
        """Personel yetkilerini ayarla"""
        # Gelir/Gider sayfalarını devre dışı bırak
        self.disable_page(8)  # Gelir
        self.disable_page(9)  # Gider
        
    def set_observer_permissions(self):
        """Gözlemci yetkilerini ayarla"""
        self.set_personnel_permissions()
        
        # Tüm düzenleme butonlarını devre dışı bırak
        for i in range(self.stackedWidget.count()):
            page = self.stackedWidget.widget(i)
            self.set_readonly_mode(page)
            
    def disable_page(self, index):
        """Belirtilen sayfayı devre dışı bırak"""
        # Sayfaya erişimi engelle
        pass
        
    def set_readonly_mode(self, widget):
        """Widget'ı salt okunur moda al"""
        # Tüm QLineEdit, QComboBox, QPushButton'ları kontrol et
        for child in widget.findChildren(QtWidgets.QLineEdit):
            child.setReadOnly(True)
        for child in widget.findChildren(QtWidgets.QComboBox):
            child.setEnabled(False)
        for child in widget.findChildren(QtWidgets.QPushButton):
            if child.objectName() not in ['navigationButton']:  # Gezinme butonlarını hariç tut
                child.setEnabled(False)    

    def update_total_balance(self):
        """Calculates and updates the total balance of all accounts"""
        total = 0.0
        
        # Get balances from all accounts
        if hasattr(self, 'cash_transactions_page'):
            total += float(self.cash_amount_label.text().split()[0]) if hasattr(self, 'cash_amount_label') else 0
        
        if hasattr(self, 'tonboo_ziraat_page'):
            total += float(self.tonboo_ziraat_amount_label.text().split()[0]) if hasattr(self, 'tonboo_ziraat_amount_label') else 0
        
        if hasattr(self, 'tonboo_garanti_page'):
            total += float(self.tonboo_garanti_amount_label.text().split()[0]) if hasattr(self, 'tonboo_garanti_amount_label') else 0
        
        if hasattr(self, 'iwant_ziraat_page'):
            total += float(self.iwant_ziraat_amount_label.text().split()[0]) if hasattr(self, 'iwant_ziraat_amount_label') else 0
        
        if hasattr(self, 'iwant_garanti_page'):
            total += float(self.iwant_garanti_amount_label.text().split()[0]) if hasattr(self, 'iwant_garanti_amount_label') else 0
        
        if hasattr(self, 'volkan_amount_page'):
            total += float(self.volkan_amount_amount_label.text().split()[0]) if hasattr(self, 'volkan_amount_amount_label') else 0
        
        # Update the label
        self.label_2.setText(f"{total:.2f} TL")

    def on_account_frame_click(self, account_name):
        """Hesap kartlarına tıklandığında çalışır"""
        account_mapping = {
            "CASH": 0,
            "Tonboo Ziraat": 1,
            "Tonboo Garanti": 2,
            "Iwant Ziraat": 3,
            "Iwant Garanti": 4,
            "Volkan Amount": 5
        }
        
        if account_name in account_mapping:
            self.stackedWidget.setCurrentIndex(account_mapping[account_name])
            print(f"{account_name} hesabı seçildi")    

    def create_future_payment_frame(self, x, y, icon, title, amount):
        """Gelecek ödemeler için frame oluşturur"""
        frame = QtWidgets.QFrame(self.frame_9)  # frame_9, gelecek ödemelerin ana frame'i
        frame.setGeometry(QtCore.QRect(x, y, 241, 51))
        frame.setStyleSheet("""
            background-color: transparent;
            border: none;
        """)
        frame.setFrameShape(QtWidgets.QFrame.NoFrame)
        frame.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))

    def create_account_frame(self, x, y, icon, title, amount):
        """Hesap frame'i oluşturur - SAYDAM ARKA PLAN - Ortalanmış"""
        frame = QtWidgets.QFrame(self.frame)
        frame.setGeometry(QtCore.QRect(x, y, 261, 71))
        frame.setStyleSheet("background-color: transparent; border: none;")
        frame.setFrameShape(QtWidgets.QFrame.NoFrame)
        frame.setFrameShadow(QtWidgets.QFrame.Plain)
        frame.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        
        # İkon
        icon_label = QtWidgets.QLabel(frame)
        icon_label.setGeometry(QtCore.QRect(20, 0, 91, 71))
        font = QtGui.QFont()
        font.setPointSize(31)
        font.setBold(True)
        font.setWeight(75)
        icon_label.setFont(font)
        icon_label.setStyleSheet("background-color: transparent; color: white;")
        icon_label.setAlignment(QtCore.Qt.AlignCenter)
        icon_label.setText(icon)
        
        # Başlık
        title_label = QtWidgets.QLabel(frame)
        title_label.setGeometry(QtCore.QRect(110, 0, 141, 41))
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        title_label.setFont(font)
        title_label.setStyleSheet("background-color: transparent; color: white;")
        title_label.setAlignment(QtCore.Qt.AlignCenter)
        title_label.setText(title)
        
        # Miktar
        amount_label = QtWidgets.QLabel(frame)
        amount_label.setGeometry(QtCore.QRect(110, 30, 141, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        amount_label.setFont(font)
        amount_label.setStyleSheet("background-color: transparent; color: yellow;")
        amount_label.setAlignment(QtCore.Qt.AlignCenter)
        amount_label.setText(amount)
        
        # Frame'e referanslar ekle (güncelleme için)
        frame.title_label = title_label
        frame.amount_label = amount_label
        
        # Frame'i tıklanabilir yap
        frame.mousePressEvent = lambda event, t=title: self.on_account_frame_click(t)
        
        # CASH frame'i için özel referans sakla
        if title == "CASH":
            self.cash_amount_label = amount_label
        
        # Tonboo Ziraat frame'i için özel referans sakla
        if title == "Tonboo Ziraat":
            self.tonboo_ziraat_amount_label = amount_label
        
        # Tonboo Garanti frame'i için özel referans sakla (EKLENDİ)
        if title == "Tonboo Garanti":
            self.tonboo_garanti_amount_label = amount_label

        # Iwant Ziraat frame'i için özel referans sakla (EKLENDİ)
        if title == "Iwant Ziraat":
            self.iwant_ziraat_amount_label = amount_label    

        # Iwant Garanti frame'i için özel referans sakla
        if title == "Iwant Garanti":
            self.iwant_garanti_amount_label = amount_label

        # Volkan Amount frame'i için özel referans sakla
        if title == "Volkan Amount":
            self.volkan_amount_amount_label = amount_label
        
        return frame

    def create_bottom_menu_buttons(self):
        """Alt menü butonlarını oluşturur"""
        buttons_data = [
            (10, "📦", "库存追踪"),
            (120, "🚚", "订单"), 
            (240, "📈", "收入"),
            (350, "📉", "花费"),
            (460, "🗃️", "文件"),
            (570, "🔐", "密码"),
            (670, "📱", "参考资料"),
            (760, "🚢", "进口")
        ]
        
        for x, icon, label_text in buttons_data:
            # Buton - border kaldırıldı
            button = QtWidgets.QPushButton(self.frame_14)
            button.setGeometry(QtCore.QRect(x, 5, 71, 71))
            font = QtGui.QFont()
            font.setPointSize(35)
            button.setFont(font)
            button.setStyleSheet("background-color: transparent; color: white; border: none;")
            button.setText(icon)
            button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            
            # Label
            label = QtWidgets.QLabel(self.frame_14)
            label.setGeometry(QtCore.QRect(x, 90, 71, 16))
            font = QtGui.QFont()
            font.setPointSize(10)
            font.setBold(True)
            font.setWeight(75)
            label.setFont(font)
            label.setStyleSheet("color:white; background-color: transparent; border: none;")
            label.setAlignment(QtCore.Qt.AlignCenter)
            label.setText(label_text)
            
            # Butona tıklama olayı ekle
            button.clicked.connect(lambda checked, t=label_text: self.on_bottom_menu_click(t))

    def create_pages(self):
        """StackedWidget sayfalarını oluşturur"""
        page_names = [
            "CASH",
            "Tonboo Ziraat",
            "Tonboo Garanti",
            "Iwant Ziraat",
            "Iwant Garanti",
            "Volkan Amount",
            "库存追踪 (Stok)",
            "订单 (Siparişler)",
            "收入 (Gelir)",
            "花费 (Gider)",
            "文件 (Dosyalar)",
            "密码 (Şifreler)",
            "参考资料 (Referans)",
            "进口 (İthalat)"
        ]
        
        for name in page_names:
            if name == "CASH":
                self.cash_transactions_page = CashTransactionsPageWidget()
                self.cash_transactions_page.back_to_main.connect(lambda: self.stackedWidget.setCurrentIndex(0))
                self.cash_transactions_page.balance_updated.connect(self.update_cash_balance)
                self.stackedWidget.addWidget(self.cash_transactions_page) 
                
            elif name == "Iwant Ziraat": 
                self.iwant_ziraat_page = IwantZiraatTransactionsPageWidget()
                self.iwant_ziraat_page.balance_updated.connect(self.update_iwant_ziraat_balance)
                self.stackedWidget.addWidget(self.iwant_ziraat_page)    
            elif name == "Tonboo Ziraat":
                self.tonboo_ziraat_page = TonbooZiraatTransactionsPageWidget()
                self.tonboo_ziraat_page.balance_updated.connect(self.update_tonboo_ziraat_balance)
                self.stackedWidget.addWidget(self.tonboo_ziraat_page)
            elif name == "Tonboo Garanti": 
                self.tonboo_garanti_page = TonbooGarantiTransactionsPageWidget()
                self.tonboo_garanti_page.balance_updated.connect(self.update_tonboo_garanti_balance)
                self.stackedWidget.addWidget(self.tonboo_garanti_page)
            elif name == "Iwant Garanti":
                self.iwant_garanti_page = IwantGarantiTransactionsPageWidget()
                self.iwant_garanti_page.balance_updated.connect(self.update_iwant_garanti_balance)
                self.stackedWidget.addWidget(self.iwant_garanti_page)
            elif name == "Volkan Amount":
                self.volkan_amount_page = VolkanAmountPageWidget()
                self.volkan_amount_page.balance_updated.connect(self.update_volkan_amount_balance)
                self.stackedWidget.addWidget(self.volkan_amount_page)
            elif name == "收入 (Gelir)":
                self.income_page = IncomePageWidget()
                if hasattr(self.income_page, 'transaction_added'):
                    self.income_page.transaction_added.connect(self.on_any_account_transaction_added)
                self.stackedWidget.addWidget(self.income_page)
            elif name == "花费 (Gider)":
                self.expense_page = ExpensePageWidget()
                if hasattr(self.expense_page, 'transaction_added'):
                    self.expense_page.transaction_added.connect(self.on_any_account_transaction_added)
                self.stackedWidget.addWidget(self.expense_page)
            elif name == "库存追踪 (Stok)":
                # Kullanıcı rolünü geçerek StockPage oluştur
                stock_page = StockPage(user_role=self.current_user_role)
                self.stackedWidget.addWidget(stock_page)
            elif name == "参考资料 (Referans)":
                reference_page = ReferencePage()
                self.stackedWidget.addWidget(reference_page)
            elif name == "订单 (Siparişler)":
                daily_orders_page = DailyOrdersWidget()
                self.stackedWidget.addWidget(daily_orders_page)
            elif name == "密码 (Şifreler)":
                paswords_page = PasswordManager()
                self.stackedWidget.addWidget(paswords_page)   
            elif name == "进口 (İthalat)":
                imports_page = ImportsPage()
                self.stackedWidget.addWidget(imports_page)     
            else:
                page = QWidget()
                layout = QVBoxLayout(page)
                
                title_label = QLabel(f"{name}")
                title_font = QtGui.QFont()
                title_font.setPointSize(24)
                title_font.setBold(True)
                title_label.setFont(title_font)
                title_label.setAlignment(QtCore.Qt.AlignCenter)
                title_label.setStyleSheet("color: #2c3e50; margin: 20px;")
                
                content_label = QLabel(f"{name} sayfası içeriği burada görüntülenecek.\n\nBu alan dinamik olarak güncellenebilir.")
                content_font = QtGui.QFont()
                content_font.setPointSize(14)
                content_label.setFont(content_font)
                content_label.setAlignment(QtCore.Qt.AlignCenter)
                content_label.setStyleSheet("color: #34495e; margin: 20px;")
                content_label.setWordWrap(True)
                
                layout.addWidget(title_label)
                layout.addWidget(content_label)
                layout.addStretch()
                
                self.stackedWidget.addWidget(page)
    
    def update_cash_balance(self, balance):
        """Updates the CASH account balance display"""
        if hasattr(self, 'cash_amount_label'):
            self.cash_amount_label.setText(f"{balance:.2f} TL")
        self.update_total_balance()
    
    def update_tonboo_ziraat_balance(self, balance):
        """Tonboo Ziraat hesabının bakiyesini günceller"""
        if hasattr(self, 'tonboo_ziraat_amount_label'):
            self.tonboo_ziraat_amount_label.setText(f"{balance:.2f} TL")
        self.update_total_balance()

    def update_tonboo_garanti_balance(self, balance): # EKLENDİ
        """Tonboo Garanti hesabının bakiyesini günceller"""
        if hasattr(self, 'tonboo_garanti_amount_label'):
            self.tonboo_garanti_amount_label.setText(f"{balance:.2f} TL")
        self.update_total_balance()

    def update_iwant_ziraat_balance(self, balance):
        """Iwant Ziraat hesabının bakiyesini günceller"""
        if hasattr(self, 'iwant_ziraat_amount_label'):
            self.iwant_ziraat_amount_label.setText(f"{balance:.2f} TL")        
        self.update_total_balance()

    def update_iwant_garanti_balance(self, balance):
        """Iwant Garanti hesabının bakiyesini günceller"""
        if hasattr(self, 'iwant_garanti_amount_label'):
            self.iwant_garanti_amount_label.setText(f"{balance:.2f} TL")
        self.update_total_balance()

    def update_volkan_amount_balance(self, balance):
        """Volkan Amount hesabının bakiyesini günceller"""
        if hasattr(self, 'volkan_amount_amount_label'):
            self.volkan_amount_amount_label.setText(f"{balance:.2f} TL")
        self.update_total_balance()

    def setup_connections(self):
        # Cash sayfasını al ve bağlantıları kur
        if hasattr(self, 'cash_transactions_page') and isinstance(self.cash_transactions_page, CashTransactionsPageWidget):
            self.cash_transactions_page.load_cash_transactions()
            self.cash_transactions_page.balance_updated.connect(self.update_cash_balance)
            self.cash_transactions_page.back_to_main.connect(lambda: self.stackedWidget.setCurrentIndex(0))
        
        # Tonboo Ziraat sayfasını al ve bağlantıları kur
        if hasattr(self, 'tonboo_ziraat_page') and isinstance(self.tonboo_ziraat_page, TonbooZiraatTransactionsPageWidget):
            self.tonboo_ziraat_page.balance_updated.connect(self.update_tonboo_ziraat_balance)
            # Sayfa yüklendiğinde işlemleri yükle
            self.tonboo_ziraat_page.load_tonboo_ziraat_transactions() 

        # Tonboo Garanti sayfasını al ve bağlantıları kur (EKLENDİ)
        if hasattr(self, 'tonboo_garanti_page') and isinstance(self.tonboo_garanti_page, TonbooGarantiTransactionsPageWidget):
            self.tonboo_garanti_page.balance_updated.connect(self.update_tonboo_garanti_balance)
            # Sayfa yüklendiğinde işlemleri yükle
            self.tonboo_garanti_page.load_tonboo_garanti_transactions() 

        if hasattr(self, 'iwant_ziraat_page') and isinstance(self.iwant_ziraat_page, IwantZiraatTransactionsPageWidget):
            self.iwant_ziraat_page.balance_updated.connect(self.update_iwant_ziraat_balance)
            # Sayfa yüklendiğinde işlemleri yükle
            self.iwant_ziraat_page.load_iwant_ziraat_transactions() 

        if hasattr(self, 'iwant_garanti_page') and isinstance(self.iwant_garanti_page, IwantGarantiTransactionsPageWidget):
            self.iwant_garanti_page.balance_updated.connect(self.update_iwant_garanti_balance)
            # Sayfa yüklendiğinde işlemleri yükle
            self.iwant_garanti_page.load_iwant_garanti_transactions()

        if hasattr(self, 'volkan_amount_page') and isinstance(self.volkan_amount_page, VolkanAmountPageWidget):
            self.volkan_amount_page.balance_updated.connect(self.update_volkan_amount_balance)
            # Sayfa yüklendiğinde işlemleri yükle
            self.volkan_amount_page.load_volkan_amount_transactions()

        # Initialize total balance
        self.update_total_balance()

    def on_cash_transaction_added(self):
        """Yeni CASH işlemi eklendiğinde çağrılır - Genelleştirilmiş on_any_account_transaction_added yerine geçebilir"""
        if hasattr(self, 'cash_transactions_page') and isinstance(self.cash_transactions_page, CashTransactionsPageWidget):
            self.cash_transactions_page.recalculate_balance()

    def on_any_account_transaction_added(self, account_name): 
        """Herhangi bir hesaba işlem eklendiğinde çağrılır ve ilgili hesabı günceller."""
        print(f"İşlem eklendi: {account_name} hesabı güncelleniyor.")
        if account_name == "CASH" and hasattr(self, 'cash_transactions_page'):
            self.cash_transactions_page.load_cash_transactions()
        elif account_name == "Tonboo Ziraat" and hasattr(self, 'tonboo_ziraat_page'):
            self.tonboo_ziraat_page.load_tonboo_ziraat_transactions()
        elif account_name == "Tonboo Garanti" and hasattr(self, 'tonboo_garanti_page'):
            self.tonboo_garanti_page.load_tonboo_garanti_transactions()
        elif account_name == "Iwant Ziraat" and hasattr(self, 'iwant_ziraat_page'): 
            self.iwant_ziraat_page.load_iwant_ziraat_transactions()    
        elif account_name == "Iwant Garanti" and hasattr(self, 'iwant_garanti_page'):
            self.iwant_garanti_page.load_iwant_garanti_transactions()
        elif account_name == "Volkan Amount" and hasattr(self, 'volkan_amount_page'):
            self.volkan_amount_page.load_volkan_amount_transactions()

    def on_account_frame_click(self, account_name):
        """Hesap frame'ine tıklandığında çalışır"""
        account_mapping = {
            "CASH": 0,
            "Tonboo Ziraat": 1,
            "Tonboo Garanti": 2,
            "Iwant Ziraat": 3,
            "Iwant Garanti": 4,
            "Volkan Amount": 5
        }
        
        if account_name in account_mapping:
            self.stackedWidget.setCurrentIndex(account_mapping[account_name])
            print(f"{account_name} hesabı seçildi")

    def on_future_payment_click(self, payment_name):
        """Gelecek ödeme kartına tıklandığında çalışır"""
        print(f"{payment_name} gelecek ödemesi seçildi")

    def on_bottom_menu_click(self, menu_name):
        """Alt menü butonuna tıklandığında çalışır"""
        menu_mapping = {
            "库存追踪":6,
            "订单": 7,
            "收入": 8,
            "花费": 9,
            "文件": 10,
            "密码": 11,
            "参考资料": 12,
            "进口": 13
        }
        
        if menu_name in menu_mapping:
            index = menu_mapping[menu_name]
            if isinstance(index, list):
                # İlk stok sayfasını göster (gerekirse seçim menüsü eklenebilir)
                self.stackedWidget.setCurrentIndex(index[0])
            else:
                self.stackedWidget.setCurrentIndex(index)
            print(f"{menu_name} menüsü seçildi")

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Finansal Yönetim Sistemi"))
        self.label_2.setText(_translate("MainWindow", "0.00 TL"))
        self.label_4.setText(_translate("MainWindow", "资金"))
        self.label_40.setText(_translate("MainWindow", "💰未来付款"))

        


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())