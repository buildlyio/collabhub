# onboarding/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import TeamMember

class TeamMemberRegistrationForm(UserCreationForm):
    team_member_type = forms.ChoiceField()
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    email = forms.EmailField()
    bio = forms.CharField(widget=forms.Textarea, required=False)
    linkedin = forms.URLField(required=False)
    experience_years = forms.IntegerField(required=False)
    github_account = forms.URLField(required=False)

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'team_member_type', 'first_name', 'last_name', 'email', 'bio', 'linkedin', 'experience_years', 'github_account']

from .models import Resource

class ResourceForm(forms.ModelForm):
    class Meta:
        model = Resource
        fields = ['team_member_type', 'title', 'link', 'document']