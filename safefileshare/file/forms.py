from django import forms
from django.forms import ValidationError


class UploadFileForm(forms.Form):
    secret_link = forms.URLField(required=False)
    secret_file = forms.FileField(required=False)
    secret_password = forms.CharField(
        max_length=64,
        label="Your passphrase",
        widget=forms.PasswordInput()
    )

    def is_valid(self):
        valid = super().is_valid()
        form_data = self.cleaned_data
        check = [form_data.get("secret_link"), form_data.get("secret_file")]
        if all(check) or not any(check):
            return False
        return valid


class GetSecretForm(forms.Form):
    password = forms.CharField(
        max_length=64,
        label="Passphrase",
        widget=forms.PasswordInput()
    )
