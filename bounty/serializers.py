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

class BountySubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = BountySubmission
        fields = '__all__'

class BountySetterSerializer(serializers.ModelSerializer):
    class Meta:
        model = BountySetter
        fields = '__all__'

class BountyHunterSerializer(serializers.ModelSerializer):
    class Meta:
        model = BountyHunter
        fields = '__all__'

class BountySerializer(serializers.ModelSerializer):
    class Meta:
        model = Bounty
        fields = '__all__'

class IssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Issue
        fields = '__all__'

class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = '__all__'

class AcceptedBountySerializer(serializers.ModelSerializer):
    class Meta:
        model = AcceptedBounty
        fields = '__all__'

class ContractSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contract
        fields = '__all__'

class DevelopmentAgencySerializer(serializers.ModelSerializer):
    class Meta:
        model = DevelopmentAgency
        fields = '__all__'
