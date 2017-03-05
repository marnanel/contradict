from django import forms

class DictionaryUploadForm(forms.Form):
	dictionary = forms.FileField()

