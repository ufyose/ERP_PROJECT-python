# test_update.py adında yeni bir dosya oluşturun ve aşağıdaki kodu ekleyin
from update import FinanceUpdater

def test_update():
    updater = FinanceUpdater()
    
    # Veritabanındaki en son versiyonu al
    latest_version = updater.check_version()
    if not latest_version:
        print("❌ Versiyon bilgisi alınamadı!")
        return
    
    print(f"⏳ Son versiyon: {latest_version['version']}")
    
    # İndirme işlemini test et (gerçek bir URL olmalı)
    download_url = latest_version["download_url"]
    print(f"🔗 İndirme URL: {download_url}")
    
    zip_path = updater.download_update(download_url)
    if not zip_path:
        print("❌ İndirme başarısız!")
        return
    
    print(f"✅ İndirildi: {zip_path}")
    
    # Güncellemeyi uygula (test amaçlı)
    success = updater.apply_update(zip_path)
    print(f"🔄 Güncelleme başarılı mı: {success}")

if __name__ == "__main__":
    test_update()