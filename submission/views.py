from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .models import SubmissionLink, Submission, User
from onboarding.models import TeamMember
from .forms import SubmissionForm
import qrcode
from django.conf import settings

import io
import os
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from onboarding.models import TeamMemberResource
from django import template


@login_required
def generate_link(request):
    # Create the submission link
    submission_link = SubmissionLink.objects.create(admin_user=request.user)
    
    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(f'{settings.BASE_URL}/submission/submit/{submission_link.unique_url}')
    qr.make(fit=True)

    img = qr.make_image(fill='black', back_color='white')

    # Use in-memory file to store the QR code
    image_io = io.BytesIO()
    img.save(image_io, format='PNG')
    image_io.seek(0)  # Go to the start of the BytesIO object

    # Define the path within the S3 bucket
    filename = f'qr_codes/{submission_link.unique_url}.png'
    
    # Save the image to S3
    file_content = ContentFile(image_io.getvalue())
    file_url = default_storage.save(filename, file_content)

    # Store the S3 URL in the database
    submission_link.qr_code = default_storage.url(filename)
    submission_link.save()
    
    team_member_profile = get_object_or_404(TeamMember, user=request.user)

    return render(request, 'link_generated.html', {'submission_link': submission_link,'team_member_profile': team_member_profile})

@login_required
def delete_submission_link(request, unique_url):
    submission_link = get_object_or_404(SubmissionLink, id=unique_url)
    
    # Delete the QR code from S3
    if submission_link.qr_code:
        file_path = submission_link.qr_code.replace(settings.MEDIA_URL, '')
        default_storage.delete(file_path)
    
    # Delete the submission link
    submission_link.delete()
    
    return redirect('dashboard')  # Replace 'some_view_name' with the name of the view you want to redirect to

def submission_form(request, unique_url):
    submission_link = get_object_or_404(SubmissionLink, unique_url=unique_url)
    team_member_profile = get_object_or_404(TeamMember, user=submission_link.admin_user)
    if request.method == 'POST':
        form = SubmissionForm(request.POST)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.submission_link = submission_link
            submission.save()
            return HttpResponse('Thank you! Submission successful.')
    else:
        form = SubmissionForm()

    return render(request, 'submission_form.html', {'form': form, 'team_member_profile': team_member_profile, 'submission_link': submission_link})

@csrf_exempt
@login_required
@require_POST
def update_resource_progress(request):
    resource_id = int(request.POST.get('resource_id'))
    progress = int(request.POST.get('progress'))

    try:
        team_member = get_object_or_404(TeamMember, user=request.user)
        team_member_resource, created = TeamMemberResource.objects.get_or_create(
            team_member=team_member,
            resource_id=resource_id,
            defaults={'progress': progress}
        )
        if not created:
            team_member_resource.progress = progress
            team_member_resource.save()

        return JsonResponse({'success': True, 'created': created})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    

register = template.Library()

@register.simple_tag
def get_resource_progress(resource_id):
    if not resource_id:
        return 'Invalid data'

    try:
        team_member_resource = TeamMemberResource.objects.get(
            resource_id=resource_id,
        )
        return team_member_resource.progress
    except TeamMemberResource.DoesNotExist:
        return 'Resource not found'
    except Exception as e:
        return str(e)