document.addEventListener('DOMContentLoaded', () => {

    const analysisForm = document.getElementById('analysis-form'); 
    const sourceTypeRadios = document.querySelectorAll('input[name="source_type"]');
    const imageFileField = document.getElementById('image-file-field'); 
    const imageUrlField = document.getElementById('image-url-field'); 
    const submitButton = analysisForm ? analysisForm.querySelector('button[type="submit"]') : null;
    const loadingIndicator = document.getElementById('loading-indicator'); 

    function toggleSourceFields() {
        let selectedType = 'F';
        sourceTypeRadios.forEach(radio => {
            if (radio.checked) {
                selectedType = radio.value;
            }
        });

        if (imageFileField && imageUrlField) {
            if (selectedType === 'F') {
                imageFileField.classList.remove('hidden');
                imageUrlField.classList.add('hidden');
            } else if (selectedType === 'U') {
                imageFileField.classList.add('hidden');
                imageUrlField.classList.remove('hidden');
            }
        } else {
             console.warn("Dosya veya URL alanları bulunamadı. HTML ID'lerini kontrol edin.");
        }
    }

    if (sourceTypeRadios.length > 0) {
        sourceTypeRadios.forEach(radio => {
            radio.addEventListener('change', toggleSourceFields);
        });
        toggleSourceFields();
    } else {
        console.warn("Kaynak türü radio butonları bulunamadı.");
    }


    if (analysisForm && submitButton && loadingIndicator) {
        analysisForm.addEventListener('submit', () => {
            submitButton.disabled = true;
            loadingIndicator.classList.remove('hidden');
            submitButton.textContent = 'Analiz Ediliyor...';

           
        });
    } else {
         console.warn("Form, gönder butonu veya yükleniyor göstergesi bulunamadı. ID'leri kontrol edin.");
    }

}); 