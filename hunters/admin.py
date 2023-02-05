from .models import *
from django.contrib import admin

admin.site.register(Hunter, HunterAdmin)
admin.site.register(HunterEntry, HunterEntryAdmin)
