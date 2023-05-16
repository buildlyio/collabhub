from django_filters import FilterSet, RangeFilter, CharFilter
from .models import Issue, Bounty


class IssueFilter(FilterSet):
    tags = CharFilter(field_name='tags', lookup_expr='icontains')
    language = CharFilter(field_name='language', lookup_expr='icontains')
    framework = CharFilter(field_name='framework', lookup_expr='icontains')
    hosting_environment = CharFilter(field_name='hosting_environment', lookup_expr='icontains')
    complexity = RangeFilter()

    class Meta:
        model = Issue
        fields = ['tags', 'language', 'framework', 'hosting_environment', 'complexity']


class IssueFilter(FilterSet):
    language = CharFilter(lookup_expr='icontains')
    framework = CharFilter(lookup_expr='icontains')

    class Meta:
        model = Issue
        fields = ['language', 'framework']


class BountyFilter(FilterSet):
    tags = CharFilter(lookup_expr='icontains')
    title = CharFilter(lookup_expr='icontains')
    description = CharFilter(lookup_expr='icontains')

    class Meta:
        model = Bounty
        fields = ['tags', 'title', 'description']
