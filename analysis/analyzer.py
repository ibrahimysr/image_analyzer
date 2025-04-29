
import google.generativeai as genai
from PIL import Image
import re
from typing import Optional, Dict, Any, List
from django.conf import settings # Django ayarları için

GEMINI_API_KEY = getattr(settings, 'GEMINI_API_KEY', None) # API Anahtarı ayarlardan alınır
GEMINI_MODEL_VISION = getattr(settings, 'GEMINI_MODEL_VISION', 'gemini-1.5-flash')
GEMINI_MODEL_TEXT = getattr(settings, 'GEMINI_MODEL_TEXT', 'gemini-1.5-flash')
REQUEST_TIMEOUT = getattr(settings, 'REQUEST_TIMEOUT', 15)

class GeminiMultiModalAnalyzer:
    """
    Gemini AI modelini kullanarak hem görüntü analizi (obje/anahtar kelime)
    hem de metin özetleme işlemlerini gerçekleştiren sınıf.
    """
    def __init__(self):
        """
        Analyzer'ı başlatır ve Gemini API'sini yapılandırır.
        API anahtarını Django ayarlarından alır.
        """
        self.api_key = GEMINI_API_KEY
        if not self.api_key:
            print("[Gemini Hata] GEMINI_API_KEY ayarlanmamış!")
            raise ValueError("Gemini API anahtarı Django ayarlarında (settings.py) tanımlanmamış.")

        self._configure_gemini()
        try:
            self.vision_model = genai.GenerativeModel(GEMINI_MODEL_VISION)
            self.text_model = genai.GenerativeModel(GEMINI_MODEL_TEXT)
            print(f"[Gemini] Vision Model ({GEMINI_MODEL_VISION}) ve Text Model ({GEMINI_MODEL_TEXT}) hazırlandı.")
        except Exception as e:
             print(f"[Gemini Hata] Modeller oluşturulurken hata: {e}")
             raise ConnectionError(f"Gemini modelleri ({GEMINI_MODEL_VISION}, {GEMINI_MODEL_TEXT}) oluşturulamadı. Model adlarını ve API erişimini kontrol edin.") from e


    def _configure_gemini(self):
        """Gemini API istemcisini yapılandırır."""
        try:
            genai.configure(api_key=self.api_key)
            print("[Gemini] API başarıyla yapılandırıldı.")
        except Exception as e:
            print(f"[Gemini Hata] API anahtarı yapılandırılamadı: {e}")
            raise ConnectionError("Gemini API yapılandırılamadı. API anahtarınızı kontrol edin.") from e

    def analyze_image(self, image: Image.Image) -> Optional[Dict[str, Any]]:
        """
        Verilen görüntüyü analiz ederek ana nesneyi ve anahtar kelimeleri çıkarır.

        Args:
            image: Analiz edilecek PIL Image nesnesi.

        Returns:
            {'object': str, 'keywords': List[str]} içeren bir sözlük veya hata durumunda None.
        """
        print("[Gemini] Görüntü analizi başlatılıyor (obje/anahtar kelimeler)...")
        prompt = """
        Bu resimdeki ana, en belirgin nesneyi tek kelime veya kısa bir ifadeyle (Türkçe) tanımla.
        Ardından, bu nesneyle ilgili 3 ila 5 adet alakalı Türkçe anahtar kelime listele.
        Cevabını SADECE şu formatta ver, başka hiçbir açıklama ekleme:
        Nesne: [Ana nesnenin adı]
        Anahtar Kelimeler: [kelime1], [kelime2], [kelime3], ...
        """
        try:
            response = self.vision_model.generate_content(
                [prompt, image],
                request_options={'timeout': REQUEST_TIMEOUT}
            )
          
            if not response.parts:
                 safety_feedback = response.prompt_feedback if hasattr(response, 'prompt_feedback') else "Detay yok"
                 print(f"[Gemini Hata] Görüntü analizinden boş yanıt alındı. Olası neden: Güvenlik filtresi. Feedback: {safety_feedback}")
                 return None

            text_response = response.text.strip()
            print(f"[Gemini] Ham Analiz Yanıtı:\n{text_response}")
            return self._parse_analysis_response(text_response)

        except Exception as e:
            print(f"[Gemini Hata] Görüntü analizi sırasında API hatası: {e}")
           
            return None

    def _parse_analysis_response(self, text_response: str) -> Optional[Dict[str, Any]]:
        """Gemini'den gelen nesne/anahtar kelime yanıtını ayrıştırır."""
        try:
            nesne_match = re.search(r"Nesne:\s*(.+)", text_response, re.IGNORECASE | re.DOTALL)
            keywords_match = re.search(r"Anahtar Kelimeler:\s*(.+)", text_response, re.IGNORECASE | re.DOTALL)

            if nesne_match and keywords_match:
                nesne = nesne_match.group(1).split('\n')[0].strip()
                keywords_raw = keywords_match.group(1).strip()
                keywords_raw = keywords_raw.rstrip('.')
                keywords = [kw.strip() for kw in keywords_raw.split(',') if kw.strip()]

                if nesne and keywords:
                    print(f"[Gemini] Ayrıştırma başarılı: Nesne='{nesne}', Anahtar Kelimeler={keywords}")
                    return {"object": nesne, "keywords": keywords}
                else:
                    print("[Gemini Hata] Ayrıştırma: Yanıtta nesne veya anahtar kelimeler boş geldi.")
                    self._print_failed_response(text_response)
                    return None
            else:
                print("[Gemini Hata] Ayrıştırma: Model yanıtı beklenen formatta değil.")
                self._print_failed_response(text_response)
                return None
        except Exception as e:
            print(f"[Gemini Hata] Ayrıştırma sırasında hata: {e}")
            self._print_failed_response(text_response)
            return None

    def summarize_text(self, context: str, object_name: str) -> Optional[str]:
        """
        Verilen metin bağlamını (web içeriği) kullanarak obje hakkında bir özet oluşturur.

        Args:
            context: Özetlenecek web içeriği metni.
            object_name: Özetin odaklanacağı nesnenin adı.

        Returns:
            Oluşturulan özet metni veya hata durumunda None.
        """
        print(f"[Gemini] '{object_name}' hakkında özet oluşturuluyor...")
        # Çok uzun context'leri kırpmak gerekebilir, modelin limitlerini aşmamak için.
    

        prompt = f"""
        Aşağıdaki metin '{object_name}' hakkında yapılan bir web aramasının sonuçlarından derlenmiştir.
        Bu metinleri kullanarak '{object_name}' hakkında 2-3 cümlelik kısa, bilgilendirici ve akıcı bir Türkçe açıklama oluştur.
        Sadece sağlanan metinlerdeki bilgilere dayan, kendi bilgini katma.
        Eğer metinlerde '{object_name}' ile ilgili yeterli veya anlamlı bilgi yoksa, "Sağlanan metinlerde bu konu hakkında yeterli bilgi bulunamadı." şeklinde bir yanıt ver.
        Cevabını doğrudan açıklama olarak yaz, "Metinlere göre..." gibi girişler yapma.

        --- Web İçeriği Başlangıcı ---
        {context[:20000]} 
        --- Web İçeriği Sonu ---

        '{object_name}' hakkında açıklama:
        """
        try:
            response = self.text_model.generate_content(
                prompt,
                request_options={'timeout': REQUEST_TIMEOUT * 2}
            )

            if not response.parts:
                 safety_feedback = response.prompt_feedback if hasattr(response, 'prompt_feedback') else "Detay yok"
                 print(f"[Gemini Hata] Özetlemeden boş yanıt alındı. Olası neden: Güvenlik filtresi. Feedback: {safety_feedback}")
                 return None

            summary = response.text.strip()
            print("[Gemini] Özet başarıyla oluşturuldu.")
            if len(summary) < 20 and ("bilgi bulunamadı" not in summary.lower()):
                 print(f"[Gemini Uyarı] Oluşturulan özet çok kısa görünüyor: '{summary}'")
            return summary
        except Exception as e:
            print(f"[Gemini Hata] Metin özetleme sırasında API hatası: {e}")
            return None

    def _print_failed_response(self, response_text: str):
        """Başarısız ayrıştırma durumunda modelin ham yanıtını yazdırır."""
        print("--- Başarısız Model Yanıtı (Ayrıştırma) ---")
        print(response_text)
        print("-----------------------------------------")