frappe.ui.form.on('Bank Account', {
    refresh: function(frm) {
        // Add quick actions
        frm.add_custom_button(__('View Transactions'), function() {
            frappe.set_route('List', 'Transaction', {bank_account: frm.doc.name});
        }, __('Related'));

        frm.add_custom_button(__('Link UPI'), function() {
            frappe.call({
                method: 'frappe.client.get_list',
                args: {
                    doctype: 'UPI ID',
                    filters: {bank_account: frm.doc.name}
                },
                callback: function(r) {
                    if (r.message && r.message.length > 0) {
                        frappe.set_route('Form', 'UPI ID', r.message[0].name);
                    } else {
                        frappe.new_doc('UPI ID', {bank_account: frm.doc.name, customer: frm.doc.customer});
                    }
                }
            });
        }, __('Actions'));
    },

    is_primary: function(frm) {
        if (frm.doc.is_primary) {
            frm.set_value('allow_upi', 1);
            frm.set_value('allow_netbanking', 1);
        }
    }
});
