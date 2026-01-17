from django.core.management.base import BaseCommand
from onboarding.models import CertificationTrack, CompositeCertification, CommunityBadge


class Command(BaseCommand):
    help = 'Seed certification tracks, badges, and composite certifications'

    def handle(self, *args, **options):
        self.stdout.write("=" * 60)
        self.stdout.write("Seeding Certification Tracks...")
        self.stdout.write("=" * 60)
        
        # Seed tracks
        tracks_data = [
            {'key': 'frontend', 'name': 'Frontend Developer', 
             'description': 'Master modern frontend development with React, TypeScript, and UI/UX best practices.', 
             'icon': '🎨', 'color': '#3B82F6', 'order': 1},
            {'key': 'backend', 'name': 'Backend Developer', 
             'description': 'Build robust APIs, microservices, and scalable backend systems.', 
             'icon': '⚙️', 'color': '#10B981', 'order': 2},
            {'key': 'product_manager', 'name': 'Product Manager', 
             'description': 'Lead product development using RAD methodology and agile practices.', 
             'icon': '📊', 'color': '#8B5CF6', 'order': 3},
            {'key': 'ai', 'name': 'AI/ML Developer', 
             'description': 'Develop AI-powered applications, machine learning models, and intelligent systems.', 
             'icon': '🤖', 'color': '#F97316', 'order': 4},
            {'key': 'ai_ethics', 'name': 'AI Ethical Developer', 
             'description': 'Build responsible AI systems with ethical considerations, bias mitigation, and transparency.', 
             'icon': '⚖️', 'color': '#06B6D4', 'order': 5},
            {'key': 'leadership', 'name': 'Leadership', 
             'description': 'Lead development teams, manage technical projects, and drive engineering culture.', 
             'icon': '👔', 'color': '#EF4444', 'order': 6},
        ]
        
        for td in tracks_data:
            track, created = CertificationTrack.objects.update_or_create(key=td['key'], defaults=td)
            status = 'Created' if created else 'Updated'
            self.stdout.write(f"  {status} track: {track.name}")
        
        self.stdout.write("")
        self.stdout.write("=" * 60)
        self.stdout.write("Seeding CTO/Lead Composite Certification...")
        self.stdout.write("=" * 60)
        
        # Create CTO/Lead composite certification
        leadership = CertificationTrack.objects.get(key='leadership')
        cto, created = CompositeCertification.objects.update_or_create(
            key='cto_lead',
            defaults={
                'name': 'CTO/Lead Certification',
                'description': (
                    'The CTO/Lead Certification recognizes developers who have demonstrated '
                    'senior-level expertise across multiple technical domains combined with '
                    'strong leadership skills.\n\n'
                    'Requirements:\n'
                    '• Level 3 (Senior) certification in Leadership track\n'
                    '• Level 3 (Senior) certification in at least 2 additional tracks\n'
                    '• Minimum of 3 total Level 3 certifications'
                ),
                'min_level': 3,
                'min_total_tracks': 3,
                'icon': '👑',
                'color': '#F59E0B',
                'badge_color': '#F59E0B',
                'certificate_template': 'cto_lead',
                'is_active': True,
                'order': 1,
            }
        )
        cto.required_tracks.add(leadership)
        status = 'Created' if created else 'Updated'
        self.stdout.write(f"  {status} CTO/Lead certification")
        
        self.stdout.write("")
        self.stdout.write("=" * 60)
        self.stdout.write("Seeding Community Badges...")
        self.stdout.write("=" * 60)
        
        # Create badges
        badges_data = [
            {'key': 'ai_developer_l1', 'name': 'AI Developer - Foundation', 
             'description': 'Completed AI Developer Level 1 certification. Understands ML fundamentals and AI tool usage.',
             'badge_type': 'achievement', 'icon': '🤖', 'color': '#F97316', 'order': 10},
            {'key': 'ai_developer_l2', 'name': 'AI Developer - Practitioner', 
             'description': 'Completed AI Developer Level 2 certification. Can build and deploy AI/ML applications.',
             'badge_type': 'achievement', 'icon': '🧠', 'color': '#F97316', 'order': 11},
            {'key': 'ai_developer_l3', 'name': 'AI Developer - Senior', 
             'description': 'Completed AI Developer Level 3 certification. Expert in AI systems architecture and advanced ML.',
             'badge_type': 'achievement', 'icon': '🔮', 'color': '#F97316', 'order': 12},
            {'key': 'ai_ethics_l1', 'name': 'AI Ethics - Foundation', 
             'description': 'Completed AI Ethical Developer Level 1. Understands ethical AI principles and bias awareness.',
             'badge_type': 'achievement', 'icon': '⚖️', 'color': '#06B6D4', 'order': 13},
            {'key': 'ai_ethics_l2', 'name': 'AI Ethics - Practitioner', 
             'description': 'Completed AI Ethical Developer Level 2. Can implement fair and transparent AI systems.',
             'badge_type': 'achievement', 'icon': '🛡️', 'color': '#06B6D4', 'order': 14},
            {'key': 'ai_ethics_l3', 'name': 'AI Ethics - Senior', 
             'description': 'Completed AI Ethical Developer Level 3. Expert in responsible AI governance and audit.',
             'badge_type': 'achievement', 'icon': '🏛️', 'color': '#06B6D4', 'order': 15},
            {'key': 'leadership_l1', 'name': 'Leadership - Foundation', 
             'description': 'Completed Leadership Level 1. Understands team dynamics and basic management principles.',
             'badge_type': 'leadership', 'icon': '📋', 'color': '#EF4444', 'order': 16},
            {'key': 'leadership_l2', 'name': 'Leadership - Practitioner', 
             'description': 'Completed Leadership Level 2. Can lead small teams and manage technical projects.',
             'badge_type': 'leadership', 'icon': '🎯', 'color': '#EF4444', 'order': 17},
            {'key': 'leadership_l3', 'name': 'Leadership - Senior', 
             'description': 'Completed Leadership Level 3. Expert in engineering management and organizational leadership.',
             'badge_type': 'leadership', 'icon': '👔', 'color': '#EF4444', 'order': 18},
            {'key': 'cto_lead', 'name': 'CTO/Lead', 
             'description': 'Achieved CTO/Lead status with Level 3 in Leadership and 2+ additional tracks. Ready to lead engineering organizations.',
             'badge_type': 'leadership', 'icon': '👑', 'color': '#F59E0B', 'order': 100},
        ]
        
        for bd in badges_data:
            badge, created = CommunityBadge.objects.update_or_create(key=bd['key'], defaults=bd)
            status = 'Created' if created else 'Updated'
            self.stdout.write(f"  {status} badge: {badge.name}")
        
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("=" * 60))
        self.stdout.write(self.style.SUCCESS("DONE! All certifications and badges seeded."))
        self.stdout.write(self.style.SUCCESS("=" * 60))
