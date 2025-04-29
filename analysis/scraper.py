import requests
import time
from typing import Optional, List
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
import re
from django.conf import settings 

MAX_SEARCH_RESULTS = getattr(settings, 'MAX_SEARCH_RESULTS', 3)
MAX_CONTENT_LENGTH_PER_PAGE = getattr(settings, 'MAX_CONTENT_LENGTH_PER_PAGE', 2000)
REQUEST_TIMEOUT = getattr(settings, 'REQUEST_TIMEOUT', 15)
USER_AGENT = getattr(settings, 'USER_AGENT', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')


class WebScraper:
 
    def search_and_extract(self, query: str, num_results: int = MAX_SEARCH_RESULTS) -> Optional[str]:
      
        print(f"\n[WebScraper] Web'de '{query}' için arama yapılıyor ({num_results} sonuç hedefleniyor)...")
        extracted_texts: List[str] = []
        urls_processed: set[str] = set()
        urls_tried: int = 0

        try:
            
            with DDGS(timeout=REQUEST_TIMEOUT) as ddgs:
                search_generator = ddgs.text(query, max_results=num_results + 5) 

                for result in search_generator:
                    if len(extracted_texts) >= num_results:
                        print("[WebScraper] Hedeflenen sayıda sayfa içeriği toplandı.")
                        break

                    urls_tried += 1
                    url = result.get('href')

                    if not url or not url.startswith(('http://', 'https://')) or url in urls_processed:
                        print(f"[WebScraper] Geçersiz veya tekrarlanan URL atlanıyor: {url}")
                        continue

                    urls_processed.add(url) 
                    page_content = self._fetch_and_parse_url(url)

                    if page_content:
                        extracted_texts.append(page_content)
                        print(f"[WebScraper] Başarılı: {len(extracted_texts)}/{num_results} sayfa çıkarıldı.")
                    else:
                        
                        pass

                    time.sleep(0.4) 

            if not extracted_texts:
                print(f"[WebScraper] Arama sonuçlarından ({urls_tried} denenen URL) metin içeriği çıkarılamadı.")
                return None

            print(f"\n[WebScraper] Toplam {len(extracted_texts)} sayfadan metin başarıyla çıkarıldı.")
            return "\n\n--- Yeni Sayfa İçeriği ---\n\n".join(extracted_texts)

        except Exception as e:
            print(f"[WebScraper Hata] Web araması/işlemesi sırasında genel hata: {e}")
            import traceback
            print(traceback.format_exc()) 
            return None

    def _fetch_and_parse_url(self, url: str) -> Optional[str]:
        print(f"  [WebScraper] -> Sayfa indiriliyor/işleniyor: {url[:80]}...")
        try:
            headers = {'User-Agent': USER_AGENT}
            response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT, allow_redirects=True)
            response.raise_for_status() 

            content_type = response.headers.get('Content-Type', '').lower()
            if 'text/html' not in content_type:
                print(f"     [WebScraper] Atlanıyor: HTML olmayan içerik ({content_type}). URL: {url}")
                return None

            if len(response.content) > 5_000_000: 
                 print(f"     [WebScraper] Atlanıyor: İçerik çok büyük ({len(response.content)} bytes). URL: {url}")
                 return None

           
            try:
                 soup = BeautifulSoup(response.content, 'lxml') 
            except ImportError:
                 soup = BeautifulSoup(response.content, 'html.parser')

            for element in soup(["script", "style", "nav", "footer", "header", "aside", "form", "button", "img", "svg", "figure", "noscript"]):
                element.decompose()

            main_content = soup.find('article') or soup.find('main') or soup.find('div', role='main') or soup.body
            if not main_content:
                 print(f"     [WebScraper] Sayfada ana içerik alanı (article, main, body) bulunamadı. URL: {url}")
                 return None

            page_text = main_content.get_text(separator='\n', strip=True)
            page_text = re.sub(r'\n\s*\n', '\n', page_text).strip()

            if page_text and len(page_text) > 50: 
                print(f"     [WebScraper] Metin çıkarıldı (yaklaşık {len(page_text)} karakter).")
                return page_text[:MAX_CONTENT_LENGTH_PER_PAGE]
            elif not page_text:
                print(f"     [WebScraper] Sayfadan metin çıkarılamadı (boş içerik). URL: {url}")
                return None
            else:
                 print(f"     [WebScraper] Çıkarılan metin çok kısa ({len(page_text)} karakter), atlanıyor. URL: {url}")
                 return None

        except requests.exceptions.Timeout:
            print(f"     [WebScraper Hata] Zaman aşımı (URL: {url[:80]}...)")
            return None
        except requests.exceptions.TooManyRedirects:
             print(f"     [WebScraper Hata] Çok fazla yönlendirme (URL: {url[:80]}...)")
             return None
        except requests.exceptions.RequestException as e:
            print(f"     [WebScraper Hata] Sayfa indirilemedi (URL: {url[:80]}...): {e}")
            return None
        except Exception as e:
            print(f"     [WebScraper Hata] Sayfa işlenirken beklenmedik hata (URL: {url[:80]}...): {e}")
            import traceback
            print(traceback.format_exc(limit=1)) 
            return None