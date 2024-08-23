from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .models import SubmissionLink, Submission
from .forms import SubmissionForm
import qrcode
from django.conf import settings

import os

@login_required
def generate_link(request):
    submission_link = SubmissionLink.objects.create(admin_user=request.user)
    
    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(submission_link.unique_url)
    qr.make(fit=True)

    img = qr.make_image(fill='black', back_color='white')
    # Define the directory path for QR codes
    qr_code_dir = os.path.join(settings.MEDIA_ROOT, 'qr_codes')
    # Ensure the directory exists
    os.makedirs(qr_code_dir, exist_ok=True)
    img_path = settings.MEDIA_URL + f'qr_codes/{submission_link.unique_url}.png'
    img.save(img_path)

    submission_link.qr_code = img_path
    submission_link.save()

    return render(request, 'submission/link_generated.html', {'submission_link': submission_link})

def submission_form(request, unique_url):
    submission_link = get_object_or_404(SubmissionLink, unique_url=unique_url)
    if request.method == 'POST':
        form = SubmissionForm(request.POST)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.submission_link = submission_link
            submission.save()
            return HttpResponse('Submission successful.')
    else:
        form = SubmissionForm()

    return render(request, 'submission/submission_form.html', {'form': form})
