from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth.hashers import make_password
from django.utils.translation import gettext_lazy as _

from safefileshare.file.models import SafeSecret


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


class SetPasswordForm(forms.ModelForm):
    """
    A form that lets a admin  set  password without entering the old password on files
    """
    password_hash = ReadOnlyPasswordHashField(
        label=_("Password"),
        help_text=_(
            "Raw passwords are not stored"
        ),
    )

    class Meta:
        model = SafeSecret
        fields = ['password_hash']
        field_classes = {'username': forms.CharField}

    error_messages = {
        'password_mismatch': _("The two password fields didn't match."),
    }
    new_password1 = forms.CharField(
        label=_("New password"),
        widget=forms.PasswordInput,
        strip=False,
    )
    new_password2 = forms.CharField(
        label=_("New password confirmation"),
        strip=False,
        widget=forms.PasswordInput,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.secret = kwargs.get('instance')

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(
                    self.error_messages['password_mismatch'],
                    code='password_mismatch',
                )
        return password2

    def save(self, commit=True):
        password = self.cleaned_data.get("new_password1")
        self.secret.password_hash = make_password(password)
        if commit:
            self.secret.save()
        return self.secret

    def save_m2m(self):
        """Fails without it"""
        pass

