#!/usr/bin/env python
"""
Seed script to create certification tracks and the CTO/Lead composite certification.
Run with: python manage.py shell < scripts/seed_certifications.py
Or: python manage.py runscript seed_certifications (if using django-extensions)
"""
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
django.setup()

from onboarding.models import CertificationTrack, CompositeCertification, CommunityBadge

def seed_tracks():
    """Create certification tracks if they don't exist"""
    
    tracks_data = [
        {
            'key': 'frontend',
            'name': 'Frontend Developer',
            'description': 'Master modern frontend development with React, TypeScript, and UI/UX best practices.',
            'icon': '🎨',
            'color': '#3B82F6',  # Blue
            'order': 1,
        },
        {
            'key': 'backend',
            'name': 'Backend Developer',
            'description': 'Build robust APIs, microservices, and scalable backend systems.',
            'icon': '⚙️',
            'color': '#10B981',  # Green
            'order': 2,
        },
        {
            'key': 'product_manager',
            'name': 'Product Manager',
            'description': 'Lead product development using RAD methodology and agile practices.',
            'icon': '📊',
            'color': '#8B5CF6',  # Purple
            'order': 3,
        },
        {
            'key': 'ai',
            'name': 'AI/ML Developer',
            'description': 'Develop AI-powered applications, machine learning models, and intelligent systems.',
            'icon': '🤖',
            'color': '#F97316',  # Orange
            'order': 4,
        },
        {
            'key': 'ai_ethics',
            'name': 'AI Ethical Developer',
            'description': 'Build responsible AI systems with ethical considerations, bias mitigation, and transparency.',
            'icon': '⚖️',
            'color': '#06B6D4',  # Cyan
            'order': 5,
        },
        {
            'key': 'leadership',
            'name': 'Leadership',
            'description': 'Lead development teams, manage technical projects, and drive engineering culture.',
            'icon': '👔',
            'color': '#EF4444',  # Red
            'order': 6,
        },
    ]
    
    created_count = 0
    for track_data in tracks_data:
        track, created = CertificationTrack.objects.update_or_create(
            key=track_data['key'],
            defaults=track_data
        )
        if created:
            created_count += 1
            print(f"Created track: {track.name}")
        else:
            print(f"Updated track: {track.name}")
    
    print(f"\nTotal tracks created: {created_count}")
    return CertificationTrack.objects.all()


def seed_composite_certifications():
    """Create composite certifications like CTO/Lead"""
    
    # Get leadership track (required for CTO/Lead)
    try:
        leadership_track = CertificationTrack.objects.get(key='leadership')
    except CertificationTrack.DoesNotExist:
        print("ERROR: Leadership track not found. Run seed_tracks() first.")
        return
    
    # Create CTO/Lead Composite Certification
    cto_cert, created = CompositeCertification.objects.update_or_create(
        key='cto_lead',
        defaults={
            'name': 'CTO/Lead Certification',
            'description': (
                'The CTO/Lead Certification recognizes developers who have demonstrated '
                'senior-level expertise across multiple technical domains combined with '
                'strong leadership skills. Recipients have proven their ability to lead '
                'teams, architect systems, and drive technical excellence.\n\n'
                'Requirements:\n'
                '• Level 3 (Senior) certification in Leadership track\n'
                '• Level 3 (Senior) certification in at least 2 additional technical tracks\n'
                '• Minimum of 3 total Level 3 certifications'
            ),
            'min_level': 3,
            'min_total_tracks': 3,
            'icon': '👑',
            'color': '#F59E0B',  # Amber/Gold
            'badge_color': '#F59E0B',
            'certificate_template': 'cto_lead',
            'is_active': True,
            'order': 1,
        }
    )
    
    # Add Leadership as required track
    cto_cert.required_tracks.add(leadership_track)
    
    if created:
        print(f"Created composite certification: {cto_cert.name}")
    else:
        print(f"Updated composite certification: {cto_cert.name}")
    
    return cto_cert


