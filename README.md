# Görsel Analiz ve Araştırma Uygulaması


Django ile geliştirilmiş, yapay zeka destekli görsel analiz ve otomatik araştırma platformu. Yüklediğiniz görselleri analiz ederek anahtar kelimeleri çıkarır ve bu kelimeler üzerinden kapsamlı web araştırması yaparak size detaylı bilgiler sunar.

## ✨ Özellikler

- 🖼️ URL veya yerel kaynaktan resim yükleme
- 🤖 Yapay zeka ile görsel analizi
- 🔍 Görseldeki nesnelerin/kavramların tespiti
- 🔑 Anahtar kelimelerin otomatik çıkarılması
- 📊 İnternet üzerinden kapsamlı araştırma
- 📝 Sonuçların anlaşılır bir formatta sunulması
- 💾 Geçmiş aramaların kaydedilmesi
- 📱 Mobil uyumlu tasarım

## 🖥️ Ekran Görüntüleri

<table>
    <tr>
    <td>Ana Sayfa</td>
    <td>Analiz Sonuçları</td>
    <td>Geçmiş Aramalar</td>
  </tr>
  <tr>
    <td><img src="https://i.imgur.com/AUCKF2l.png" alt="Ana Sayfa" /></td>
    <td><img src="https://i.imgur.com/OIP3piy.png" alt="Analiz Sonuçları" /></td>
    <td><img src="blob:https://imgur.com/a9d6a7a6-fb6a-4f3f-b9fd-41c9f32f1fe1" alt="Geçmiş Aramalar" /></td>
  </tr>


</table>

## 🛠️ Teknolojik Altyapı

### Backend
- [Django](https://www.djangoproject.com/) - Web framework
- [Django REST Framework](https://www.django-rest-framework.org/) - API yapısı
- [Sqlite](https://www.sqlite.org/) - Veritabanı


### Frontend
- [HTML5](https://developer.mozilla.org/en-US/docs/Web/HTML) / [CSS3](https://developer.mozilla.org/en-US/docs/Web/CSS) / [JavaScript](https://developer.mozilla.org/en-US/docs/Web/JavaScript)
- [Bootstrap](https://getbootstrap.com/) - Responsive tasarım
- [jQuery](https://jquery.com/) / [Vue.js](https://vuejs.org/) / [React](https://reactjs.org/) - UI etkileşimleri

## 🚀 Kurulum

### Gereksinimler
- Python 3.8+
- Django 4.0+
- Sqlite


### Yerel Ortamda Kurulum

```bash
# Repo'yu klonlayın
git clone https://github.com/ibrahimysr/image_analyzer.git
cd image_analyzer_project

# Veritabanını oluşturun
python manage.py migrate

# Yapay zeka modeleli için api key alın
GEMINI_API_KEY = "apikey"

# Geliştirme sunucusunu başlatın
python manage.py runserver
```



## 📋 Kullanım

1. Ana sayfaya gidin ve "Resim Yükle" butonuna tıklayın
2. Bir resim URL'si girin veya bilgisayarınızdan bir resim seçin
3. "Analiz Et" butonuna tıklayın
4. Sistem görsel analizi gerçekleştirecek ve anahtar kelimeleri çıkaracak
5. Çıkarılan anahtar kelimeler üzerinden web araştırması otomatik başlayacak
6. Araştırma sonuçları ve analiz detayları size sunulacak
7. Dilediğiniz sonuçları inceleyebilir veya kaydedebilirsiniz

## 🔧 Özelleştirme

Uygulama, `settings.py` dosyasında aşağıdaki ayarlar ile özelleştirilebilir:


