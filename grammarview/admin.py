from django.contrib import admin
from django.forms import BaseModelFormSet

from treenode.admin import TreeNodeModelAdmin
from treenode.forms import TreeNodeForm

from grammarview.models import EdiGrammar,EdiGrammarItem,GrammarRecord

#TEST
from django.utils.translation import gettext as _
from django.utils.translation import ngettext
from django.core.exceptions import (
    FieldDoesNotExist,
    FieldError,
    PermissionDenied,
    ValidationError,
)
from django.template.response import SimpleTemplateResponse, TemplateResponse
from django.http import HttpResponseRedirect
from django.contrib.admin import helpers, widgets
from django.contrib.admin.utils import (
    NestedObjects,
    construct_change_message,
    flatten_fieldsets,
    get_deleted_objects,
    lookup_spawns_duplicates,
    model_format_dict,
    model_ngettext,
    quote,
    unquote,
)
from django.contrib import messages

class IncorrectLookupParameters(Exception):
        pass

class GrammarRecordInline(admin.TabularInline):
        model = GrammarRecord
        form = TreeNodeForm  
        fields = ('name','mandatory','length','format','is_field','decimals','minlength','bformat','maxrepeat','subfields')
        extra = 0 

class EdiGrammarAdmin(admin.ModelAdmin):
    list_display = ['name']
    inlines = [GrammarRecordInline]
admin.site.register(EdiGrammar, EdiGrammarAdmin)

class EdiGrammarItemAdmin(admin.ModelAdmin):
    list_display = ['object_id']
admin.site.register(EdiGrammarItem, EdiGrammarItemAdmin)

# class RecordAdminFormSet(BaseModelFormSet):
#     def _construct_form(self, i, **kwargs):
#         if self.get_queryset()[i].tn_children_count == 0: #si la linea no tiene Hijos
#             form = super()._construct_form(i, **kwargs)
#             form.fields['value'].widget.attrs['style'] = "color: #000000; border: 2px solid #79aec8"
#             form.fields['value'].widget.attrs['readonly'] = False
#             #form.fields['value'].disable = False
#             return form
#         else:
#             form = super()._construct_form(i, **kwargs)
#             form.fields['value'].widget.attrs['style'] = "color:  #b7b7b7 ; border: 1px solid #b7b7b7 "
#             form.fields['value'].widget.attrs['readonly'] = True
#             #form.fields['value'].disable = True
#             return form

        # pk_required = i < self.initial_form_count()value
        # if pk_required:
        #     if self.is_bound:
        #         pk_key = "%s-%s" % (self.add_prefix(i), self.model._meta.pk.name)
        #         try:
        #             pk = self.data[pk_key]
        #         except KeyError:
        #             # The primary key is missing. The user may have tampered
        #             # with POST data.
        #             pass
        #         else:
        #             to_python = self._get_to_python(self.model._meta.pk)
        #             try:
        #                 pk = to_python(pk)
        #             except ValidationError:
        #                 # The primary key exists but is an invalid value. The
        #                 # user may have tampered with POST data.
        #                 pass
        #             else:
        #                 kwargs["instance"] = self._existing_object(pk)
        #     else:
        #         kwargs["instance"] = self.get_queryset()[i]
        # elif self.initial_extra:
        #     # Set initial values for extra forms
        #     try:
        #         kwargs["initial"] = self.initial_extra[i - self.initial_form_count()]
        #     except IndexError:
        #         pass
        # form = super()._construct_form(i, **kwargs)
        # if pk_required:
        #     form.fields[self.model._meta.pk.name].required = True
        # return form

