from django import forms

THEMES = [
    ('light', 'Light Theme'),
    ('dark', 'Dark Theme'),
    ('blue', 'Blue Modern Theme'),
]

class DocUploadForm(forms.Form):
    doc_file = forms.FileField(label='Upload a DOCX File')
    theme = forms.ChoiceField(choices=THEMES, label='Choose Theme')