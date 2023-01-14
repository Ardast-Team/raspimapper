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
# admin.site.register(models.Ccode)
# admin.site.register(models.CcodeTrigger)
# admin.site.register(models.Channel)
# admin.site.register(models.ChannelPartnerMails)
# admin.site.register(models.ChannelPartnerMail)
# admin.site.register(models.ConfirmRule)
# admin.site.register(models.Filereport)
# admin.site.register(models.Partner)
# admin.site.register(models.Partnergroup)
# admin.site.register(models.Report)
# admin.site.register(models.Routes)
# admin.site.register(models.Transaction)
# admin.site.register(models.Translate)
# admin.site.register(models.Unique)

# admin.site.register(models.Mutex)
# admin.site.register(models.Persist)



# -*- coding: utf-8 -*-

''' Bots configuration for django's admin site.'''
from django import forms
from django.forms import utils as django_forms_util

from django.utils.translation import gettext as _
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
#bots-modules
from bots import models
from bots.utils import botsglobal


class BotsAdmin(admin.ModelAdmin):
    ''' all classes in this module are sub-classed from BotsAdmin.
    '''
    list_per_page = botsglobal.ini.getint('settings', 'adminlimit', botsglobal.ini.getint('settings', 'limit', 30))
    save_as = True

    def activate(self, request, queryset):
        ''' handles the admin 'activate' action.'''
        # much faster: queryset.update(active=not F('active')) but negation of F()
        # object is not yet supported in django (20140307)
        for obj in queryset:
            obj.active = not obj.active
            obj.save()
    activate.short_description = _('activate/de-activate')

#*****************************************************************************************************


class CcodeAdmin(BotsAdmin):
    list_display = ('ccodeid', 'leftcode', 'rightcode', 'attr1', 'attr2',
                    'attr3', 'attr4', 'attr5', 'attr6', 'attr7', 'attr8')
    list_display_links = ('ccodeid',)
    list_filter = ('ccodeid',)
    ordering = ('ccodeid', 'leftcode')
    search_fields = ('ccodeid__ccodeid', 'leftcode', 'rightcode', 'attr1',
                     'attr2', 'attr3', 'attr4', 'attr5', 'attr6', 'attr7', 'attr8')
    fieldsets = (
        (None, {'fields': ('ccodeid', 'leftcode', 'rightcode', 'attr1', 'attr2', 'attr3', 'attr4', 'attr5', 'attr6', 'attr7', 'attr8'),
                'description': 'For description of user code lists and usage in mapping: see <a target="_blank" href="https://bots-edi.github.io/bots/configuration/mapping-scripts/code-conversion.html">wiki</a>.',
                'classes': ('wide extrapretty',)
                }),
        )

    def lookup_allowed(self, lookup, *args, **kwargs):
        if lookup.startswith('ccodeid'):
            return True
        return super(CcodeAdmin, self).lookup_allowed(lookup, *args, **kwargs)
admin.site.register(models.Ccode, CcodeAdmin)


class CcodetriggerAdmin(BotsAdmin):
    list_display = ('ccodeid', 'ccodeid_desc',)
    list_display_links = ('ccodeid',)
    ordering = ('ccodeid',)
    search_fields = ('ccodeid', 'ccodeid_desc')
admin.site.register(models.CcodeTrigger, CcodetriggerAdmin)


