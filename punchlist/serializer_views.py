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

class PunchlistSubmissionList(generics.ListCreateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    queryset = PunchlistSubmission.objects.all()
    serializer_class = PunchlistSubmissionSerializer

class PunchlistSubmissionDetail(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    queryset = PunchlistSubmission.objects.all()
    serializer_class = PunchlistSubmissionSerializer

class PunchlistSetterList(generics.ListCreateAPIView):
    queryset = PunchlistSetter.objects.all()
    serializer_class = PunchlistSetterSerializer

class PunchlistSetterDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = PunchlistSetter.objects.all()
    serializer_class = PunchlistSetterSerializer

class PunchlistHunterList(generics.ListCreateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    queryset = PunchlistHunter.objects.all()
    serializer_class = PunchlistHunterSerializer

class PunchlistHunterDetail(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    queryset = PunchlistHunter.objects.all()
    serializer_class = PunchlistHunterSerializer

class PunchlistList(generics.ListCreateAPIView):
    queryset = Punchlist.objects.all()
    serializer_class = PunchlistSerializer

class PunchlistDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Punchlist.objects.all()
    serializer_class = PunchlistSerializer

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

class AcceptedPunchlistList(generics.ListCreateAPIView):
    queryset = AcceptedPunchlist.objects.all()
    serializer_class = AcceptedPunchlistSerializer

class AcceptedPunchlistDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = AcceptedPunchlist.objects.all()
    serializer_class = AcceptedPunchlistSerializer

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