def seed_community_badges():
    """Create community badges for AI and Leadership tracks"""
    
    badges_data = [
        {
            'key': 'ai_developer_l1',
            'name': 'AI Developer - Foundation',
            'description': 'Completed AI Developer Level 1 certification. Understands ML fundamentals and AI tool usage.',
            'badge_type': 'achievement',
            'icon': '🤖',
            'color': '#F97316',
            'order': 10,
        },
        {
            'key': 'ai_developer_l2',
            'name': 'AI Developer - Practitioner',
            'description': 'Completed AI Developer Level 2 certification. Can build and deploy AI/ML applications.',
            'badge_type': 'achievement',
            'icon': '🧠',
            'color': '#F97316',
            'order': 11,
        },
        {
            'key': 'ai_developer_l3',
            'name': 'AI Developer - Senior',
            'description': 'Completed AI Developer Level 3 certification. Expert in AI systems architecture and advanced ML.',
            'badge_type': 'achievement',
            'icon': '🔮',
            'color': '#F97316',
            'order': 12,
        },
        {
            'key': 'ai_ethics_l1',
            'name': 'AI Ethics - Foundation',
            'description': 'Completed AI Ethical Developer Level 1. Understands ethical AI principles and bias awareness.',
            'badge_type': 'achievement',
            'icon': '⚖️',
            'color': '#06B6D4',
            'order': 13,
        },
        {
            'key': 'ai_ethics_l2',
            'name': 'AI Ethics - Practitioner',
            'description': 'Completed AI Ethical Developer Level 2. Can implement fair and transparent AI systems.',
            'badge_type': 'achievement',
            'icon': '🛡️',
            'color': '#06B6D4',
            'order': 14,
        },
        {
            'key': 'ai_ethics_l3',
            'name': 'AI Ethics - Senior',
            'description': 'Completed AI Ethical Developer Level 3. Expert in responsible AI governance and audit.',
            'badge_type': 'achievement',
            'icon': '🏛️',
            'color': '#06B6D4',
            'order': 15,
        },
        {
            'key': 'leadership_l1',
            'name': 'Leadership - Foundation',
            'description': 'Completed Leadership Level 1. Understands team dynamics and basic management principles.',
            'badge_type': 'leadership',
            'icon': '📋',
            'color': '#EF4444',
            'order': 16,
        },
        {
            'key': 'leadership_l2',
            'name': 'Leadership - Practitioner',
            'description': 'Completed Leadership Level 2. Can lead small teams and manage technical projects.',
            'badge_type': 'leadership',
            'icon': '🎯',
            'color': '#EF4444',
            'order': 17,
        },
        {
            'key': 'leadership_l3',
            'name': 'Leadership - Senior',
            'description': 'Completed Leadership Level 3. Expert in engineering management and organizational leadership.',
            'badge_type': 'leadership',
            'icon': '👔',
            'color': '#EF4444',
            'order': 18,
        },
        {
            'key': 'cto_lead',
            'name': 'CTO/Lead',
            'description': 'Achieved CTO/Lead status with Level 3 in Leadership and 2+ additional tracks. Ready to lead engineering organizations.',
            'badge_type': 'leadership',
            'icon': '👑',
            'color': '#F59E0B',
            'order': 100,
        },
    ]
    
    created_count = 0
    for badge_data in badges_data:
        badge, created = CommunityBadge.objects.update_or_create(
            key=badge_data['key'],
            defaults=badge_data
        )
        if created:
            created_count += 1
            print(f"Created badge: {badge.name}")
        else:
            print(f"Updated badge: {badge.name}")
    
    print(f"\nTotal badges created: {created_count}")


if __name__ == '__main__':
    print("=" * 60)
    print("Seeding Certification Tracks")
    print("=" * 60)
    seed_tracks()
    
    print("\n" + "=" * 60)
    print("Seeding Composite Certifications")
    print("=" * 60)
    seed_composite_certifications()
    
    print("\n" + "=" * 60)
    print("Seeding Community Badges")
    print("=" * 60)
    seed_community_badges()
    
    print("\n" + "=" * 60)
    print("DONE!")
    print("=" * 60)
