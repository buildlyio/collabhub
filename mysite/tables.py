import django_tables2 as tables
from .models import Product

class ProductTable(tables.Table):
    edit = tables.TemplateColumn(template_name='edit_column.html')
    delete = tables.TemplateColumn(template_name='delete_column.html')
    create_punchlist = tables.TemplateColumn(template_name='create_punchlist_column.html')

    class Meta:
        model = Product
        fields = ('name', 'description', 'date_created', 'date_updated')
        attrs = {'class': 'table table-striped table-bordered'}
