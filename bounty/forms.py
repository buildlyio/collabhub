from .models import BountyHunter, Bounty, Issue, BountySetter
from crispy_forms.helper import FormHelper
from crispy_forms.layout import *
from crispy_forms.bootstrap import *
from crispy_forms.layout import Layout, Submit, Reset, Div
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

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        # get rid of extra keywords before calling super
        self.request = kwargs.pop('request')
        # call super to get form fields
        super(BountyHunterForm, self).__init__(*args, **kwargs)
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
        fields = ('title', 'description', 'tags', 'hosting', 'complexity_estimate', 'repo',)
        
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
                    Field('title'),
                    Field('description'),
                    Field('tags'),
                    Field('hosting'),
                    Field('complexity_estimate'),
                    Field('repo'),
                ),
                Tab('Issues',
                    Field('issue_search', css_class="form-control"),
                    Div('issue_title', 'issue_description', 'issue_language', 'issue_framework', 'issue_github_link', css_class="search-results")
                ),
            ),
        )

    issue_title = forms.CharField(required=False)
    issue_description = forms.CharField(required=False)
    issue_language = forms.CharField(required=False)
    issue_framework = forms.CharField(required=False)
    issue_github_link = forms.URLField(required=False)

    def clean(self):
        cleaned_data = super().clean()
        repo = cleaned_data.get('repo')
        repo_owner = cleaned_data.get('repo_owner')
        repo_access_token = cleaned_data.get('repo_access_token')
        issue_search = cleaned_data.get('issue_search')

        if repo and repo_owner and repo_access_token and issue_search:
            issues = search_issues(repo, repo_owner, repo_access_token, issue_search)
            if issues:
                issue = issues[0]
                cleaned_data['issue_title'] = issue.title
                cleaned_data['issue_description'] = issue.body
                cleaned_data['issue_github_link'] = issue.html_url

        return cleaned_data

class IssueForm(forms.ModelForm):
    class Meta:
        model = Issue
        fields = ['title', 'description', 'language', 'framework', 'issue_url']
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