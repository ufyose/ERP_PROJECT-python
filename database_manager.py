# GÜNCELLENMİŞ database_manager.py (income + expense + daily_orders için)
from supabase_client import supabase
from datetime import datetime
import logging
import bcrypt

class DatabaseManager:
    def __init__(self):
        self.supabase = supabase
        self.table_name = "transactions"
        self.daily_orders_table = "daily_orders"
        self.stock_table = "stock_table"
        self.contacts_table = "contacts"
        self.passwords_table = "passwords"
        self.users_table = "users"
        self.version_control_table = "version_control"
        
        self.logger = logging.getLogger(__name__)

    def _handle_error(self, operation, e):
        """Hataları merkezi olarak yönet"""
        error_msg = f"{operation} işlemi sırasında hata oluştu: {str(e)}"
        self.logger.error(error_msg, exc_info=True)
        raise Exception(error_msg)  # Hata yukarıya fırlatılıyor

    def _validate_data(self, data, required_fields):
        """Veri doğrulama"""
        for field in required_fields:
            if field not in data or not data[field]:
                raise ValueError(f"{field} alanı boş olamaz")
        return True

    def add_income(self, **kwargs):
        return self._add_transaction(type="income", **kwargs)

    def add_expense(self, **kwargs):
        return self._add_transaction(type="expense", **kwargs)

    def _add_transaction(self, type, tarih, aciklama, para_birimi, miktar, usd_kuru=None, tl_karsiligi=None, odeme_turu="Nakit"):
        try:
            # Veri doğrulama
            self._validate_data({
                'tarih': tarih,
                'aciklama': aciklama,
                'para_birimi': para_birimi,
                'miktar': miktar
            }, ['tarih', 'aciklama', 'para_birimi', 'miktar'])

            if isinstance(tarih, str):
                try:
                    tarih = datetime.strptime(tarih, "%d.%m.%Y").date()
                except ValueError:
                    tarih = datetime.strptime(tarih, "%Y-%m-%d").date()

            if tl_karsiligi is None:
                if para_birimi == "TL":
                    tl_karsiligi = miktar
                elif para_birimi == "USD" and usd_kuru:
                    tl_karsiligi = miktar * usd_kuru
                elif para_birimi == "EUR" and usd_kuru:
                    tl_karsiligi = miktar * 1.1 * usd_kuru
                else:
                    tl_karsiligi = miktar

            data = {
                "type": type,
                "tarih": tarih.isoformat(),
                "aciklama": aciklama,
                "para_birimi": para_birimi,
                "miktar": float(miktar),
                "odeme_turu": odeme_turu,
                "usd_kuru": float(usd_kuru) if usd_kuru else None,
                "tl_karsiligi": float(tl_karsiligi)
            }

            result = self.supabase.table(self.table_name).insert(data).execute()
            
            if not result.data:
                raise Exception("Veritabanına ekleme başarısız")
                
            return result.data[0]

        except Exception as e:
            self._handle_error("Transaction ekleme", e)

    def get_all_incomes(self):
        return self._get_all_by_type("income")

    def get_all_expenses(self):
        return self._get_all_by_type("expense")

    def _get_all_by_type(self, type):
        try:
            result = self.supabase.table(self.table_name)\
                .select("*")\
                .eq("type", type)\
                .eq("aktif", True)\
                .order("tarih", desc=True)\
                .execute()
            return result.data if result.data else []
        except Exception as e:
            self._handle_error(f"{type} verileri getirme", e)
            return []

    def search_incomes(self, search_term):
        return self._search_by_type("income", search_term)

    def search_expenses(self, search_term):
        return self._search_by_type("expense", search_term)

    def _search_by_type(self, type, term):
        try:
            result = self.supabase.table(self.table_name)\
                .select("*")\
                .eq("type", type)\
                .eq("aktif", True)\
                .ilike("aciklama", f"%{term}%")\
                .order("tarih", desc=True)\
                .execute()
            return result.data if result.data else []
        except Exception as e:
            self._handle_error(f"{type} arama", e)
            return []


    def delete_income(self, income_id, soft=True):
        return self.delete_transaction(income_id, soft=soft)

    def delete_expense(self, expense_id, soft=True):
        return self.delete_transaction(expense_id, soft=soft)

    def delete_transaction(self, transaction_id, soft=True):
        try:
            if not transaction_id:
                raise ValueError("Geçersiz transaction ID")

            if soft:
                # Soft delete
                return self.update_transaction(transaction_id, aktif=False)
            else:
                # Gerçekten sil
                result = self.supabase.table(self.table_name).delete().eq("id", transaction_id).execute()
                return True if result.data else False

        except Exception as e:
            self._handle_error("Transaction silme", e)
            return False



    def update_income(self, income_id, **kwargs):
        return self.update_transaction(income_id, **kwargs)

    def update_expense(self, expense_id, **kwargs):
        return self.update_transaction(expense_id, **kwargs)

    def update_transaction(self, transaction_id, **kwargs):
        try:
            if not transaction_id:
                raise ValueError("Geçersiz transaction ID")
            
            update_data = {k: v for k, v in kwargs.items() if v is not None}

            if 'tarih' in update_data and isinstance(update_data['tarih'], str):
                try:
                    update_data['tarih'] = datetime.strptime(update_data['tarih'], "%d.%m.%Y").date().isoformat()
                except ValueError:
                    update_data['tarih'] = datetime.strptime(update_data['tarih'], "%Y-%m-%d").date().isoformat()

            # Güncelleme işlemi yapılır
            result = self.supabase.table(self.table_name).update(update_data).eq("id", transaction_id).execute()

            # Supabase bazen .data boş döner ama hata vermez
            return True

        except Exception as e:
            self._handle_error("Transaction güncelleme", e)
            return None
    def get_expenses_by_date_range(self, start_date, end_date):
        """Belirli tarih aralığındaki giderleri getirir (Supabase uyumlu)"""
        try:
            result = self.supabase.table(self.table_name)\
                .select("*")\
                .eq("type", "expense")\
                .eq("aktif", True)\
                .gte("tarih", start_date)\
                .lte("tarih", end_date)\
                .order("tarih", desc=True)\
                .execute()
            return result.data if result.data else []
        except Exception as e:
            self._handle_error("Giderleri tarih aralığında getirme", e)
            return []    

    def get_incomes_by_date_range(self, start_date, end_date):
        """Belirli tarih aralığındaki gelirleri getirir (Supabase uyumlu)"""
        try:
            result = self.supabase.table(self.table_name)\
                .select("*")\
                .eq("type", "income")\
                .eq("aktif", True)\
                .gte("tarih", start_date)\
                .lte("tarih", end_date)\
                .order("tarih", desc=True)\
                .execute()
            return result.data if result.data else []
        except Exception as e:
            self._handle_error("Gelirleri tarih aralığında getirme", e)
            return [] 
    # ------------------ STOCK TABLE FONKSİYONLARI ------------------ #

    def add_stock_item(self, urun_kodu, urun_adi, miktar, birim_fiyat, gercek_stok=None):
        try:
            # Eğer gerçek stok belirtilmemişse, normal stokla aynı yap
            if gercek_stok is None:
                gercek_stok = miktar
                
            data = {
                "urun_kodu": str(urun_kodu),
                "urun_adi": str(urun_adi),
                "miktar": int(miktar),
                "gercek_stok": int(gercek_stok),  # Zorunlu alan
                "birim_fiyat": float(birim_fiyat)
            }
            
            result = self.supabase.table(self.stock_table).insert(data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            self._handle_error("Stok ekleme", e)
            return None

    def get_all_stock_items(self):
        try:
            result = self.supabase.table(self.stock_table).select("*").order("urun_adi").execute()
            return result.data if result.data else []
        except Exception as e:
            self._handle_error("Stok verisi getirme", e)
            return []
    def get_stock_item_by_code(self, product_code):
        """Ürün koduna göre stok item'ını getirir"""
        try:
            result = self.supabase.table(self.stock_table)\
                .select("*")\
                .eq("urun_kodu", product_code)\
                .execute()
            return result.data[0] if result.data else None
        except Exception as e:
            self._handle_error("Stok item'ı getirme", e)
            return None    
        
    def update_stock_quantity(self, product_code, new_quantity, new_real_quantity=None):
        """Verilen ürün koduna ait stok miktarını günceller."""
        try:
            if new_quantity < 0:  # Stok miktarının negatif olmamasını sağla
                new_quantity = 0
                
            update_data = {"miktar": new_quantity}
            
            if new_real_quantity is not None:
                if new_real_quantity < 0:
                    new_real_quantity = 0
                update_data["gercek_stok"] = new_real_quantity
                
            result = self.supabase.table(self.stock_table)\
                .update(update_data)\
                .eq("urun_kodu", product_code)\
                .execute()
                
            return True if result.data else False
        except Exception as e:
            self._handle_error(f"Stok miktarı güncellenirken hata oluştu: {e}", e)
            return False    

    def get_stock_quantity(self, product_code):
        """Verilen ürün koduna ait stok miktarını döndürür."""
        try:
            result = self.supabase.table(self.stock_table).select("miktar").eq("urun_kodu", product_code).execute()
            if result.data:
                return result.data[0]['miktar']
            return None
        except Exception as e:
            self._handle_error(f"Stok miktarı sorgulanırken hata oluştu: {e}", e)
            return None

    

    def update_stock_item(self, item_id, **kwargs):
        try:
            if not item_id:
                raise ValueError("Geçersiz stok ID")
                
            update_data = {k: v for k, v in kwargs.items() if v is not None}
            
            if 'miktar' in update_data and update_data['miktar'] <= 0:
                raise ValueError("Miktar pozitif olmalıdır")
                
            if 'birim_fiyat' in update_data and update_data['birim_fiyat'] <= 0:
                raise ValueError("Birim fiyat pozitif olmalıdır")

            result = self.supabase.table(self.stock_table).update(update_data).eq("id", item_id).execute()
            
            if not result.data:
                raise Exception("Stok güncelleme başarısız")
                
            return result.data[0]
        except Exception as e:
            self._handle_error("Stok güncelleme", e)
            return None

    def delete_stock_item(self, item_id):
        try:
            if not item_id:
                raise ValueError("Geçersiz stok ID")
                
            result = self.supabase.table(self.stock_table).delete().eq("id", item_id).execute()
            return True if result.data else False
        except Exception as e:
            self._handle_error("Stok silme", e)
            return False


    # ------------------ DAILY ORDERS TABLE FONKSİYONLARI ------------------ #

    def add_daily_order(self, product_code, customer_name, product_name, quantity, unit_price, is_real_order=True):
        try:
            # Veri doğrulama
            self._validate_data({
                'product_code': product_code,
                'customer_name': customer_name,
                'product_name': product_name,
                'quantity': quantity,
                'unit_price': unit_price
            }, ['product_code', 'customer_name', 'product_name'])
            
            if quantity <= 0 or unit_price <= 0:
                raise ValueError("Miktar ve birim fiyat pozitif olmalıdır")

            # Stok kontrolü yap
            stock_item = self.get_stock_item_by_code(product_code)
            if stock_item is None:
                raise ValueError("Ürün stokta bulunamadı")
                
            stock_quantity = stock_item['miktar']
            real_stock_quantity = stock_item.get('gercek_stok', stock_quantity)
            
            # Stok güncelleme işlemi
            new_stock = stock_quantity - quantity
            if new_stock < 0:
                raise ValueError(f"Stokta yeterli ürün yok! Mevcut stok: {stock_quantity}")
                
            # Gerçek stok güncelleme
            if is_real_order:
                new_real_stock = real_stock_quantity - quantity
                if new_real_stock < 0:
                    new_real_stock = 0
            else:
                new_real_stock = real_stock_quantity
                
            # Stokları güncelle
            self.update_stock_quantity(product_code, new_stock, new_real_stock)

            order_date = datetime.now().date()
            total_amount = quantity * unit_price
            
            data = {
                "product_code": str(product_code),
                "customer_name": str(customer_name),
                "product_name": str(product_name),
                "quantity": int(quantity),
                "unit_price": float(unit_price),
                "total_amount": float(total_amount),
                "order_date": order_date.isoformat(),
                "is_real_order": is_real_order
            }
            
            result = self.supabase.table(self.daily_orders_table).insert(data).execute()
            
            if not result.data:
                raise Exception("Sipariş ekleme başarısız")
                
            return result.data[0]
        except Exception as e:
            self._handle_error("Günlük sipariş ekleme", e)
            return None

    
    def get_all_daily_orders(self, order_date=None):
        try:
            query = self.supabase.table(self.daily_orders_table).select("*")
            
            if order_date:
                if isinstance(order_date, str):
                    try:
                        order_date = datetime.strptime(order_date, "%d.%m.%Y").date()
                    except ValueError:
                        order_date = datetime.strptime(order_date, "%Y-%m-%d").date()
                query = query.eq("order_date", order_date.isoformat())
            
            result = query.execute()
            return result.data if result.data else []
            
        except Exception as e:
            self._handle_error("Günlük sipariş verisi getirme", e)
            return []

    def get_today_orders(self):
        try:
            today = datetime.now().date().isoformat()
            result = self.supabase.table(self.daily_orders_table).select("*")\
                    .eq("order_date", today).execute()
            return result.data if result.data else []
        except Exception as e:
            self._handle_error("Bugünkü siparişleri getirme", e)
            return []

    def update_daily_order(self, order_id, **kwargs):
        try:
            if not order_id:
                raise ValueError("Geçersiz sipariş ID")
                
            update_data = {k: v for k, v in kwargs.items() if v is not None}
            
            # Tarih formatını kontrol et
            if 'order_date' in update_data and isinstance(update_data['order_date'], str):
                try:
                    update_data['order_date'] = datetime.strptime(update_data['order_date'], "%d.%m.%Y").date().isoformat()
                except ValueError:
                    update_data['order_date'] = datetime.strptime(update_data['order_date'], "%Y-%m-%d").date().isoformat()
            
            # Eğer quantity veya unit_price güncellendiyse total_amount'u hesapla
            if 'quantity' in update_data or 'unit_price' in update_data:
                # Mevcut veriyi al
                current_result = self.supabase.table(self.daily_orders_table).select("quantity, unit_price").eq("id", order_id).execute()
                if current_result.data:
                    current_data = current_result.data[0]
                    quantity = update_data.get('quantity', current_data['quantity'])
                    unit_price = update_data.get('unit_price', current_data['unit_price'])
                    update_data['total_amount'] = float(quantity) * float(unit_price)
            
            result = self.supabase.table(self.daily_orders_table).update(update_data).eq("id", order_id).execute()
            
            if not result.data:
                raise Exception("Sipariş güncelleme başarısız")
                
            return result.data[0]
        except Exception as e:
            self._handle_error("Günlük sipariş güncelleme", e)
            return None

    def delete_daily_order(self, order_id):
        try:
            if not order_id:
                raise ValueError("Geçersiz sipariş ID")
                
            result = self.supabase.table(self.daily_orders_table).delete().eq("id", order_id).execute()
            return True if result.data else False
        except Exception as e:
            self._handle_error("Günlük sipariş silme", e)
            return False

    def search_daily_orders(self, search_term, order_date=None):
        try:
            query = self.supabase.table(self.daily_orders_table).select("*")
            
            if order_date:
                if isinstance(order_date, str):
                    try:
                        order_date = datetime.strptime(order_date, "%d.%m.%Y").date()
                    except ValueError:
                        order_date = datetime.strptime(order_date, "%Y-%m-%d").date()
                query = query.eq("order_date", order_date.isoformat())
            
            # Müşteri adı, ürün adı veya ürün kodunda arama yap
            result = query.or_(f"customer_name.ilike.%{search_term}%,product_name.ilike.%{search_term}%,product_code.ilike.%{search_term}%").execute()
            return result.data if result.data else []
        except Exception as e:
            self._handle_error("Günlük sipariş arama", e)
            return []

    def get_daily_orders_summary(self, order_date=None):
        try:
            orders = self.get_all_daily_orders(order_date)
            if not orders:
                return {"total_orders": 0, "total_amount": 0.0}
            
            total_orders = len(orders)
            total_amount = sum(float(order['total_amount']) for order in orders)
            
            return {
                "total_orders": total_orders,
                "total_amount": total_amount
            }
        except Exception as e:
            self._handle_error("Günlük sipariş özeti", e)
            return {"total_orders": 0, "total_amount": 0.0}

    def check_product_code_exists(self, product_code, exclude_id=None):
        try:
            if not product_code:
                return False
                
            query = self.supabase.table(self.daily_orders_table).select("id").eq("product_code", product_code)
            if exclude_id:
                query = query.neq("id", exclude_id)
            result = query.execute()
            return len(result.data) > 0
        except Exception as e:
            self._handle_error("Ürün kodu kontrol", e)
            return False

    def test_connection(self):
        try:
            result = self.supabase.table(self.table_name).select("count", count="exact").eq("type", "income").execute()
            self.logger.info(f"Veritabanı bağlantısı başarılı! Toplam gelir kaydı: {result.count}")
            return True
        except Exception as e:
            self._handle_error("Bağlantı testi", e)
            return False
        

         # ------------------ CONTACTS TABLE FONKSİYONLARI ------------------ #

    def _validate_contact_data(self, name, phone):
        """Kişi verilerini doğrula"""
        if not name or not phone:
            raise ValueError("İsim ve telefon alanları zorunludur")
        
        phone_clean = phone.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
        if not phone_clean.isdigit() or len(phone_clean) < 10:
            raise ValueError("Geçersiz telefon numarası formatı")

    def get_all_contacts(self):
        """Tüm kişileri getir"""
        try:
            # order("name") yerine order("created_at", desc=True) kullanın
            result = self.supabase.table(self.contacts_table).select("*").order("created_at", desc=True).execute()
            return [(item['id'], item['name'], item['phone'], item.get('description', '')) 
                for item in result.data] if result.data else []
        except Exception as e:
            self._handle_error("Kişileri getirme", e)
            return []

    def get_contact_by_id(self, contact_id):
        """ID'ye göre kişi getir"""
        try:
            result = self.supabase.table(self.contacts_table).select("*").eq("id", contact_id).execute()
            if result.data:
                item = result.data[0]
                return (item['id'], item['name'], item['phone'], item.get('description', ''))
            return None
        except Exception as e:
            self._handle_error("Kişi getirme", e)
            return None

    def search_contacts(self, search_term):
        """Kişi ara"""
        try:
            result = self.supabase.table(self.contacts_table).select("*").or_(
                f"name.ilike.%{search_term}%,phone.ilike.%{search_term}%,description.ilike.%{search_term}%"
            ).order("name").execute()
            
            return [(item['id'], item['name'], item['phone'], item.get('description', '')) 
                   for item in result.data] if result.data else []
        except Exception as e:
            self._handle_error("Kişi arama", e)
            return []

    def add_contact(self, name, phone, description=""):
        """Yeni kişi ekle"""
        try:
            self._validate_contact_data(name, phone)
            
            data = {
                "name": name,
                "phone": phone,
                "description": description
            }
            
            result = self.supabase.table(self.contacts_table).insert(data).execute()
            
            if not result.data:
                raise Exception("Kişi eklenemedi")
                
            return result.data[0]['id']
        except Exception as e:
            self._handle_error("Kişi ekleme", e)
            return None

    def update_contact(self, contact_id, name, phone, description=""):
        """Kişi güncelle"""
        try:
            self._validate_contact_data(name, phone)
            
            data = {
                "name": name,
                "phone": phone,
                "description": description,
                "updated_at": datetime.now().isoformat()
            }
            
            result = self.supabase.table(self.contacts_table).update(data).eq("id", contact_id).execute()
            
            if not result.data:
                raise Exception("Kişi güncellenemedi")
                
            return True
        except Exception as e:
            self._handle_error("Kişi güncelleme", e)
            return False

    def delete_contact(self, contact_id):
        """Kişi sil"""
        try:
            result = self.supabase.table(self.contacts_table).delete().eq("id", contact_id).execute()
            return len(result.data) > 0 if result.data else False
        except Exception as e:
            self._handle_error("Kişi silme", e)
            return False

    def test_connection(self):
        """Veritabanı bağlantısını test et"""
        try:
            # Contacts tablosundan örnek bir sorgu yaparak bağlantıyı test edelim
            result = self.supabase.table(self.contacts_table).select("count", count="exact").execute()
            self.logger.info(f"Veritabanı bağlantısı başarılı! Toplam kişi kaydı: {result.count}")
            return True
        except Exception as e:
            self._handle_error("Bağlantı testi", e)
            return False
        
        # ------------------ PASSWORDS TABLE FONKSİYONLARI ------------------ #

    def add_password(self, platform, username, password, description=""):
        try:
            self._validate_data({
                'platform': platform,
                'username': username,
                'password': password
            }, ['platform', 'username', 'password'])

            data = {
                "platform": platform,
                "username": username,
                "password": password,
                "description": description,
                
            }

            result = self.supabase.table(self.passwords_table).insert(data).execute()
            
            if not result.data:
                raise Exception("Şifre ekleme başarısız")
                
            return result.data[0]
        except Exception as e:
            self._handle_error("Şifre ekleme", e)
            return None

    def get_all_passwords(self):
        try:
            
            result = self.supabase.table(self.passwords_table).select("*").execute()
            return result.data if result.data else []
        except Exception as e:
            self._handle_error("Şifreleri getirme", e)
            return []

    def search_passwords(self, search_term):
        try:
            result = self.supabase.table(self.passwords_table).select("*").or_(
                f"platform.ilike.%{search_term}%,username.ilike.%{search_term}%,description.ilike.%{search_term}%"
            ).execute()
            return result.data if result.data else []
        except Exception as e:
            self._handle_error("Şifre arama", e)
            return []

    def update_password(self, password_id, platform, username, password, description=""):
        try:
            self._validate_data({
                'platform': platform,
                'username': username,
                'password': password
            }, ['platform', 'username', 'password'])

            data = {
                "platform": platform,
                "username": username,
                "password": password,
                "description": description,
                
            }

            result = self.supabase.table(self.passwords_table).update(data).eq("id", password_id).execute()
            
            if not result.data:
                raise Exception("Şifre güncelleme başarısız")
                
            return True
        except Exception as e:
            self._handle_error("Şifre güncelleme", e)
            return False

    def delete_password(self, password_id):
        try:
            result = self.supabase.table(self.passwords_table).delete().eq("id", password_id).execute()
            return len(result.data) > 0 if result.data else False
        except Exception as e:
            self._handle_error("Şifre silme", e)
            return False

    def delete_all_passwords(self):
        try:
            result = self.supabase.table(self.passwords_table).delete().neq("id", 0).execute()
            return len(result.data) > 0 if result.data else False
        except Exception as e:
            self._handle_error("Tüm şifreleri silme", e)
            return False
        
        # ------------------ İMPORTS TABLE FONKSİYONLARI ------------------ #
    
    def get_all_imports(self):
        try:
            result = self.supabase.table("imports").select("*").execute()
            return result.data if result.data else []
        except Exception as e:
            self._handle_error("İthalat verileri getirme", e)
            return []

    def add_import_product(self, urun_adi, miktar, tarih, durum, alt_durum="", notlar=""):
        try:
            self._validate_data({
                'urun_adi': urun_adi,
                'miktar': miktar,
                'tarih': tarih,
                'durum': durum
            }, ['urun_adi', 'miktar', 'tarih', 'durum'])

            if isinstance(tarih, str):
                try:
                    tarih = datetime.strptime(tarih, "%d.%m.%Y").date().isoformat()
                except ValueError:
                    tarih = datetime.strptime(tarih, "%Y-%m-%d").date().isoformat()

            data = {
                "urun_adi": urun_adi,
                "miktar": miktar,
                "tarih": tarih,
                "durum": durum,
                "alt_durum": alt_durum,
                "notlar": notlar
            }

            result = self.supabase.table("imports").insert(data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            self._handle_error("İthalat ürünü ekleme", e)
            return None

    def update_import(self, import_id, **kwargs):
        try:
            if not import_id:
                raise ValueError("Geçersiz ithalat ID")

            update_data = {k: v for k, v in kwargs.items() if v is not None}
            
            if 'tarih' in update_data and isinstance(update_data['tarih'], str):
                try:
                    update_data['tarih'] = datetime.strptime(update_data['tarih'], "%d.%m.%Y").date().isoformat()
                except ValueError:
                    update_data['tarih'] = datetime.strptime(update_data['tarih'], "%Y-%m-%d").date().isoformat()

            result = self.supabase.table("imports").update(update_data).eq("id", import_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            self._handle_error("İthalat güncelleme", e)
            return None

    def delete_import(self, import_id):
        try:
            result = self.supabase.table("imports").delete().eq("id", import_id).execute()
            return len(result.data) > 0 if result.data else False
        except Exception as e:
            self._handle_error("İthalat silme", e)
            return False
        

          # ------------------ USERS FONKSİYONLARI ------------------ #
        # database_manager.py'ye ekleyin (__init__ fonksiyonunda self.users_table = "users" eklemeyi unutmayın)

    def add_user(self, username, password, role):
        """Yeni kullanıcı ekler"""
        try:
            # Basit hashleme (production'da bcrypt kullanın)
            password_hash = str(hash(password))
            
            data = {
                "username": username,
                "password_hash": password_hash,
                "role": role
            }
            
            result = self.supabase.table(self.users_table).insert(data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            self._handle_error("Kullanıcı ekleme", e)
            return None

    # Mevcut fonksiyonlara bu eklemeleri yapın
    def get_user_by_username(self, username):
        """Kullanıcı adına göre kullanıcı getirir"""
        try:
            result = self.supabase.table(self.users_table)\
                .select("*")\
                .eq("username", username)\
                .execute()
            return result.data[0] if result.data else None
        except Exception as e:
            self._handle_error("Kullanıcı getirme", e)
            return None

    def verify_user(self, username, password):
        """Kullanıcı doğrulama"""
        try:
            user = self.get_user_by_username(username)
            if not user:
                return None
                
            # BCRYPT ile şifre kontrolü
            if bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
                return user
            return None
        except Exception as e:
            self._handle_error("Kullanıcı doğrulama", e)
            return None
            

   # ================= VERSION CONTROL FONKSİYONLARI ================= #
    def get_latest_version_info(self):
        """Supabase'ten en son sürüm bilgisini getirir"""
        try:
            result = self.supabase.table("version_control")\
                       .select("*")\
                       .order("created_at", desc=True)\
                       .limit(1)\
                       .execute()
            return result.data[0] if result.data else None
        except Exception as e:
            self._handle_error("Sürüm bilgisi getirme", e)
            return None          

