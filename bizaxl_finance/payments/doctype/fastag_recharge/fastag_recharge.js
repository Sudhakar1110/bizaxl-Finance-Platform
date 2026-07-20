frappe.ui.form.on('FASTag Recharge', {
    refresh: function(frm) {
        if (frm.doc.docstatus == 0) {
            frm.add_custom_button(__('Get Balance'), function() {
                frappe.msgprint(__('Balance check feature coming soon.'));
            }, __('Actions'));
        }
    }
});
