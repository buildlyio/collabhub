# onboarding/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import TeamMember, TeamMemberType, DevelopmentAgency
from .models import TEAM_MEMBER_TYPES

class TeamMemberRegistrationForm(UserCreationForm):
    team_member_type = forms.ChoiceField(choices=[(key, value) for key, value in TEAM_MEMBER_TYPES if key != 'Everyone'])
    profile_types = forms.ModelMultipleChoiceField(
        queryset=TeamMemberType.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        help_text='Select all that apply (optional, uses team_member_type if none selected)'
    )
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    email = forms.EmailField()
    bio = forms.CharField(widget=forms.Textarea, required=False)
    linkedin = forms.URLField(required=False)
    experience_years = forms.IntegerField(required=False)
    github_account = forms.URLField(required=False)
    
    # Agency fields
    is_independent = forms.BooleanField(
        required=False,
        initial=True,
        label="I am an independent developer"
    )
    agency = forms.ModelChoiceField(
        queryset=DevelopmentAgency.objects.all(),
        required=False,
        empty_label="Select registered agency (if applicable)",
        help_text="Select your agency if it's registered on our platform"
    )
    agency_name_text = forms.CharField(
        max_length=255,
        required=False,
        label="Agency Name",
        help_text="If your agency isn't listed above, enter the name here"
    )

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'team_member_type', 'profile_types', 'first_name', 'last_name', 'email', 'bio', 'linkedin', 'experience_years', 'github_account', 'is_independent', 'agency', 'agency_name_text']

from .models import Resource

class TeamMemberUpdateForm(forms.ModelForm):
    class Meta:
        model = TeamMember
        fields = '__all__'
        
class ResourceForm(forms.ModelForm):
    team_member_type = forms.ChoiceField(
        choices=TEAM_MEMBER_TYPES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        help_text='Select the team member type this resource is intended for'
    )
    
    class Meta:
        model = Resource
        fields = ['team_member_type', 'title', 'link', 'document', 'descr']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Enter resource title'}),
            'link': forms.URLInput(attrs={'placeholder': 'https://example.com'}),
            'descr': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Describe this resource and how it helps developers'}),
        }


from .models import DevelopmentAgency
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

class DevelopmentAgencyForm(forms.ModelForm):
    class Meta:
        model = DevelopmentAgency
        fields = ['agency_name', 'team_size', 'skills', 'background', 'hourly_rate', 'project_rate', 'industries_worked', 'agency_type', 'github_repository', 'contact_name', 'contact_email', 'contact_phone', 'linkedin_url', 'how_they_found_us', 'logo']
        widgets = {
            'skills': forms.Textarea(attrs={'rows': 3}),
            'background': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.add_input(Submit('submit', 'Register Agency', css_class='btn btn-primary'))
    
    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data