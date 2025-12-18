"""
PDF and PNG generation for contracts and certificates with hash verification
"""
import io
import os
from datetime import datetime
from django.conf import settings
from django.core.files.base import ContentFile
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from PIL import Image, ImageDraw, ImageFont
import qrcode


def generate_contract_pdf(contract):
    """
    Generate a PDF for a signed contract with hash verification
    Returns the file content
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.75*inch, bottomMargin=1*inch)
    
    # Container for document elements
    elements = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1F2937'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#3B82F6'),
        spaceAfter=12,
        fontName='Helvetica-Bold'
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['BodyText'],
        fontSize=11,
        leading=14,
        textColor=colors.HexColor('#374151')
    )
    
    # Title
    elements.append(Paragraph(contract.title, title_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Contract metadata
    metadata = [
        ['Contract Type:', contract.get_contract_type_display()],
        ['Customer:', contract.customer.company_name],
        ['Start Date:', contract.start_date.strftime('%B %d, %Y')],
        ['End Date:', contract.end_date.strftime('%B %d, %Y')],
        ['Status:', contract.get_status_display()],
    ]
    
    if contract.signed_at:
        metadata.append(['Signed On:', contract.signed_at.strftime('%B %d, %Y at %I:%M %p')])
        metadata.append(['Signed By:', contract.signed_by])
    
    metadata_table = Table(metadata, colWidths=[2*inch, 4*inch])
    metadata_table.setStyle(TableStyle([
        ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 10),
        ('FONT', (1, 0), (1, -1), 'Helvetica', 10),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#374151')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    
    elements.append(metadata_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Services & Fees
    if contract.line_items.exists():
        elements.append(Paragraph('Services & Fees', heading_style))
        elements.append(Spacer(1, 0.1*inch))
        
        line_items_data = [['Service', 'Description', 'Qty', 'Unit Price', 'Discount', 'Total', 'Billing']]
        
        for item in contract.line_items.all():
            line_items_data.append([
                item.get_service_type_display(),
                item.description,
                str(item.quantity),
                f'${item.unit_price}',
                f'{item.discount_percentage}%',
                f'${item.total}',
                item.get_billing_frequency_display()
            ])
        
        # Add total row
        total_amount = contract.total_amount
        line_items_data.append(['', '', '', '', '', f'${total_amount}', 'Total'])
        
        items_table = Table(line_items_data, colWidths=[1.2*inch, 1.5*inch, 0.5*inch, 0.8*inch, 0.7*inch, 0.8*inch, 0.8*inch])
        items_table.setStyle(TableStyle([
            # Header
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3B82F6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 9),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            
            # Body
            ('FONT', (0, 1), (-1, -2), 'Helvetica', 8),
            ('TEXTCOLOR', (0, 1), (-1, -2), colors.HexColor('#374151')),
            ('GRID', (0, 0), (-1, -2), 0.5, colors.HexColor('#E5E7EB')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
            
            # Total row
            ('FONT', (0, -1), (-1, -1), 'Helvetica-Bold', 10),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#F3F4F6')),
            ('ALIGN', (5, -1), (5, -1), 'RIGHT'),
        ]))
        
        elements.append(items_table)
        elements.append(Spacer(1, 0.3*inch))
    
    # Additional terms
    if contract.contract_text:
        elements.append(Paragraph('Additional Terms & Conditions', heading_style))
        elements.append(Spacer(1, 0.1*inch))
        
        # Split text into paragraphs
        for para in contract.contract_text.split('\n\n'):
            if para.strip():
                elements.append(Paragraph(para.strip(), body_style))
                elements.append(Spacer(1, 0.1*inch))
        
        elements.append(Spacer(1, 0.2*inch))
    
    # Signature section
    if contract.signed_at and contract.signature_data:
        elements.append(Paragraph('Digital Signature', heading_style))
        elements.append(Spacer(1, 0.1*inch))
        
        sig_data = [
            ['Signed By:', contract.signed_by],
            ['Date & Time:', contract.signed_at.strftime('%B %d, %Y at %I:%M %p %Z')],
            ['IP Address:', contract.signature_ip or 'Not recorded'],
        ]
        
        sig_table = Table(sig_data, colWidths=[1.5*inch, 4*inch])
        sig_table.setStyle(TableStyle([
            ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 10),
            ('FONT', (1, 0), (1, -1), 'Helvetica', 10),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#374151')),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        elements.append(sig_table)
        elements.append(Spacer(1, 0.2*inch))
    
    # Verification hash footer
    if contract.contract_hash:
        elements.append(Spacer(1, 0.3*inch))
        
        # Generate QR code for verification
        base_url = getattr(settings, 'BASE_URL', getattr(settings, 'SITE_URL', 'https://collabhub.buildly.io'))
        verification_url = f"{base_url}/onboarding/verify/contract/{contract.contract_hash}/"
        qr = qrcode.QRCode(version=1, box_size=3, border=2)
        qr.add_data(verification_url)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")
        
        # Save QR code to buffer
        qr_buffer = io.BytesIO()
        qr_img.save(qr_buffer, format='PNG')
        qr_buffer.seek(0)
        
        # Add verification section
        verify_style = ParagraphStyle(
            'Verify',
            parent=styles['BodyText'],
            fontSize=8,
            textColor=colors.HexColor('#6B7280'),
            alignment=TA_CENTER
        )
        
        hash_style = ParagraphStyle(
            'Hash',
            parent=styles['BodyText'],
            fontSize=7,
            textColor=colors.HexColor('#9CA3AF'),
            alignment=TA_CENTER,
            fontName='Courier'
        )
        
        elements.append(Paragraph('🔒 VERIFIED CONTRACT', verify_style))
        elements.append(Spacer(1, 0.05*inch))
        elements.append(Paragraph(f'Verification Hash: {contract.contract_hash}', hash_style))
        elements.append(Spacer(1, 0.05*inch))
        elements.append(Paragraph(f'Verify at: {verification_url}', verify_style))
    
    # Build PDF
    doc.build(elements)
    
    pdf_content = buffer.getvalue()
    buffer.close()
    
    return pdf_content


def generate_contract_png(contract):
    """
    Generate a PNG preview image of the contract (first page)
    """
    # First generate the PDF
    pdf_content = generate_contract_pdf(contract)
    
    # For now, create a simple image with contract info
    # In production, you'd convert PDF to image using pdf2image or similar
    width, height = 850, 1100
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)
    
    # Try to use a better font
    try:
        title_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 32)
        heading_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 20)
        body_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 14)
        small_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 10)
    except:
        title_font = heading_font = body_font = small_font = ImageFont.load_default()
    
    # Draw title
    y_pos = 50
    draw.text((width//2, y_pos), contract.title, fill='#1F2937', font=title_font, anchor='mt')
    
    # Draw metadata
    y_pos += 80
    draw.text((50, y_pos), f"Customer: {contract.customer.company_name}", fill='#374151', font=body_font)
    y_pos += 30
    draw.text((50, y_pos), f"Contract Type: {contract.get_contract_type_display()}", fill='#374151', font=body_font)
    y_pos += 30
    draw.text((50, y_pos), f"Period: {contract.start_date} to {contract.end_date}", fill='#374151', font=body_font)
    
    if contract.signed_at:
        y_pos += 40
        draw.text((50, y_pos), f"✓ Signed by {contract.signed_by}", fill='#059669', font=heading_font)
        y_pos += 30
        draw.text((50, y_pos), f"On {contract.signed_at.strftime('%B %d, %Y at %I:%M %p')}", fill='#6B7280', font=body_font)
    
    # Draw hash
    if contract.contract_hash:
        y_pos = height - 100
        draw.text((width//2, y_pos), "🔒 VERIFIED CONTRACT", fill='#3B82F6', font=heading_font, anchor='mt')
        y_pos += 30
        draw.text((width//2, y_pos), f"Hash: {contract.contract_hash[:32]}...", fill='#9CA3AF', font=small_font, anchor='mt')
    
    # Save to buffer
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    return buffer.getvalue()


def generate_certificate_pdf(developer_certification):
    """
    Generate a professional certificate PDF for a developer
    """
    buffer = io.BytesIO()
    
    # Create canvas
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    # Background color
    c.setFillColor(colors.HexColor('#F9FAFB'))
    c.rect(0, 0, width, height, fill=1, stroke=0)
    
    # Border
    c.setStrokeColor(colors.HexColor(developer_certification.certification_level.badge_color))
    c.setLineWidth(10)
    c.rect(20, 20, width-40, height-40, fill=0, stroke=1)
    
    # Inner border
    c.setStrokeColor(colors.HexColor('#E5E7EB'))
    c.setLineWidth(2)
    c.rect(40, 40, width-80, height-80, fill=0, stroke=1)
    
    # Title
    c.setFillColor(colors.HexColor('#1F2937'))
    c.setFont('Helvetica-Bold', 36)
    c.drawCentredString(width/2, height-120, 'CERTIFICATE OF COMPLETION')
    
    # Subtitle
    c.setFont('Helvetica', 16)
    c.setFillColor(colors.HexColor('#6B7280'))
    c.drawCentredString(width/2, height-160, 'This certifies that')
    
    # Developer name
    c.setFont('Helvetica-Bold', 32)
    c.setFillColor(colors.HexColor(developer_certification.certification_level.badge_color))
    dev_name = developer_certification.developer.user.get_full_name()
    c.drawCentredString(width/2, height-220, dev_name)
    
    # Achievement text
    c.setFont('Helvetica', 16)
    c.setFillColor(colors.HexColor('#6B7280'))
    c.drawCentredString(width/2, height-270, 'has successfully completed the requirements for')
    
    # Certification name
    c.setFont('Helvetica-Bold', 24)
    c.setFillColor(colors.HexColor('#1F2937'))
    cert_name = developer_certification.certification_level.name
    c.drawCentredString(width/2, height-320, cert_name)
    
    # Level badge
    c.setFont('Helvetica', 14)
    c.setFillColor(colors.HexColor(developer_certification.certification_level.badge_color))
    level_text = f"Level: {developer_certification.certification_level.get_level_type_display()}"
    c.drawCentredString(width/2, height-360, level_text)
    
    # Score if available
    if developer_certification.score:
        c.setFont('Helvetica', 12)
        c.setFillColor(colors.HexColor('#6B7280'))
        c.drawCentredString(width/2, height-390, f'Score: {developer_certification.score}%')
    
    # Issue date
    c.setFont('Helvetica', 12)
    c.setFillColor(colors.HexColor('#374151'))
    issue_date = developer_certification.issued_at.strftime('%B %d, %Y')
    c.drawCentredString(width/2, height-450, f'Issued on {issue_date}')
    
    # Certificate number
    c.setFont('Helvetica-Bold', 10)
    c.setFillColor(colors.HexColor('#9CA3AF'))
    c.drawCentredString(width/2, 140, f'Certificate No: {developer_certification.certificate_number}')
    
    # Verification hash
    if developer_certification.certificate_hash:
        c.setFont('Courier', 8)
        c.setFillColor(colors.HexColor('#9CA3AF'))
        c.drawCentredString(width/2, 120, f'Verification Hash: {developer_certification.certificate_hash[:48]}...')
        
        # QR Code for verification
        base_url = getattr(settings, 'BASE_URL', getattr(settings, 'SITE_URL', 'https://collabhub.buildly.io'))
        verification_url = f"{base_url}/onboarding/verify/certificate/{developer_certification.certificate_hash}/"
        qr = qrcode.QRCode(version=1, box_size=5, border=2)
        qr.add_data(verification_url)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")
        
        # Save QR to temp buffer
        qr_buffer = io.BytesIO()
        qr_img.save(qr_buffer, format='PNG')
        qr_buffer.seek(0)
        
        # Draw QR code
        from reportlab.lib.utils import ImageReader
        qr_image = ImageReader(qr_buffer)
        c.drawImage(qr_image, width-140, 60, width=80, height=80, mask='auto')
        
        c.setFont('Helvetica', 8)
        c.drawRightString(width-50, 45, 'Scan to verify')
    
    # Footer
    c.setFont('Helvetica', 10)
    c.setFillColor(colors.HexColor('#6B7280'))
    c.drawCentredString(width/2, 90, 'Buildly Inc. - Certified Developer Program')
    base_url = getattr(settings, 'BASE_URL', getattr(settings, 'SITE_URL', 'https://collabhub.buildly.io'))
    c.drawCentredString(width/2, 75, f'Verify at: {base_url}/onboarding/verify/')
    
    c.save()
    
    pdf_content = buffer.getvalue()
    buffer.close()
    
    return pdf_content


def generate_certificate_png(developer_certification):
    """
    Generate a PNG image of the certificate
    """
    width, height = 1200, 900
    img = Image.new('RGB', (width, height), color='#F9FAFB')
    draw = ImageDraw.Draw(img)
    
    # Border
    border_color = developer_certification.certification_level.badge_color
    draw.rectangle([10, 10, width-10, height-10], outline=border_color, width=15)
    draw.rectangle([30, 30, width-30, height-30], outline='#E5E7EB', width=3)
    
    # Fonts
    try:
        title_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 48)
        name_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 42)
        cert_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 32)
        body_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 20)
        small_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 14)
    except:
        title_font = name_font = cert_font = body_font = small_font = ImageFont.load_default()
    
    # Title
    y_pos = 100
    draw.text((width//2, y_pos), 'CERTIFICATE OF COMPLETION', fill='#1F2937', font=title_font, anchor='mt')
    
    # Subtitle
    y_pos += 80
    draw.text((width//2, y_pos), 'This certifies that', fill='#6B7280', font=body_font, anchor='mt')
    
    # Developer name
    y_pos += 60
    dev_name = developer_certification.developer.user.get_full_name()
    draw.text((width//2, y_pos), dev_name, fill=border_color, font=name_font, anchor='mt')
    
    # Achievement
    y_pos += 80
    draw.text((width//2, y_pos), 'has successfully completed the requirements for', fill='#6B7280', font=body_font, anchor='mt')
    
    # Certification name
    y_pos += 60
    cert_name = developer_certification.certification_level.name
    draw.text((width//2, y_pos), cert_name, fill='#1F2937', font=cert_font, anchor='mt')
    
    # Level
    y_pos += 60
    level_text = f"Level: {developer_certification.certification_level.get_level_type_display()}"
    draw.text((width//2, y_pos), level_text, fill=border_color, font=body_font, anchor='mt')
    
    # Score
    if developer_certification.score:
        y_pos += 40
        draw.text((width//2, y_pos), f'Score: {developer_certification.score}%', fill='#6B7280', font=body_font, anchor='mt')
    
    # Date
    y_pos += 60
    issue_date = developer_certification.issued_at.strftime('%B %d, %Y')
    draw.text((width//2, y_pos), f'Issued on {issue_date}', fill='#374151', font=body_font, anchor='mt')
    
    # Certificate number
    y_pos = height - 120
    draw.text((width//2, y_pos), f'Certificate No: {developer_certification.certificate_number}', fill='#9CA3AF', font=small_font, anchor='mt')
    
    # Hash
    if developer_certification.certificate_hash:
        y_pos += 30
        draw.text((width//2, y_pos), f'Hash: {developer_certification.certificate_hash[:48]}...', fill='#9CA3AF', font=small_font, anchor='mt')
    
    # Save
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    return buffer.getvalue()


def save_contract_documents(contract):
    """
    Generate and save both PDF and PNG for a contract
    """
    # Generate PDF
    pdf_content = generate_contract_pdf(contract)
    pdf_filename = f"contract_{contract.id}_{contract.contract_hash[:8]}.pdf"
    contract.pdf_file.save(pdf_filename, ContentFile(pdf_content), save=False)
    
    # Generate PNG
    png_content = generate_contract_png(contract)
    png_filename = f"contract_{contract.id}_{contract.contract_hash[:8]}.png"
    contract.png_file.save(png_filename, ContentFile(png_content), save=False)
    
    contract.save()
    
    return contract


def save_certificate_documents(developer_certification):
    """
    Generate and save both PDF and PNG for a certificate
    """
    # Generate PDF
    pdf_content = generate_certificate_pdf(developer_certification)
    pdf_filename = f"cert_{developer_certification.certificate_number}.pdf"
    developer_certification.pdf_file.save(pdf_filename, ContentFile(pdf_content), save=False)
    
    # Generate PNG
    png_content = generate_certificate_png(developer_certification)
    png_filename = f"cert_{developer_certification.certificate_number}.png"
    developer_certification.png_file.save(png_filename, ContentFile(png_content), save=False)
    
    developer_certification.save()
    
    return developer_certification
