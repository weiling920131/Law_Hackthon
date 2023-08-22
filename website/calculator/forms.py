from django import forms
from .models import dist

class locationForm(forms.Form):
    d = [('0', '請選擇')]
    d += [(i.dist_id, i.name) for i in dist.objects.all()]
    縣市 = forms.ChoiceField(choices=d, widget=forms.Select(attrs={'hx-get': 'load_town', 'hx-target': '#id_鄉鎮市區'}))
    鄉鎮市區 = forms.ChoiceField()