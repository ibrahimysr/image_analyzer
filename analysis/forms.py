from django import forms

class AnalysisForm(forms.Form):
    source_type = forms.ChoiceField(
        choices=[('F', 'Dosyadan Yükle'), ('U', 'URL Gir')],
        widget=forms.RadioSelect,
        initial='F',
        label="Kaynak Türü"
    )
    image_file = forms.ImageField(
        required=False, 
        label="Resim Dosyası"
    )
    image_url = forms.URLField(
        required=False,
        label="Resim URL'si"
    )

    def clean(self):
        cleaned_data = super().clean()
        source_type = cleaned_data.get('source_type')
        image_file = cleaned_data.get('image_file')
        image_url = cleaned_data.get('image_url')

        if source_type == 'F' and not image_file:
            raise forms.ValidationError("Dosya yükleme seçiliyken bir resim dosyası seçmelisiniz.", code='required')
        if source_type == 'U' and not image_url:
            raise forms.ValidationError("URL seçiliyken bir resim URL'si girmelisiniz.", code='required')
        if source_type == 'F' and image_url:
             cleaned_data['image_url'] = ''
        if source_type == 'U' and image_file:
             cleaned_data['image_file'] = None

        return cleaned_data