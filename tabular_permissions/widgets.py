from __future__ import unicode_literals

from collections import OrderedDict

from django import VERSION
from django.apps import apps
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.utils.encoding import force_text
from .app_settings import (
    EXCLUDE_FUNCTION, EXCLUDE_APPS,
    EXCLUDE_MODELS, USE_FOR_CONCRETE,
    TRANSLATION_FUNC, APPS_CUSTOMIZATION_FUNC,
    CUSTOM_PERMISSIONS_CUSTOMIZATION_FUNC,
    TEMPLATE)
from .helpers import get_perm_name


def get_reminder_permissions_iterator(choices, reminder_perms):
    reminder_perms_list = reminder_perms.values()
    l = []
    for c in choices:
        if c[0] in reminder_perms_list:
            l.append(c)
    return l


class TabularPermissionsWidget(FilteredSelectMultiple):
    # Template that renders the widget
    base_template_name = "django/forms/widgets/select.html"
    # Template that renders the table and includes the widget
    template_name = TEMPLATE

    def __init__(self, verbose_name, is_stacked, input_name='user_permissions', attrs=None, choices=()):
        super(TabularPermissionsWidget, self).__init__(verbose_name, is_stacked, attrs, choices)
        self.managed_perms = []
        self.input_name = input_name  # in case of UserAdmin, it's 'user_permissions', GroupAdmin it's 'permissions'
        self.hide_original = True
        self.org_choices = list(self.choices)

    def get_table_context(self, name, value, attrs):
        choices = self.org_choices
        apps_available = OrderedDict()  # []  # main container to send to template
        user_permissions = Permission.objects.filter(id__in=value or []).values_list('id', flat=True)
        all_perms = Permission.objects.all().values('id', 'codename', 'content_type_id').order_by('codename')
        excluded_perms = set([])
        codename_id_map = {}
        for p in all_perms:
            codename_id_map['%s_%s' % (p['codename'], p['content_type_id'])] = p['id']

        # reminder_perms used to detect if the tabular permissions covers all permissions,
        # if true, we don't need to make the default widget visible.
        reminder_perms = codename_id_map.copy()

        # a global flag to either show or hide the other permission column in the table
        custom_permissions_available = False

        for app in apps.get_app_configs():
            app_dict = {'verbose_name': force_text(app.verbose_name),
                        'label': app.label,
                        'models': OrderedDict()}

            for model_name in app.models:
                model_custom_permissions = []
                model_custom_permissions_ids = []

                model = app.models[model_name]
                opts = model._meta
                ct_id = ContentType.objects.get_for_model(model, for_concrete_model=USE_FOR_CONCRETE).pk

                view_perm_name = get_perm_name(model_name, 'view')
                add_perm_name = get_perm_name(model_name, 'add')
                change_perm_name = get_perm_name(model_name, 'change')
                delete_perm_name = get_perm_name(model_name, 'delete')

                view_perm_id = codename_id_map.get('%s_%s' % (view_perm_name, ct_id),
                                                   False) if 'view' in opts.default_permissions else False
                add_perm_id = codename_id_map.get('%s_%s' % (add_perm_name, ct_id),
                                                  False) if 'add' in opts.default_permissions else False
                change_perm_id = codename_id_map.get('%s_%s' % (change_perm_name, ct_id),
                                                     False) if 'change' in opts.default_permissions else False
                delete_perm_id = codename_id_map.get('%s_%s' % (delete_perm_name, ct_id),
                                                     False) if 'delete' in opts.default_permissions else False
                if opts.permissions:
                    custom_permissions_available = True
                    for codename, perm_name in opts.permissions:
                        c_perm_id = codename_id_map.get('%s_%s' % (codename, ct_id), False)
                        verbose_name = TRANSLATION_FUNC(codename, perm_name, ct_id)
                        model_custom_permissions.append(
                            (codename, verbose_name, c_perm_id)
                        )
                        model_custom_permissions_ids.append(c_perm_id)

                if view_perm_id or add_perm_id or change_perm_id or delete_perm_id or model_custom_permissions:
                    excluded_perms.update([view_perm_id, add_perm_id, change_perm_id, delete_perm_id] +
                                          model_custom_permissions_ids)
                    reminder_perms.pop('%s_%s' % (view_perm_name, ct_id), False)
                    reminder_perms.pop('%s_%s' % (add_perm_name, ct_id), False)
                    reminder_perms.pop('%s_%s' % (change_perm_name, ct_id), False)
                    reminder_perms.pop('%s_%s' % (delete_perm_name, ct_id), False)
                    for c, v, _id in model_custom_permissions:
                        reminder_perms.pop('%s_%s' % (c, ct_id), False)

                    # Because the logic of exclusion should/would work on both the tabular_permissin widget
                    # and the normal widget
                    # ie bydefautlwe exclude the session, admin log permissions and we dont want that on either widgets
                    if app.label in EXCLUDE_APPS or model_name in EXCLUDE_MODELS or EXCLUDE_FUNCTION(model):
                        continue

                    app_dict['models'][model_name] = {
                        'model_name': model_name,
                        'model': model,
                        'verbose_name_plural': force_text(opts.verbose_name_plural),
                        'verbose_name': force_text(opts.verbose_name),
                        'view_perm_id': view_perm_id,
                        'view_perm_name': view_perm_name,
                        'add_perm_id': add_perm_id,
                        'add_perm_name': add_perm_name,
                        'change_perm_id': change_perm_id,
                        'change_perm_name': change_perm_name,
                        'delete_perm_id': delete_perm_id,
                        'delete_perm_name': delete_perm_name,
                        'custom_permissions': model_custom_permissions,
                    }

            if app.models:
                apps_available[app.label] = app_dict
        if VERSION >= (2, 1, 0) and custom_permissions_available:
            colspan = 7
        elif VERSION >= (2, 1, 0) or custom_permissions_available:
            colspan = 6
        else:
            colspan = 5

        apps_available = APPS_CUSTOMIZATION_FUNC(apps_available)

        self.managed_perms = excluded_perms
        if reminder_perms:
            self.hide_original = False

        reminder_choices = get_reminder_permissions_iterator(choices, reminder_perms)
        # filter the left over permission
        reminder_choices = CUSTOM_PERMISSIONS_CUSTOMIZATION_FUNC(reminder_choices)

        ctx = {
            'template_name': "tabular_permissions/admin/tabular_permissions.html",
            'apps_available': apps_available,
            'user_permissions': user_permissions,
            'codename_id_map': codename_id_map,
            'input_name': self.input_name,
            'custom_permissions_available': custom_permissions_available,
            'colspan': colspan,
            'django_supports_view_permissions': VERSION >= (2, 1, 0),
            'reminder_choices': reminder_choices
        }
        return ctx

    def get_context(self, name, value, attrs):
        ctx = self.get_table_context(name, value, attrs)
        self.choices = ctx.get('reminder_choices', [])
        context = super().get_context(name, value, attrs)
        context['widget']['base_template_name'] = self.base_template_name
        context['widget']['table'] = ctx
        return context

    class Media:
        js = ('tabular_permissions/tabular_permissions.js',)
