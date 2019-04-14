from django import forms


class UploadFileForm(forms.Form):
    link = forms.CharField(max_length=50)
    file = forms.FileField()
    password = forms.PasswordInput()


