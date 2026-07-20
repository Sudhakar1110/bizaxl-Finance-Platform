frappe.ui.form.on('Loan Disbursement', {
    refresh: function(frm) {
        if (frm.doc.status == 'Pending') {
            frm.add_custom_button(__('Disburse Now'), function() {
                frm.savesubmit();
            }, __('Actions'));
        }
    }
});
