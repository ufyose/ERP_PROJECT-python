from packaging import version
from database_manager import DatabaseManager

# Uygulamanızın ŞU ANKİ versiyonu (projeye göre güncelleyin)
CURRENT_VERSION = "1.0.0"  

def is_new_version_available():
    """Yeni sürüm olup olmadığını kontrol eder"""
    try:
        db = DatabaseManager()
        latest_data = db.get_latest_version_info()
        
        if not latest_data:
            print("⚠️ Veritabanında versiyon bilgisi bulunamadı")
            return False, CURRENT_VERSION
        
        print(f"🔍 Veritabanındaki son versiyon: {latest_data['version']}")
        print(f"📱 Mevcut versiyon: {CURRENT_VERSION}")
        
        latest_ver = latest_data['version']
        
        # Sürüm karşılaştırması
        if version.parse(latest_ver) > version.parse(CURRENT_VERSION):
            print("🆕 Yeni versiyon bulundu!")
            return True, latest_data  # (yeni_var_mi, sürüm_bilgisi)
            
        print("✅ Zaten en güncel sürüm kullanılıyor")
        return False, CURRENT_VERSION
        
    except Exception as e:
        print(f"❌ Hata oluştu: {str(e)}")
        return False, CURRENT_VERSION

# Test kısmı (dosya doğrudan çalıştırılırsa)
if __name__ == "__main__":
    print("\n🔎 Versiyon kontrolü başlatılıyor...")
    available, version_data = is_new_version_available()
    
    print("\n📊 Sonuçlar:")
    print(f"Güncelleme gerekli mi: {'Evet' if available else 'Hayır'}")
    if isinstance(version_data, dict):
        print(f"Son versiyon: {version_data['version']}")
        print(f"İndirme URL: {version_data.get('download_url', 'Yok')}")
    else:
        print(f"Mevcut versiyon: {version_data}")