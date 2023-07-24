from django import forms
from .models import Profile, Invitation


from core.forms import BootstrapForm

class ProfileForm(BootstrapForm, forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('bio',)

class InvitationForm(BootstrapForm, forms.ModelForm):
    class Meta:
        model = Invitation
        fields = ('email',)