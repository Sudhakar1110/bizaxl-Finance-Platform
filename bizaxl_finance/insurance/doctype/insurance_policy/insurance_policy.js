frappe.ui.form.on('Insurance Policy', {
    refresh: function(frm) {
        frm.add_custom_button(__('Premium Payments'), function() {
            frappe.set_route('List', 'Premium Payment', {insurance_policy: frm.doc.name});
        }, __('Related'));

        frm.add_custom_button(__('Claims'), function() {
            frappe.set_route('List', 'Insurance Claim', {insurance_policy: frm.doc.name});
        }, __('Related'));
    }
});
