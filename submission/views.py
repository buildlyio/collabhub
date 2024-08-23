from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .models import SubmissionLink, Submission
from .forms import SubmissionForm
import qrcode
from django.conf import settings


import io
import os
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile


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
    qr.add_data(submission_link.unique_url)
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
