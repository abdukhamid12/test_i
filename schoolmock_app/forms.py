from django import forms

from .models import *

class EnterNameForm(forms.ModelForm):
  class Meta:
    model = Profile
    fields = ['name', 'surname', 'school', 'classroom']
    widgets = {
      'name': forms.TextInput(attrs={'type': 'text', 'id': 'student-name', 'placeholder': 'Введите имя'}),
      'surname': forms.TextInput(attrs={'type': 'text', 'id': 'student-surname', 'placeholder': 'Введите фамилию'}),
      'school': forms.TextInput(attrs={'type': 'text', 'id': 'student-school', 'placeholder': 'Введите школу'}),
      'classroom': forms.TextInput(attrs={'type': 'text', 'id': 'student-class', 'placeholder': 'Введите класс'}),
    }