class GrammarRecordAdmin(TreeNodeModelAdmin):

    # set the changelist display mode: 'accordion', 'breadcrumbs' or 'indentation' (default)
    # when changelist results are filtered by a querystring,
    # 'breadcrumbs' mode will be used (to preserve data display integrity)
    treenode_display_mode = TreeNodeModelAdmin.TREENODE_DISPLAY_MODE_ACCORDION
    # treenode_display_mode = TreeNodeModelAdmin.TREENODE_DISPLAY_MODE_BREADCRUMBS
    # treenode_display_mode = TreeNodeModelAdmin.TREENODE_DISPLAY_MODE_INDENTATION

    # use TreeNodeForm to automatically exclude invalid parent choices

    #form = TreeNodeForm
    list_display = ['name', 'min', 'max' , 'mandatory','length','format','decimals','maxrepeat','edigrammar']
    list_editable = ['min', 'max','mandatory']
    ordering = ['edigrammar','id']
    list_filter = ['edigrammar']
    search_fields = ['edigrammar__name__icontains']

    #form.fields['value'].disabled = True

    # def has_change_permission(self, request, obj: Record= Record):
    #     if obj.tn_children_count == 0 :
    #         return True
    #     else:
    #         return True   

   #  def get_changelist_formset(self, request, **kwargs):
   #      kwargs['formset'] = RecordAdminFormSet
   #      return super().get_changelist_formset(request, **kwargs)

   #  def changelist_view(self, request, extra_context=None):
   #      """
   #      The 'change list' admin view for this model.
   #      """
   #      from django.contrib.admin.views.main import ERROR_FLAG

   #      opts = self.model._meta
   #      app_label = opts.app_label
   #      if not self.has_view_or_change_permission(request):
   #          raise PermissionDenied

   #      try:
   #          cl = self.get_changelist_instance(request)
   #      except IncorrectLookupParameters:
   #          # Wacky lookup parameters were given, so redirect to the main
   #          # changelist page, without parameters, and pass an 'invalid=1'
   #          # parameter via the query string. If wacky parameters were given
   #          # and the 'invalid=1' parameter was already in the query string,
   #          # something is screwed up with the database, so display an error
   #          # page.
   #          if ERROR_FLAG in request.GET:
   #              return SimpleTemplateResponse(
   #                  "admin/invalid_setup.html",
   #                  {
   #                      "title": _("Database error"),
   #                  },
   #              )
   #          return HttpResponseRedirect(request.path + "?" + ERROR_FLAG + "=1")

   #      # If the request was POSTed, this might be a bulk action or a bulk
   #      # edit. Try to look up an action or confirmation first, but if this
   #      # isn't an action the POST will fall through to the bulk edit check,
   #      # below.
   #      action_failed = False
   #      selected = request.POST.getlist(helpers.ACTION_CHECKBOX_NAME)

   #      actions = self.get_actions(request)
   #      # Actions with no confirmation
   #      if (
   #          actions
   #          and request.method == "POST"
   #          and "index" in request.POST
   #          and "_save" not in request.POST
   #      ):
   #          if selected:
   #              response = self.response_action(
   #                  request, queryset=cl.get_queryset(request)
   #              )
   #              if response:
   #                  return response
   #              else:
   #                  action_failed = True
   #          else:
   #              msg = _(
   #                  "Items must be selected in order to perform "
   #                  "actions on them. No items have been changed."
   #              )
   #              self.message_user(request, msg, messages.WARNING)
   #              action_failed = True

   #      # Actions with confirmation
   #      if (
   #          actions
   #          and request.method == "POST"
   #          and helpers.ACTION_CHECKBOX_NAME in request.POST
   #          and "index" not in request.POST
   #          and "_save" not in request.POST
   #      ):
   #          if selected:
   #              response = self.response_action(
   #                  request, queryset=cl.get_queryset(request)
   #              )
   #              if response:
   #                  return response
   #              else:
   #                  action_failed = True

   #      if action_failed:
   #          # Redirect back to the changelist page to avoid resubmitting the
   #          # form if the user refreshes the browser or uses the "No, take
   #          # me back" button on the action confirmation page.
   #          return HttpResponseRedirect(request.get_full_path())

   #      # If we're allowing changelist editing, we need to construct a formset
   #      # for the changelist given all the fields to be edited. Then we'll
   #      # use the formset to validate/process POSTed data.
   #      formset = cl.formset = None

   #      # Handle POSTed bulk-edit data.
   #      if request.method == "POST" and cl.list_editable and "_save" in request.POST:
   #          if not self.has_change_permission(request):
   #              raise PermissionDenied
   #          FormSet = self.get_changelist_formset(request)
   #          modified_objects = self._get_list_editable_queryset(
   #              request, FormSet.get_default_prefix()
   #          )
   #          formset = cl.formset = FormSet(
   #              request.POST, request.FILES, queryset=modified_objects
   #          )
   #          if formset.is_valid():
   #              changecount = 0
   #              for form in formset.forms:
   #                  if form.has_changed():
   #                      obj = self.save_form(request, form, change=True)
   #                      if obj.tn_children_count == 0:  #si la linea no tiene Hijos
   #                          self.save_model(request, obj, form, change=True)
   #                          self.save_related(request, form, formsets=[], change=True)
   #                          change_msg = self.construct_change_message(request, form, None)
   #                          self.log_change(request, obj, change_msg)
   #                          changecount += 1

   #              if changecount:
   #                  msg = ngettext(
   #                      "%(count)s %(name)s was changed successfully.",
   #                      "%(count)s %(name)s were changed successfully.",
   #                      changecount,
   #                  ) % {
   #                      "count": changecount,
   #                      "name": model_ngettext(opts, changecount),
   #                  }
   #                  self.message_user(request, msg, messages.SUCCESS)

   #              return HttpResponseRedirect(request.get_full_path())

   #      # Handle GET -- construct a formset for display.
   #      elif cl.list_editable and self.has_change_permission(request):
   #          FormSet = self.get_changelist_formset(request)
   #          formset = cl.formset = FormSet(queryset=cl.result_list)

   #      # Build the list of media to be used by the formset.
   #      if formset:
   #          media = self.media + formset.media
   #      else:
   #          media = self.media

   #      # Build the action form and populate it with available actions.
   #      if actions:
   #          action_form = self.action_form(auto_id=None)
   #          action_form.fields["action"].choices = self.get_action_choices(request)
   #          media += action_form.media
   #      else:
   #          action_form = None

   #      selection_note_all = ngettext(
   #          "%(total_count)s selected", "All %(total_count)s selected", cl.result_count
   #      )

   #      context = {
   #          **self.admin_site.each_context(request),
   #          "module_name": str(opts.verbose_name_plural),
   #          "selection_note": _("0 of %(cnt)s selected") % {"cnt": len(cl.result_list)},
   #          "selection_note_all": selection_note_all % {"total_count": cl.result_count},
   #          "title": cl.title,
   #          "subtitle": None,
   #          "is_popup": cl.is_popup,
   #          "to_field": cl.to_field,
   #          "cl": cl,
   #          "media": media,
   #          "has_add_permission": self.has_add_permission(request),
   #          "opts": cl.opts,
   #          "action_form": action_form,
   #          "actions_on_top": self.actions_on_top,
   #          "actions_on_bottom": self.actions_on_bottom,
   #          "actions_selection_counter": self.actions_selection_counter,
   #          "preserved_filters": self.get_preserved_filters(request),
   #          **(extra_context or {}),
   #      }

   #      request.current_app = self.admin_site.name

   #      return TemplateResponse(
   #          request,
   #          self.change_list_template
   #          or [
   #              "admin/%s/%s/change_list.html" % (app_label, opts.model_name),
   #              "admin/%s/change_list.html" % app_label,
   #              "admin/change_list.html",
   #          ],
   #          context,
   #      )     

admin.site.register(GrammarRecord, GrammarRecordAdmin)

# class FieldAdmin(admin.ModelAdmin):

#     # set the changelist display mode: 'accordion', 'breadcrumbs' or 'indentation' (default)
#     # when changelist results are filtered by a querystring,
#     # 'breadcrumbs' mode will be used (to preserve data display integrity)
#     # treenode_display_mode = TreeNodeModelAdmin.TREENODE_DISPLAY_MODE_ACCORDION
#     # treenode_display_mode = TreeNodeModelAdmin.TREENODE_DISPLAY_MODE_BREADCRUMBS
#     # treenode_display_mode = TreeNodeModelAdmin.TREENODE_DISPLAY_MODE_INDENTATION

#     # use TreeNodeForm to automatically exclude invalid parent choices
#     list_display = ['record_name','name','value']
#     list_editable = ['value']
#     list_select_related = ['record']
#     def record_name(self, Field):
#         return Field.record.name
# admin.site.register(Field, FieldAdmin)