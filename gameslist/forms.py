from django import forms
from .models import SYSTEMS

class SystemForm(forms.Form):
    system = forms.ChoiceField(choices=SYSTEMS,label="System",widget=forms.Select)