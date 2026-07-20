frappe.ui.form.on('Financial Goal', {
    refresh: function(frm) {
        frm.add_custom_button(__('Link Portfolio Holdings'), function() {
            frappe.set_route('List', 'Portfolio Holding', {customer: frm.doc.customer});
        }, __('Related'));
    }
});
