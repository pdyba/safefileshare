from django import forms


class UploadFileForm(forms.Form):
    secret_link = forms.URLField(required=False)
    secret_file = forms.FileField(required=False)
    secret_password = forms.CharField(
        max_length=64,
        label="Your passphrase",
        widget=forms.PasswordInput()
    )

    def validate(self, value):
        super().validate(value)
        if not self.secret_link and not self.secret_file:
            return False
        return True


class GetSecretForm(forms.Form):
    password = forms.CharField(
        max_length=64,
        label="Passphrase",
        widget=forms.PasswordInput()
    )
