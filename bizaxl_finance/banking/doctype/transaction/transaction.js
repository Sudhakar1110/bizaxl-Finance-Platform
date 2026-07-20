frappe.ui.form.on('Transaction', {
    refresh: function(frm) {
        if (frm.doc.docstatus == 1) {
            frm.add_custom_button(__('Reverse Transaction'), function() {
                frappe.confirm(
                    __('Are you sure you want to reverse this transaction?'),
                    function() {
                        frappe.call({
                            method: 'frappe.client.insert',
                            args: {
                                doctype: 'Transaction',
                                doc: {
                                    transaction_type: 'Reversal',
                                    amount: frm.doc.amount,
                                    from_account: frm.doc.from_account,
                                    customer: frm.doc.customer,
                                    description: 'Reversal of ' + frm.doc.reference_number,
                                    reversal_of: frm.doc.name,
                                    status: 'Completed'
                                }
                            },
                            callback: function() {
                                frm.reload_doc();
                            }
                        });
                    }
                );
            }, __('Actions'));
        }
    },

    transaction_type: function(frm) {
        if (frm.doc.transaction_type === 'Credit' || frm.doc.transaction_type === 'Refund') {
            frm.set_value('status', 'Completed');
        }
    },

    amount: function(frm) {
        if (frm.doc.amount > 100000) {
            frappe.msgprint(__('Transaction amount exceeds ₹1,00,000. Additional verification may be required.'));
        }
    }
});
