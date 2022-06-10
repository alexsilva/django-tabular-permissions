window.onload = function() {
  (function($){
        $(".related-widget-wrapper:has(table)").addClass('related-widget-wrapper-user-permissions');
        $('input.select-all.select-column').on('change', function () {
            var $el = $(this),
                state = $el.prop('checked');
            // search for related columns.
            $('#tabular_permissions').find("tr td." + $el.data('permission')).find('input').each(function (i, e) {
                $(e).prop('checked', state)
            })
        });
        $('input.select-all.select-row').on('change', function(){
            var $this = $(this);
            $this.parents('tr').find('.checkbox').not('.select-all').each(function(i,elem){
                $(elem).prop('checked', $this.prop('checked'));
            })
        });
        $('form').on('submit', function () {
            var user_perms = [];
            var table_permissions = $('#tabular_permissions');
            var input_name = table_permissions.attr('data-input-name');
            table_permissions.find("input[type=checkbox]").not('.select-all').each(function (i, elem) {
                var $elem = $(elem);
                if ($(elem).prop('checked')) {
                    user_perms.push($elem.attr('data-perm-id'))
                }
            });
            var user_group_permissions = $('[name=' + input_name +']');
            var output = [];
            $.each(user_perms, function (key, value) {
                output.push('<option value="' + value + '" selected="selected" style="display:none"></option>');
            });
            user_group_permissions.append(output);
        })
    })(django.jQuery);
};