class ChannelAdmin(BotsAdmin):
    list_display = ('idchannel', 'inorout', 'type', 'communicationscript', 'remove', 'host', 'port', 'username', 'secret', 'path', 'filename', 'mdnchannel',
                    'testpath', 'archivepath', 'rsrv3', 'rsrv2', 'rsrv1', 'syslock', 'parameters', 'starttls', 'apop', 'askmdn', 'sendmdn', 'ftpactive', 'ftpbinary')
    list_filter = ('inorout', 'type')
    ordering = ('idchannel',)
    readonly_fields = ('communicationscript',)
    search_fields = ('idchannel', 'inorout', 'type', 'host', 'username', 'path', 'filename', 'archivepath', 'desc')
    fieldsets = (
        (None, {'fields': (('idchannel', 'inorout', 'type'),
                           ('remove', 'communicationscript'),
                           ('host', 'port'),
                           ('username', 'secret'),
                           ('path', 'filename'),
                           ('archivepath', 'rsrv3'),
                           'desc'),
                'classes': ('wide extrapretty',)
                }),
        (_('Email specific'), {'fields': ('starttls', 'apop', 'askmdn', 'sendmdn'),
                               'classes': ('collapse wide extrapretty',)
                               }),
        (_('FTP specific'), {'fields': ('ftpactive', 'ftpbinary', 'ftpaccount'),
                             'classes': ('collapse wide extrapretty',)
                             }),
        (_('Safe writing & file locking'), {'fields': ('mdnchannel', 'syslock', 'lockname'),
                                            'description': 'For more info see <a target="_blank" href="https://bots-edi.github.io/bots/configuration/channel/file-locking.html">wiki</a><br>',
                                            'classes': ('collapse wide extrapretty',)
                                            }),
        (_('Other'), {'fields': ('testpath', 'keyfile', 'certfile', 'rsrv2', 'rsrv1', 'parameters'),
                      'classes': ('collapse wide extrapretty',)
                      }),
    )
admin.site.register(models.Channel, ChannelAdmin)


class MyConfirmruleAdminForm(forms.ModelForm):
    ''' customs form for route for additional checks'''
    class Meta:
        model = models.ConfirmRule
        widgets = {'idroute': forms.Select(), }
        fields = '__all__'

    def clean(self):
        super(MyConfirmruleAdminForm, self).clean()
        if self.cleaned_data['ruletype'] == 'route':
            if not self.cleaned_data['idroute']:
                raise django_forms_util.ValidationError(_('For ruletype "route" it is required to indicate a route.'))
        elif self.cleaned_data['ruletype'] == 'channel':
            if not self.cleaned_data['idchannel']:
                raise django_forms_util.ValidationError(
                    _('For ruletype "channel" it is required to indicate a channel.'))
        elif self.cleaned_data['ruletype'] == 'frompartner':
            if not self.cleaned_data['frompartner']:
                raise django_forms_util.ValidationError(
                    _('For ruletype "frompartner" it is required to indicate a frompartner.'))
        elif self.cleaned_data['ruletype'] == 'topartner':
            if not self.cleaned_data['topartner']:
                raise django_forms_util.ValidationError(
                    _('For ruletype "topartner" it is required to indicate a topartner.'))
        elif self.cleaned_data['ruletype'] == 'messagetype':
            if not self.cleaned_data['messagetype']:
                raise django_forms_util.ValidationError(
                    _('For ruletype "messagetype" it is required to indicate a messagetype.'))
        return self.cleaned_data


class ConfirmruleAdmin(BotsAdmin):
    actions = ('activate',)
    form = MyConfirmruleAdminForm
    list_display = ('active', 'negativerule', 'confirmtype', 'ruletype',
                    'frompartner', 'topartner', 'idroute', 'idchannel', 'messagetype')
    list_display_links = ('confirmtype',)
    list_filter = ('active', 'confirmtype', 'ruletype')
    search_fields = ('confirmtype', 'ruletype', 'frompartner__idpartner',
                     'topartner__idpartner', 'idroute', 'idchannel__idchannel', 'messagetype')
    ordering = ('confirmtype', 'ruletype')
    fieldsets = (
        (None, {'fields': ('active', 'negativerule', 'confirmtype', 'ruletype', 'frompartner', 'topartner', 'idroute', 'idchannel', 'messagetype'),
                'classes': ('wide extrapretty',)
                }),
        )

    def formfield_for_dbfield(self, db_field, **kwargs):
        ''' make dynamic choice list for field idroute. not a foreign key, gave to much trouble.'''
        if db_field.name == 'idroute':
            kwargs['widget'].choices = models.getroutelist()
        return super(ConfirmruleAdmin, self).formfield_for_dbfield(db_field, **kwargs)
