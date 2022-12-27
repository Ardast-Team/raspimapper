from urllib.parse import urlencode
from django.contrib import admin, messages
from django.http import HttpRequest

#from django.contrib.contenttypes.admin import GenericTabularInline # commented because we plug it into a separate app (store_custom)
#from tags.models import TaggedItem # commented because we plug it into a separate app (store_custom)

from bots import models
#from django.db.models import Count
#from django.utils.html import format_html
from django.urls import reverse
# Register your models here.
#admin.site.register(models.Product) #useless if I have ProductAdmin class 
admin.site.register(models.Ccode)
admin.site.register(models.CcodeTrigger)
admin.site.register(models.Channel)
admin.site.register(models.ChannelPartnerMails)
admin.site.register(models.ChannelPartnerMail)
admin.site.register(models.ConfirmRule)
admin.site.register(models.Filereport)
admin.site.register(models.Partner)
admin.site.register(models.Partnergroup)
admin.site.register(models.Report)
admin.site.register(models.Routes)
admin.site.register(models.Transaction)
admin.site.register(models.Translate)
admin.site.register(models.Unique)

admin.site.register(models.Mutex)
admin.site.register(models.Persist)



