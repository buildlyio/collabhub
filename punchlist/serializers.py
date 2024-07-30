from rest_framework import serializers
from .models import *

class PositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Position
        fields = '__all__'

class BugSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bug
        fields = '__all__'

class PunchlistSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PunchlistSubmission
        fields = '__all__'

class PunchlistSetterSerializer(serializers.ModelSerializer):
    class Meta:
        model = PunchlistSetter
        fields = '__all__'

class PunchlistHunterSerializer(serializers.ModelSerializer):
    class Meta:
        model = PunchlistHunter
        fields = '__all__'

class PunchlistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Punchlist
        fields = '__all__'

class IssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Issue
        fields = '__all__'

class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = '__all__'

class AcceptedPunchlistSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcceptedPunchlist
        fields = '__all__'

class ContractSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contract
        fields = '__all__'

class DevelopmentAgencySerializer(serializers.ModelSerializer):
    class Meta:
        model = DevelopmentAgency
        fields = '__all__'
