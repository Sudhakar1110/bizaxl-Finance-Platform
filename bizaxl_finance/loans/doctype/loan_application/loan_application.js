frappe.ui.form.on('Loan Application', {
    refresh: function(frm) {
        if (frm.doc.status == 'Under Review') {
            frm.add_custom_button(__('Approve'), function() {
                frappe.confirm(__('Approve this loan application?'), function() {
                    frm.set_value('status', 'Approved');
                    frm.set_value('approval_date', frappe.datetime.get_today());
                    frm.set_value('approved_by', frappe.session.user);
                    frm.save();
                });
            }, __('Actions'));

            frm.add_custom_button(__('Reject'), function() {
                frappe.prompt([
                    {fieldname: 'reason', fieldtype: 'Small Text', label: 'Rejection Reason', reqd: 1}
                ], function(values) {
                    frm.set_value('status', 'Rejected');
                    frm.set_value('rejection_reason', values.reason);
                    frm.save();
                }, __('Reject Loan'), __('Submit'));
            }, __('Actions'));
        }

        if (frm.doc.status == 'Approved') {
            frm.add_custom_button(__('Disburse Loan'), function() {
                frappe.call({
                    method: 'frappe.client.insert',
                    args: {
                        doctype: 'Loan Disbursement',
                        doc: {
                            loan_application: frm.doc.name,
                            customer: frm.doc.customer,
                            disbursement_amount: frm.doc.loan_amount,
                            interest_rate: frm.doc.interest_rate,
                            tenure_months: frm.doc.tenure_months
                        }
                    },
                    callback: function(r) {
                        frappe.set_route('Form', 'Loan Disbursement', r.message.name);
                    }
                });
            }, __('Actions'));
        }
    },

    loan_product: function(frm) {
        if (frm.doc.loan_product) {
            frappe.call({
                method: 'frappe.client.get',
                args: {
                    doctype: 'Loan Product',
                    name: frm.doc.loan_product
                },
                callback: function(r) {
                    var product = r.message;
                    frm.set_value('interest_rate', product.interest_rate);
                    frm.set_value('loan_type', product.loan_type);
                }
            });
        }
    },

    loan_amount: function(frm) {
        frm.trigger('calculate_emi');
    },

    interest_rate: function(frm) {
        frm.trigger('calculate_emi');
    },

    tenure_months: function(frm) {
        frm.trigger('calculate_emi');
    },

    calculate_emi: function(frm) {
        // Trigger server-side calculation
        if (frm.doc.loan_amount && frm.doc.interest_rate && frm.doc.tenure_months) {
            frm.call({
                method: 'calculate_emi',
                doc: frm.doc,
                callback: function(r) {
                    frm.refresh_field('emi_amount');
                    frm.refresh_field('total_interest');
                    frm.refresh_field('total_payable');
                }
            });
        }
    }
});
