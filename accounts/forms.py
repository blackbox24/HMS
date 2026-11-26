from django import forms


class LoginForm(forms.Form):
    """Minimal login form — we authenticate manually so axes sees exactly
    one attempt per POST (AuthenticationForm would authenticate twice)."""

    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


class ResetRequestForm(forms.Form):
    username = forms.CharField(
        label='Username',
        widget=forms.TextInput(attrs={
            'class': 'input',
            'autocomplete': 'username',
        }),
    )
