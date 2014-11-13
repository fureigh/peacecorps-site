from django import forms
from django.contrib.auth.forms import (
    UserCreationForm, AdminPasswordChangeForm)
from django.utils.translation import ugettext_lazy as _

from contenteditor import models


# Password length requirements
def password_validator(password):
    """Validates a given string against required password params. This is
    required in order to maintain FISMA compliance."""
    # Set up an errors array to capture things we find
    errors = []

    # Defines special characters we allow
    # TODO: I guess this could be a regex instead, I just typed all the chars
    # on my keyboard :)
    valid_special_chars = set('~`!@#$%^&*()-_=+[{]}\|;:'",<.>/?/*-.+")
    if not password:
        errors.append('Password cannot be blank.')
    if not any(x.isupper() for x in password):
        errors.append('Password needs at least one uppercase letter.')
    if not any(x.islower() for x in password):
        errors.append('Password needs at least one lowercase letter.')
    if not any(x.isdigit() for x in password):
        errors.append('Password needs at least one number.')
    if not any((x in valid_special_chars) for x in password):
        errors.append('Password needs a special character.')
    if not len(password) >= 20:
        errors.append('Password must be at least 20 characters in length.')

    return errors


class StrictUserCreationForm(UserCreationForm):
    password1 = forms.CharField(
        label=_("Password"), widget=forms.PasswordInput, help_text=_("""
            Enter a password. Requirements include: at least 20 characters,
            at least one uppercase letter, at least one lowercase letter, at
            least one number, and at least one special character.
            """))

    def clean_password1(self):
        """Adds to the default password validation routine in order to enforce
        stronger passwords"""
        password = self.cleaned_data['password1']
        errors = password_validator(password)

        # If password_validator returns errors, raise an error, else proceed.
        if errors:
            raise forms.ValidationError('\n'.join(errors))
        else:
            return password


class StrictAdminPasswordChangeForm(AdminPasswordChangeForm):
    password1 = forms.CharField(
        label=_("Password"), widget=forms.PasswordInput, help_text=_("""
            Enter a password. Requirements include: at least 20 characters,
            at least one uppercase letter, at least one lowercase letter, at
            least one number, and at least one special character.
            """))

    def clean_password1(self):
        """Adds to the default password validation routine in order to enforce
        stronger passwords"""
        password = self.cleaned_data['password1']
        errors = password_validator(password)
        # Also check that this is a new password
        if self.user.check_password(self.cleaned_data['password1']):
            errors.append("Must not reuse a password")

        # If password_validator returns errors, raise an error, else proceed.
        if errors:
            raise forms.ValidationError('\n'.join(errors))
        else:
            return password

    def save(self):
        user = super(StrictAdminPasswordChangeForm, self).save()
        user.extra.password_expires = models.expires()
        user.extra.save()
        return user