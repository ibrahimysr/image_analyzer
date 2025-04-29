import requests
import io
import os
from PIL import Image, UnidentifiedImageError
from typing import Optional
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.conf import settings 

REQUEST_TIMEOUT = getattr(settings, 'REQUEST_TIMEOUT', 15)
USER_AGENT = getattr(settings, 'USER_AGENT', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')

class ImageLoader:
    """
    Görüntüleri yerel dosya yolundan, bir URL'den veya Django UploadedFile'dan
    yüklemekten sorumlu sınıf.
    """

    def load_from_source(self, source: any) -> Optional[Image.Image]:
        """
        Verilen kaynak (dosya yolu, URL veya Django UploadedFile) üzerinden resmi yükler.

        Args:
            source: Resmin dosya yolu, URL'si veya Django InMemoryUploadedFile nesnesi.

        Returns:
            Başarılı olursa bir PIL Image nesnesi, aksi takdirde None.
        """
        print(f"[ImageLoader] Kaynak türü kontrol ediliyor: {type(source)}")
        try:
            if isinstance(source, str) and source.startswith(('http://', 'https://')):
                return self._load_from_url(source)
            elif isinstance(source, InMemoryUploadedFile): 
                print(f"[ImageLoader] Django UploadedFile işleniyor: {source.name}")
                return self._load_from_uploaded_file(source)
            elif isinstance(source, str) and os.path.exists(source): 
                 print(f"[ImageLoader] Yerel dosya yolu işleniyor (Dikkatli Kullanım): {source}")
                 return self._load_from_file(source)
            elif isinstance(source, str):
                 print(f"[ImageLoader Hata] Geçersiz string kaynak: '{source[:100]}...' Ne URL ne de geçerli dosya yolu.")
                 return None
            else:
                print(f"[ImageLoader Hata] Desteklenmeyen kaynak türü: {type(source)}")
                return None
        except Exception as e:
            print(f"[ImageLoader Hata] load_from_source içinde beklenmedik hata: {e}")
            return None

    def _load_from_url(self, url: str) -> Optional[Image.Image]:
        """URL'den resim yükler."""
        print(f"[ImageLoader] URL'den resim indiriliyor: {url}")
        try:
            headers = {'User-Agent': USER_AGENT}
            response = requests.get(url, stream=True, timeout=REQUEST_TIMEOUT, headers=headers)
            response.raise_for_status()

            content_type = response.headers.get('content-type', '').lower()
            if not content_type.startswith('image/'):
                print(f"[ImageLoader Hata] URL geçerli bir resim değil (Content-Type: {content_type}). URL: {url}")
                return None

            image_bytes = response.content
            if not image_bytes:
                print(f"[ImageLoader Hata] URL'den boş içerik alındı. URL: {url}")
                return None

            img = Image.open(io.BytesIO(image_bytes))
            img.verify()
            img = Image.open(io.BytesIO(image_bytes)) 
            print("[ImageLoader] Resim URL'den başarıyla yüklendi.")
            return img
        except requests.exceptions.Timeout:
            print(f"[ImageLoader Hata] URL'den resim indirilirken zaman aşımı: {url}")
            return None
        except requests.exceptions.RequestException as e:
            print(f"[ImageLoader Hata] URL'den resim indirilirken ağ hatası: {e}")
            return None
        except (IOError, UnidentifiedImageError, SyntaxError) as e:
             print(f"[ImageLoader Hata] URL'den gelen resim dosyası bozuk veya tanınamıyor: {e} (URL: {url})")
             return None
        except Exception as e:
            print(f"[ImageLoader Hata] URL yüklenirken beklenmedik hata: {e} (URL: {url})")
            return None

    def _load_from_file(self, file_path: str) -> Optional[Image.Image]:
        """Yerel dosyadan resim yükler."""
        print(f"[ImageLoader] Yerel dosyadan resim yükleniyor: {file_path}")
      
        if not os.path.exists(file_path):
            print(f"[ImageLoader Hata] Belirtilen dosya bulunamadı: {file_path}")
            return None
        try:
            img = Image.open(file_path)
            img.verify()
            img = Image.open(file_path) 
            print("[ImageLoader] Resim yerel dosyadan başarıyla yüklendi.")
            return img
        except FileNotFoundError:
            print(f"[ImageLoader Hata] Dosya bulunamadı (tekrar kontrol): {file_path}")
            return None
        except (IOError, UnidentifiedImageError, SyntaxError) as e:
            print(f"[ImageLoader Hata] Yerel resim dosyası açılırken veya tanınırken hata: {e} (Dosya: {file_path})")
            return None
        except Exception as e:
            print(f"[ImageLoader Hata] Yerel dosya yüklenirken beklenmedik hata: {e} (Dosya: {file_path})")
            return None

    def _load_from_uploaded_file(self, uploaded_file: InMemoryUploadedFile) -> Optional[Image.Image]:
        """Django InMemoryUploadedFile'dan resim yükler."""
        print(f"[ImageLoader] Django UploadedFile işleniyor: {uploaded_file.name}")
        try:
            uploaded_file.seek(0)
            img = Image.open(uploaded_file)
            img.verify()
            uploaded_file.seek(0)
            img = Image.open(uploaded_file)
            print("[ImageLoader] Resim UploadedFile'dan başarıyla yüklendi.")
            return img
        except (IOError, UnidentifiedImageError, SyntaxError) as e:
            print(f"[ImageLoader Hata] Yüklenen resim dosyası bozuk veya tanınamıyor: {e} (Dosya: {uploaded_file.name})")
            return None
        except Exception as e:
             print(f"[ImageLoader Hata] UploadedFile işlenirken beklenmedik hata: {e} (Dosya: {uploaded_file.name})")
             return None