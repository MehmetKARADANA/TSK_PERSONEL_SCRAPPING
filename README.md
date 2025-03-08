TSK Personel Temin Bildirim Servisi
Bu depo, TSK Personel Temin web sitesindeki yeni duyuru ve temin ilanlarını takip eden ve bildirim servisine anlık bildirim gönderen bir servis içerir.
Servisler
1. Scraping Service (scrapping.py)
TSK Personel Temin web sitesini belirli aralıklarla kontrol eder
Yeni duyuru ve temin ilanlarını tespit eder
Bulunan yeni içerikleri Firebase Firestore'a kaydeder
2. Notification Service (notification_service.py)
Firebase Firestore'daki değişiklikleri gerçek zamanlı olarak izler
Yeni eklenen duyuru ve teminler için bildirim gönderir
FCM (Firebase Cloud Messaging) üzerinden mobil bildirimleri yönetir
3. Main Service (main.py)(ayrı ayrı çalıştırmayı tercih ediyorum)
Scraping ve Notification servislerini yönetir
Her iki servisi ayrı process'lerde çalıştırır
Kurulum
Gerekli paketleri yükleyin:
Firebase kimlik bilgilerini ekleyin:
tskpersonelteminapp-firebase-adminsdk-*.json dosyasını proje dizinine yerleştirin
Servisi başlatın:
Notlar
Servis VPS sunucularında çalışmak üzere tasarlanmıştır
Loglar ayrı dosyalarda tutulur
Screen ile arka planda çalıştırılabilir
Güvenlik
Firebase kimlik bilgileri ve diğer hassas dosyalar .gitignore ile versiyon kontrolünden çıkarılmıştır
Servis sadece yetkili kullanıcılara bildirim gönderir
Lisans
Bu proje özel kullanım için geliştirilmiştir.
