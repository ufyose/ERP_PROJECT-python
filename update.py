# update.py
import os
import sys
import shutil
import requests
import hashlib
import zipfile
import subprocess
from pathlib import Path
from database_manager import DatabaseManager  # Sizin veritabanı yöneticiniz

class FinanceUpdater:
    def __init__(self):
        self.temp_dir = "temp_finance_update"
        self.db = DatabaseManager()  # Veritabanı bağlantısı
        self.exclude_files = self._get_protected_files()  # DB'den korunacak dosyaları al

    def _get_protected_files(self):
        """Veritabanından korunacak dosya listesini çek"""
        try:
            result = self.db.supabase.table("app_config")\
                       .select("protected_files")\
                       .eq("config_key", "update_protection")\
                       .single()\
                       .execute()
            return result.data.get("protected_files", [])
        except Exception as e:
            print(f"⚠️ Config okuma hatası: {e}")
            return []

    def check_version(self):
        """Veritabanından en son sürümü kontrol et"""
        try:
            latest = self.db.supabase.table("version_control")\
                     .select("*")\
                     .order("created_at", desc=True)\
                     .limit(1)\
                     .execute()
            return latest.data[0] if latest.data else None
        except Exception as e:
            print(f"❌ Sürüm kontrol hatası: {e}")
            return None

    def download_update(self, url):
        try:
            print(f"🔄 İndirme denemesi: {url}")
            
            # SSL doğrulamasını geçici olarak kapat
            import urllib3
            urllib3.disable_warnings()
            
            response = requests.get(url, stream=True, timeout=10, verify=False)
            response.raise_for_status()  # HTTP hatalarını yakala
            
            # İndirilen veriyi göster
            print(f"🔵 HTTP Durumu: {response.status_code}")
            print(f"🔵 İçerik Uzunluğu: {len(response.content)} bayt")
            
            # ... dosya kaydetme kodu ...
            
        except Exception as e:
            print(f"🔴 Kritik Hata Detayı: {type(e).__name__}: {str(e)}")
            return None

    def apply_update(self, zip_path):
        """Güncellemeyi uygula"""
        try:
            print("🔄 Uygulanıyor...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(self.temp_dir)
            
            # Veritabanında bakım modunu aç
            self.db.supabase.table("app_status")\
                 .upsert({"key": "maintenance", "value": True}).execute()
            
            for item in Path(self.temp_dir).iterdir():
                if item.name in self.exclude_files:
                    continue
                
                dest = Path.cwd() / item.name
                if dest.exists():
                    shutil.rmtree(dest) if dest.is_dir() else dest.unlink()
                shutil.move(str(item), str(dest))
            
            # Sürüm güncellemesini kaydet
            version_info = self.check_version()
            if version_info:
                self.db.supabase.table("system_info")\
                     .upsert({"current_version": version_info["version"]}).execute()
            
            return True
        except Exception as e:
            self._log_error("apply", str(e))
            return False
        finally:
            # Bakım modunu kapat
            self.db.supabase.table("app_status")\
                 .upsert({"key": "maintenance", "value": False}).execute()

    def _log_error(self, stage, error):
        """Hataları veritabanına kaydet"""
        self.db.supabase.table("update_errors").insert({
            "stage": stage,
            "error": error,
            "timestamp": "now()"
        }).execute()

def perform_update():
    """Tam güncelleme akışı"""
    updater = FinanceUpdater()
    
    if latest := updater.check_version():
        if zip_path := updater.download_update(latest["download_url"]):
            if updater.verify_checksum(zip_path, latest.get("checksum")):
                if updater.apply_update(zip_path):
                    updater.db.supabase.table("update_logs").insert({
                        "version": latest["version"],
                        "status": "success"
                    }).execute()
                    updater.restart_app()

if __name__ == "__main__":
    perform_update()