admin.site.register(models.ConfirmRule, ConfirmruleAdmin)


class MailInline(admin.TabularInline):
    model = models.ChannelPartnerMails
    fields = ('idchannel', 'mail', 'cc')
    extra = 1


class PartnerAdmin(BotsAdmin):
    actions = ('activate',)
    filter_horizontal = ('group',)
    inlines = (MailInline,)
    list_display = ('active', 'idpartner', 'name', 'address1', 'city', 'countrysubdivision', 'countrycode',
                    'postalcode', 'startdate', 'enddate', 'phone1', 'phone2', 'attr1', 'attr2', 'attr3', 'attr4', 'attr5')
    list_display_links = ('idpartner',)
    list_filter = ('active',)
    ordering = ('idpartner',)
    search_fields = ('idpartner', 'name', 'address1', 'city', 'countrysubdivision',
                     'countrycode', 'postalcode', 'attr1', 'attr2', 'attr3', 'attr4', 'attr5', 'name1', 'name2', 'name3')
    fieldsets = (
        (None, {'fields': ('active', ('idpartner', 'name'), 'desc', ('startdate', 'enddate')),
                'classes': ('wide extrapretty',)
                }),
        (_('Address'), {'fields': ('name1', 'name2', 'name3', 'address1', 'address2', 'address3', ('postalcode', 'city'), ('countrycode', 'countrysubdivision'), ('phone1', 'phone2')),
                        'classes': ('collapse wide extrapretty',)
                        }),
        (_('Is in groups'), {'fields': ('group',),
                             'classes': ('collapse wide extrapretty',)
                             }),
        (_('User defined'), {'fields': ('attr1', 'attr2', 'attr3', 'attr4', 'attr5'),
                             'classes': ('wide extrapretty',)
                             }),
    )

    def queryset(self, request):
        return self.model.objects.filter(isgroup=False)
admin.site.register(models.Partner, PartnerAdmin)

#~ class PartnerInline(admin.TabularInline):
#~ model = models.partner.group.through
# fields = ('idpartner','name')
# extra = 1
#~ fk_name = 'from_partner_id'


class PartnerGroupAdmin(BotsAdmin):
    actions = ('activate',)
    #~ inlines = [PartnerInline,]
    #~ exclude = ('group',)
    list_display = ('active', 'idpartner', 'name', 'startdate', 'enddate')
    list_display_links = ('idpartner',)
    list_filter = ('active',)
    ordering = ('idpartner',)
    search_fields = ('idpartner', 'name', 'desc')
    fieldsets = (
        (None, {'fields': ('active', 'idpartner', 'name', 'desc', ('startdate', 'enddate')),
                'classes': ('wide extrapretty',)
                }),
    )

    def queryset(self, request):
        return self.model.objects.filter(isgroup=True)
admin.site.register(models.Partnergroup, PartnerGroupAdmin)


class MyRouteAdminForm(forms.ModelForm):
    ''' customs form for route for additional checks'''
    class Meta:
        model = models.Routes
        fields = '__all__'

    def clean(self):
        super(MyRouteAdminForm, self).clean()
        if self.cleaned_data['fromchannel'] and self.cleaned_data['translateind'] != 2 and (not self.cleaned_data['fromeditype'] or not self.cleaned_data['frommessagetype']):
            raise django_forms_util.ValidationError(
                _('When using an inchannel and not pass-through, both "fromeditype" and "frommessagetype" are required.'))
        return self.cleaned_data


