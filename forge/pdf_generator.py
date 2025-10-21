"""
PDF License and Support Document Generator
Generates signed license and support documents for purchased Buildly Forge apps
"""

import os
from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib import colors
from django.conf import settings
from django.core.files.base import ContentFile


class LicensePDFGenerator:
    """Generate professional license and support documents"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
    
    def setup_custom_styles(self):
        """Set up custom paragraph styles"""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.HexColor('#1f2937'),
            alignment=1  # Center
        ))
        
        self.styles.add(ParagraphStyle(
            name='SubTitle',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceAfter=20,
            textColor=colors.HexColor('#374151'),
        ))
        
        self.styles.add(ParagraphStyle(
            name='InfoBox',
            parent=self.styles['Normal'],
            fontSize=11,
            leftIndent=20,
            rightIndent=20,
            spaceAfter=12,
            borderColor=colors.HexColor('#e5e7eb'),
            borderWidth=1,
            borderPadding=10,
            backColor=colors.HexColor('#f9fafb'),
        ))
    
    def generate_license_document(self, purchase_data, purchase_id):
        """
        Generate a comprehensive license and support PDF document
        
        Args:
            purchase_data (dict): Purchase information from Stripe metadata
            purchase_id (str): Purchase ID for reference
            
        Returns:
            BytesIO: PDF document as bytes
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72,
                              topMargin=72, bottomMargin=18)
        
        # Build the document content
        story = []
        
        # Header
        story.append(Paragraph("🔐 BUILDLY FORGE LICENSE & SUPPORT AGREEMENT", self.styles['CustomTitle']))
        story.append(Spacer(1, 20))
        
        # Purchase Information Box
        purchase_info = f"""
        <b>Purchase Details</b><br/>
        Purchase ID: {purchase_id}<br/>
        Date: {datetime.now().strftime('%B %d, %Y')}<br/>
        Application: {purchase_data.get('forge_app_name', 'N/A')}<br/>
        Customer: {purchase_data.get('user_name', 'N/A')} ({purchase_data.get('user_email', 'N/A')})<br/>
        Amount Paid: ${int(purchase_data.get('final_price_cents', 0)) / 100:.2f} USD
        """
        if purchase_data.get('discount_applied', 'False') == 'True':
            purchase_info += f"<br/>Original Price: ${int(purchase_data.get('original_price_cents', 0)) / 100:.2f} USD"
            purchase_info += f"<br/>🎉 Labs Member Discount Applied: 50% off"
        
        story.append(Paragraph(purchase_info, self.styles['InfoBox']))
        story.append(Spacer(1, 20))
        
        # Application Information
        story.append(Paragraph("📦 APPLICATION INFORMATION", self.styles['SubTitle']))
        
        app_info = f"""
        <b>Repository Access:</b><br/>
        • GitHub Repository: <a href="{purchase_data.get('forge_app_repo_url', '#')}" color="blue">{purchase_data.get('forge_app_repo_url', 'N/A')}</a><br/>
        • Repository Owner: {purchase_data.get('forge_app_repo_owner', 'N/A')}<br/>
        • Repository Name: {purchase_data.get('forge_app_repo_name', 'N/A')}<br/>
        • License Type: {purchase_data.get('forge_app_license_type', 'N/A').upper()}
        """
        story.append(Paragraph(app_info, self.styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Fair Hybrid License Terms
        story.append(Paragraph("⚖️ FAIR HYBRID LICENSE TERMS", self.styles['SubTitle']))
        
        license_terms = """
        This software is licensed under the <b>Business Source License 1.1 (BSL 1.1)</b> with automatic conversion to Apache 2.0.
        
        <b>PRIMARY LICENSE:</b> Business Source License 1.1<br/>
        <b>CONVERSION DATE:</b> 24 months from first publication<br/>
        <b>FUTURE LICENSE:</b> Apache License 2.0<br/>
        
        <b>PERMITTED USES:</b><br/>
        • ✅ Personal use, learning, and development<br/>
        • ✅ Internal business operations<br/>
        • ✅ Educational and research purposes<br/>
        • ✅ Modification and customization for your needs<br/>
        
        <b>COMMERCIAL USE TERMS:</b><br/>
        • ✅ Commercial use is permitted with this purchased license<br/>
        • ✅ You may deploy this software in production environments<br/>
        • ✅ You may integrate this software into your commercial products<br/>
        • ✅ You receive priority support and updates<br/>
        
        <b>RESTRICTIONS:</b><br/>
        • ❌ You may not offer this software as a competing marketplace service<br/>
        • ❌ You may not redistribute this software for commercial gain without permission<br/>
        
        <b>AUTOMATIC CONVERSION:</b><br/>
        After 24 months from the initial publication date, this software automatically converts to Apache 2.0 license, 
        removing all commercial restrictions and making it freely available for all uses.
        """
        
        story.append(Paragraph(license_terms, self.styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Installation Instructions
        story.append(Paragraph("🚀 INSTALLATION INSTRUCTIONS", self.styles['SubTitle']))
        
        installation_guide = f"""
        <b>Step 1: Clone the Repository</b><br/>
        <font name="Courier">git clone {purchase_data.get('forge_app_repo_url', '')}</font><br/>
        <font name="Courier">cd {purchase_data.get('forge_app_repo_name', '')}</font><br/>
        
        <b>Step 2: Choose Your Deployment Option</b><br/>
        This application supports multiple deployment methods:<br/>
        • 🐳 <b>Docker:</b> Use docker-compose.yml for standalone deployment<br/>
        • 📄 <b>GitHub Pages:</b> Follow docs/github-pages.md for static site hosting<br/>
        • ☸️ <b>Kubernetes:</b> Apply manifests in k8s/ directory<br/>
        • ⚡ <b>Buildly Core:</b> Follow buildly-integration.md for microservice setup<br/>
        
        <b>Step 3: Environment Configuration</b><br/>
        Follow the README.md file in the repository for platform-specific setup instructions.<br/>
        
        <b>Step 4: License Integration</b><br/>
        Add this license file to your project root and ensure compliance with the BSL 1.1 terms.<br/>
        
        <b>Step 5: Production Deployment</b><br/>
        You are authorized to deploy this software in production with your commercial license on any supported platform.
        """
        
        story.append(Paragraph(installation_guide, self.styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Support Information
        story.append(Paragraph("🛠️ SUPPORT & MAINTENANCE", self.styles['SubTitle']))
        
        support_info = """
        <b>Priority Support Access:</b><br/>
        • 📧 Email Support: support@buildly.io<br/>
        • 💬 Community Discord: https://discord.gg/buildly<br/>
        • 📚 Documentation: https://docs.buildly.io<br/>
        • 🎫 Priority Support Portal: https://support.buildly.io<br/>
        
        <b>What's Included:</b><br/>
        • ✅ Priority technical support via email<br/>
        • ✅ Access to premium documentation and guides<br/>
        • ✅ Community support forum access<br/>
        • ✅ Updates and security patches<br/>
        • ✅ Commercial deployment guidance<br/>
        
        <b>Response Times:</b><br/>
        • 🟢 Critical Issues: 4 business hours<br/>
        • 🟡 Standard Issues: 1 business day<br/>
        • 🔵 General Questions: 2 business days<br/>
        
        When contacting support, please include your Purchase ID: <b>{purchase_id}</b>
        """
        
        story.append(Paragraph(support_info, self.styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Labs Membership (if applicable)
        if purchase_data.get('is_labs_customer', 'False') == 'True':
            story.append(Paragraph("🎯 BUILDLY LABS MEMBER BENEFITS", self.styles['SubTitle']))
            
            labs_benefits = """
            <b>Congratulations! You're a Buildly Labs Member.</b><br/>
            
            <b>Additional Benefits:</b><br/>
            • 🎉 50% discount on all Forge marketplace apps (applied to this purchase)<br/>
            • 🚀 Early access to new applications and features<br/>
            • 👥 Access to exclusive Labs community and events<br/>
            • 🎓 Priority access to training and certification programs<br/>
            • 💼 Enhanced support with dedicated Labs success manager<br/>
            
            <b>Labs Portal:</b> <a href="https://labs.buildly.io" color="blue">https://labs.buildly.io</a><br/>
            <b>Labs Support:</b> labs-support@buildly.io
            """
            
            story.append(Paragraph(labs_benefits, self.styles['Normal']))
            story.append(Spacer(1, 20))
        
        # Footer
        story.append(Spacer(1, 30))
        footer_text = f"""
        <b>Document Information:</b><br/>
        Generated on: {datetime.now().strftime('%B %d, %Y at %I:%M %p UTC')}<br/>
        Document ID: FORGE-{purchase_id}<br/>
        Version: 1.0<br/>
        
        <i>This document serves as your official license and support agreement. 
        Please retain this document for your records and reference when accessing support.</i><br/>
        
        <b>Buildly Technologies</b> • https://buildly.io • support@buildly.io
        """
        
        story.append(Paragraph(footer_text, self.styles['Normal']))
        
        # Build the PDF
        doc.build(story)
        buffer.seek(0)
        return buffer


def generate_license_pdf(purchase_data, purchase_id):
    """
    Convenience function to generate license PDF
    
    Args:
        purchase_data (dict): Purchase information from Stripe
        purchase_id (str): Purchase ID
        
    Returns:
        BytesIO: PDF document
    """
    generator = LicensePDFGenerator()
    return generator.generate_license_document(purchase_data, purchase_id)