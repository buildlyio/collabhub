from rest_framework import generics
from .models import *
from .serializers import *
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated


class PositionList(generics.ListCreateAPIView):
    queryset = Position.objects.all()
    serializer_class = PositionSerializer

class PositionDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Position.objects.all()
    serializer_class = PositionSerializer

class BugList(generics.ListCreateAPIView):
    queryset = Bug.objects.all()
    serializer_class = BugSerializer

class BugDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Bug.objects.all()
    serializer_class = BugSerializer

class BountySubmissionList(generics.ListCreateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    queryset = BountySubmission.objects.all()
    serializer_class = BountySubmissionSerializer

class BountySubmissionDetail(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    queryset = BountySubmission.objects.all()
    serializer_class = BountySubmissionSerializer

class BountySetterList(generics.ListCreateAPIView):
    queryset = BountySetter.objects.all()
    serializer_class = BountySetterSerializer

class BountySetterDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = BountySetter.objects.all()
    serializer_class = BountySetterSerializer

class BountyHunterList(generics.ListCreateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    queryset = BountyHunter.objects.all()
    serializer_class = BountyHunterSerializer

class BountyHunterDetail(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    queryset = BountyHunter.objects.all()
    serializer_class = BountyHunterSerializer

class BountyList(generics.ListCreateAPIView):
    queryset = Bounty.objects.all()
    serializer_class = BountySerializer

class BountyDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Bounty.objects.all()
    serializer_class = BountySerializer

class IssueList(generics.ListCreateAPIView):
    queryset = Issue.objects.all()
    serializer_class = IssueSerializer

class IssueDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Issue.objects.all()
    serializer_class = IssueSerializer

class PlanList(generics.ListCreateAPIView):
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer

class PlanDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer

class AcceptedBountyList(generics.ListCreateAPIView):
    queryset = AcceptedBounty.objects.all()
    serializer_class = AcceptedBountySerializer

class AcceptedBountyDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = AcceptedBounty.objects.all()
    serializer_class = AcceptedBountySerializer

class ContractList(generics.ListCreateAPIView):
    queryset = Contract.objects.all()
    serializer_class = ContractSerializer

class ContractDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Contract.objects.all()
    serializer_class = ContractSerializer

class DevelopmentAgencyList(generics.ListCreateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    queryset = DevelopmentAgency.objects.all()
    serializer_class = DevelopmentAgencySerializer

class DevelopmentAgencyDetail(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    queryset = DevelopmentAgency.objects.all()
    serializer_class = DevelopmentAgencySerializer
