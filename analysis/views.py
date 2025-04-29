from django.shortcuts import render, redirect
from django.conf import settings
from .forms import AnalysisForm
from .models import AnalysisResult
from .analyzer import GeminiMultiModalAnalyzer
from .scraper import WebScraper
from .utils import ImageLoader 
from PIL import Image
import traceback 

MAX_SEARCH_RESULTS = getattr(settings, 'MAX_SEARCH_RESULTS', 3)
MAX_CONTENT_LENGTH_PER_PAGE = getattr(settings, 'MAX_CONTENT_LENGTH_PER_PAGE', 2000)
REQUEST_TIMEOUT = getattr(settings, 'REQUEST_TIMEOUT', 15)
USER_AGENT = getattr(settings, 'USER_AGENT', 'Mozilla/5.0 ...') 

def analyze_image_view(request):
    form = AnalysisForm(request.POST or None, request.FILES or None)
    analysis_data = None
    error_message = None 

    if request.method == 'POST' and form.is_valid():
        source_type = form.cleaned_data['source_type']
        image_file = form.cleaned_data['image_file']
        image_url = form.cleaned_data['image_url']

        source_input = image_file.name if source_type == 'F' else image_url
        image_source_for_loader = image_file if source_type == 'F' else image_url

        image_loader = ImageLoader()
        analyzer = GeminiMultiModalAnalyzer()
        scraper = WebScraper() 

        try:
            print(f"Kaynak yükleniyor: {source_input}")
            image_pil = image_loader.load_from_source(image_source_for_loader)

            if not image_pil:
                raise ValueError("Görüntü yüklenemedi.")

            print("Görüntü analizi başlatılıyor...")
            analysis_result = analyzer.analyze_image(image_pil)
            if not analysis_result or not analysis_result.get("object") or not analysis_result.get("keywords"):
                raise ValueError("Görüntü analizi başarısız oldu veya eksik sonuç döndü.")

            object_name = analysis_result["object"]
            keywords = analysis_result["keywords"]
            print(f"Analiz sonucu: Nesne={object_name}, Anahtar Kelimeler={keywords}")

            search_query = f"{object_name} hakkında bilgi {' '.join(keywords[:3])}"
            print(f"Web araması yapılıyor: '{search_query}'")
            web_content = scraper.search_and_extract(search_query, num_results=MAX_SEARCH_RESULTS)

            summary = None
            summary_status = "Özet oluşturulamadı (web içeriği yok veya hata oluştu)."
            if web_content:
                print("Metin özeti oluşturuluyor...")
                summary = analyzer.summarize_text(web_content, object_name)
                if summary:
                    print("Özet başarıyla oluşturuldu.")
                    summary_status = summary
                else:
                    print("Özet oluşturulamadı.")
            else:
                print("Web içeriği bulunamadığı için özet atlandı.")

            db_result = AnalysisResult.objects.create(
                source_type=source_type,
                source_input=source_input,
                image_file=image_file if source_type == 'F' else None,
                object_name=object_name,
                keywords=keywords, 
                summary=summary
            )
            print(f"Sonuç veritabanına kaydedildi (ID: {db_result.id})")

            analysis_data = {
                'object': object_name,
                'keywords': keywords,
                'summary': summary_status,
                'image_url': db_result.image_file.url if db_result.image_file else image_url, 
                'source_type': db_result.get_source_type_display(),
                'source_input': source_input
            }

        except Exception as e:
            error_message = f"Analiz sırasında bir hata oluştu: {e}"
            print(f"HATA: {error_message}")
            print(traceback.format_exc())

    context = {
        'form': form,
        'analysis_data': analysis_data,
        'error_message': error_message,
    }
    return render(request, 'analysis/analyze_form.html', context)


def analysis_history_view(request):
    """Geçmiş analiz sonuçlarını listeler."""
    history = AnalysisResult.objects.all().order_by('-created_at') 
    context = {
        'history': history
    }
    return render(request, 'analysis/analysis_history.html', context)