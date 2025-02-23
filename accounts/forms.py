from django.contrib.auth.forms import UserCreationForm, AuthenticationForm



from django import forms


class SignUpForm(UserCreationForm):
    from schoolmock_app.models import Profile
    role = forms.ChoiceField(choices=Profile.ROLE, label="Роль", widget=forms.RadioSelect)

    class Meta:
        from django.contrib.auth.models import User
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control'}),
        }
    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    username = forms.CharField(max_length=254, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))