class RoutesAdmin(BotsAdmin):
    actions = ('activate',)
    form = MyRouteAdminForm
    list_display = ('active', 'idroute', 'seq', 'routescript', 'fromchannel', 'fromeditype', 'frommessagetype', 'alt', 'frompartner', 'topartner', 'translt', 'tochannel',
                    'defer', 'toeditype', 'tomessagetype', 'frompartner_tochannel', 'topartner_tochannel', 'indefaultrun', 'testindicator', 'zip_incoming', 'zip_outgoing',)
    list_display_links = ('idroute',)
    list_filter = ('active', 'notindefaultrun', 'idroute', 'fromeditype')
    ordering = ('idroute', 'seq')
    readonly_fields = ('routescript',)
    search_fields = ('idroute', 'fromchannel__idchannel', 'fromeditype', 'frommessagetype',
                     'alt', 'tochannel__idchannel', 'toeditype', 'tomessagetype', 'desc')
    fieldsets = (
        (None, {'fields': (('active', 'notindefaultrun'), 'routescript', ('idroute', 'seq',), 'fromchannel', ('fromeditype', 'frommessagetype'), 'translateind', 'tochannel', 'desc'),
                'classes': ('wide extrapretty',)
                }),
        (_('Filtering for outchannel'), {'fields': ('toeditype', 'tomessagetype', 'frompartner_tochannel', 'topartner_tochannel', 'testindicator'),
                                         'classes': ('collapse wide extrapretty',)
                                         }),
        (_('Advanced'), {'fields': ('alt', 'frompartner', 'topartner', 'defer', 'zip_incoming', 'zip_outgoing'),
                         'classes': ('collapse wide extrapretty',)
                         }),
    )
admin.site.register(models.Routes, RoutesAdmin)


class MyTranslateAdminForm(forms.ModelForm):
    ''' customs form for translations to check if entry exists (unique_together not validated right (because of null values in partner fields))'''
    class Meta:
        model = models.Translate
        fields = '__all__'

    def clean(self):
        super(MyTranslateAdminForm, self).clean()
        blub = models.Translate.objects.filter(fromeditype=self.cleaned_data['fromeditype'],
                                               frommessagetype=self.cleaned_data['frommessagetype'],
                                               alt=self.cleaned_data['alt'],
                                               frompartner=self.cleaned_data['frompartner'],
                                               topartner=self.cleaned_data['topartner'])
        if blub and (self.instance.pk is None or self.instance.pk != blub[0].id):
            raise django_forms_util.ValidationError(
                _('Combination of fromeditype,frommessagetype,alt,frompartner,topartner already exists.'))
        return self.cleaned_data


class TranslateAdmin(BotsAdmin):
    actions = ('activate',)
    form = MyTranslateAdminForm
    list_display = ('active', 'fromeditype', 'frommessagetype_link', 'alt', 'frompartner',
                    'topartner', 'tscript_link', 'toeditype', 'tomessagetype_link')
    list_display_links = ('fromeditype',)
    list_filter = ('active', 'fromeditype', 'toeditype')
    ordering = ('fromeditype', 'frommessagetype')
    search_fields = ('fromeditype', 'frommessagetype', 'alt', 'frompartner__idpartner',
                     'topartner__idpartner', 'tscript', 'toeditype', 'tomessagetype', 'desc')
    fieldsets = (
        (None, {'fields': ('active', ('fromeditype', 'frommessagetype'), 'tscript', ('toeditype', 'tomessagetype'), 'desc'),
                'classes': ('wide extrapretty',)
                }),
        (_('Multiple translations per editype/messagetype'), {'fields': ('alt', 'frompartner', 'topartner'),
                                                              'classes': ('wide extrapretty',)
                                                              }),
    )
admin.site.register(models.Translate, TranslateAdmin)


class UniqueAdmin(BotsAdmin):  # AKA counters

    def has_add_permission(self, request):  # no adding of counters
        return False

    def has_delete_permission(self, request, obj=None):  # no deleting of counters
        return False
    actions = None
    list_display = ('domain', 'number')
    readonly_fields = ('domain',)  # never edit the domein field
    ordering = ('domain',)
    search_fields = ('domain',)
    fieldsets = (
        (None, {'fields': ('domain', 'number'),
                'classes': ('wide extrapretty',)
                }),
    )
admin.site.register(models.Unique, UniqueAdmin)

#User - change the default display of user screen
UserAdmin.list_display = ('username', 'first_name', 'last_name', 'email', 'is_active',
                          'is_staff', 'is_superuser', 'date_joined', 'last_login')
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
