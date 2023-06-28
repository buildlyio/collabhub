from .models import BountyHunter, Bounty, Issue, BountySetter, Bug
from crispy_forms.helper import FormHelper
from crispy_forms.layout import *
from crispy_forms.bootstrap import *
from crispy_forms.layout import Layout, Submit, Reset, Div, HTML, Fieldset, Field
from functools import partial
from django import forms
from django.urls import reverse
from bounty.github_issues import search_issues

import os

import requests

# Hunter Forms
class BountyHunterForm(forms.ModelForm):
    brief = forms.FileField(required=False,
        label="Upload a file",
        help_text="Select a PDF or DOC file to upload.",
    )

    class Meta:
        model = BountyHunter
        exclude = ['create_date','edit_date']
        widgets = {'comments': forms.Textarea(attrs={'rows':4}),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        # call super to get form fields
        super(BountyHunterForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_id = 'hunter_update_form'
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-sm-2'
        self.helper.field_class = 'col-sm-6'
        self.helper.form_error_title = 'Form Errors'
        self.helper.error_text_inline = True
        self.helper.help_text_inline = True
        self.helper.html5_required = True
        self.helper.layout = Layout(

            HTML("""<br/>"""),
            TabHolder(
                Tab('Position Description',
                     Fieldset('',
                        'name','level','skills','description','resume','status','language','location','remote'
                        ),
                ),

                HTML("""<br/>"""),
                FormActions(
                    Submit('submit', 'Save', css_class='btn-default'),
                    Reset('reset', 'Reset', css_class='btn-warning')
                ),
             ),
        )
        self.fields['owner'].initial = self.request.user
        super(BountyHunterForm, self).__init__(*args, **kwargs)


class BountyForm(forms.ModelForm):

    class Meta:
        model = Bounty
        fields = ('catagory','title', 'description','skills','level','brief','amount', 'tags', 'hosting', 'complexity_estimate', 'repo','owner')
        
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        # call super to get form fields
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Submit'))
        self.helper.layout = Layout(
            TabHolder(
                Tab('Bounty',
                    Field('catagory'),
                    Field('title'),
                    Field('description'),
                    Field('skills'),
                    Field('level'),
                    Field('amount'),
                    Field('brief'),
                    Field('tags'),
                    Field('hosting'),
                    Field('complexity_estimate'),
                    Field('repo'),
                ),
                Tab('GitHub Issue',
                    Div('issue_title', 'issue_description', 'issue_language', 'issue_framework', 'issue_github_link', 'issue_screenshot')
                ),
            ),
        )

    issue_title = forms.CharField(required=False)
    issue_description = forms.CharField(required=False)
    issue_language = forms.CharField(required=False)
    issue_framework = forms.CharField(required=False)
    issue_github_link = forms.URLField(required=False)
    issue_screenshot = forms.URLField(required=False)

    def clean(self):
        cleaned_data = super().clean()

        return cleaned_data

class IssueForm(forms.ModelForm):
    class Meta:
        model = Issue
        fields = ['title', 'description', 'language', 'framework', 'issue_url','screenshot']
        widgets = {'issue_url': forms.HiddenInput()}

    

from .models import BountySubmission

class BountyHunterSubmissionForm(forms.ModelForm):
    class Meta:
        model = BountySubmission
        fields = ['bounty_hunter']

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.bounty = self.request.bounty
        instance.bounty_hunter = self.request.user.bountyhunter
        if commit:
            instance.save()
        return instance


class BountyHunterForm(forms.ModelForm):
    class Meta:
        model = BountyHunter
        fields = '__all__'


class BountySetterForm(forms.ModelForm):
    class Meta:
        model = BountySetter
        fields = '__all__'



class BugForm(forms.ModelForm):
    class Meta:
        model = Bug
        fields = ['url', 'notes', 'error_message', 'severity', 'name', 'email', 'description', 'steps_to_reproduce', 'screenshots']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.add_input(Submit('submit', 'Submit'))