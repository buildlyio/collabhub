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

# Training Section Serializers
class SectionResourceSerializer(serializers.ModelSerializer):
    """Serializer for resources within a training section"""
    video_embed_html = serializers.SerializerMethodField()
    has_video = serializers.SerializerMethodField()
    
    class Meta:
        model = SectionResource
        fields = [
            'id', 'title', 'description', 'order',
            'link', 'document',
            'video_source', 'video_url', 'video_embed_code', 'video_duration_minutes',
            'video_embed_html', 'has_video',
            'estimated_time_minutes', 'is_required', 'is_active',
            'created_at', 'updated_at'
        ]
    
    def get_video_embed_html(self, obj):
        return obj.get_video_embed_html()
    
    def get_has_video(self, obj):
        return obj.has_video()


class TrainingSectionSerializer(serializers.ModelSerializer):
    """Serializer for training sections with nested resources"""
    section_resources = SectionResourceSerializer(many=True, read_only=True)
    total_resources = serializers.SerializerMethodField()
    is_available = serializers.SerializerMethodField()
    is_overdue = serializers.SerializerMethodField()
    days_until_due = serializers.SerializerMethodField()
    quizzes = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    
    class Meta:
        model = TrainingSection
        fields = [
            'id', 'training', 'name', 'description', 'order',
            'start_date', 'end_date',
            'quizzes', 'section_resources',
            'total_resources', 'is_available', 'is_overdue', 'days_until_due',
            'is_active', 'created_at', 'updated_at'
        ]
    
    def get_total_resources(self, obj):
        return obj.total_resources()
    
    def get_is_available(self, obj):
        return obj.is_available()
    
    def get_is_overdue(self, obj):
        return obj.is_overdue()
    
    def get_days_until_due(self, obj):
        return obj.days_until_due()


class TrainingSectionCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating training sections"""
    class Meta:
        model = TrainingSection
        fields = [
            'id', 'training', 'name', 'description', 'order',
            'start_date', 'end_date', 'quizzes', 'is_active'
        ]


class ResourceProgressSerializer(serializers.ModelSerializer):
    """Serializer for tracking resource completion"""
    resource_title = serializers.CharField(source='resource.title', read_only=True)
    
    class Meta:
        model = ResourceProgress
        fields = [
            'id', 'section_progress', 'resource', 'resource_title',
            'is_completed', 'completed_at', 'time_spent_minutes', 'notes'
        ]


class SectionProgressSerializer(serializers.ModelSerializer):
    """Serializer for tracking section progress"""
    section_name = serializers.CharField(source='section.name', read_only=True)
    resource_progress = ResourceProgressSerializer(many=True, read_only=True)
    resources_completed = serializers.SerializerMethodField()
    resources_total = serializers.SerializerMethodField()
    progress_percent = serializers.SerializerMethodField()
    quizzes_passed = serializers.SerializerMethodField()
    
    class Meta:
        model = SectionProgress
        fields = [
            'id', 'enrollment', 'section', 'section_name', 'status',
            'started_at', 'completed_at',
            'resource_progress', 'resources_completed', 'resources_total',
            'progress_percent', 'quizzes_passed'
        ]
    
    def get_resources_completed(self, obj):
        return obj.resources_completed()
    
    def get_resources_total(self, obj):
        return obj.resources_total()
    
    def get_progress_percent(self, obj):
        return obj.progress_percent()
    
    def get_quizzes_passed(self, obj):
        return obj.quizzes_passed()


class TeamTrainingDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for team training with sections"""
    sections = TrainingSectionSerializer(many=True, read_only=True)
    total_sections = serializers.SerializerMethodField()
    
    class Meta:
        model = TeamTraining
        fields = [
            'id', 'customer', 'developer_team', 'name', 'description',
            'sections', 'total_sections',
            'quiz', 'is_active', 'created_by', 'created_at'
        ]
    
    def get_total_sections(self, obj):
        return obj.sections.count()