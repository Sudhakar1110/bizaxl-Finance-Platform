frappe.ui.form.on('Bizaxl Customer', {
    refresh: function(frm) {
        // Add custom buttons
        frm.add_custom_button(__('Bank Accounts'), function() {
            frappe.set_route('List', 'Bank Account', {customer: frm.doc.name});
        }, __('Related'));

        frm.add_custom_button(__('Transactions'), function() {
            frappe.set_route('List', 'Transaction', {customer: frm.doc.name});
        }, __('Related'));

        frm.add_custom_button(__('Insurance Policies'), function() {
            frappe.set_route('List', 'Insurance Policy', {customer: frm.doc.name});
        }, __('Related'));

        frm.add_custom_button(__('Loan Applications'), function() {
            frappe.set_route('List', 'Loan Application', {customer: frm.doc.name});
        }, __('Related'));

        // KYC Verification button
        if (frm.doc.kyc_status == 'Under Review') {
            frm.add_custom_button(__('Approve KYC'), function() {
                frappe.confirm(
                    __('Are you sure you want to approve KYC for {0}?', [frm.doc.customer_name]),
                    function() {
                        frappe.call({
                            method: 'bizaxl_finance.customer_management.doctype.bizaxl_customer.bizaxl_customer.verify_kyc',
                            args: {
                                customer: frm.doc.name,
                                status: 'Verified'
                            },
                            callback: function(r) {
                                frm.reload_doc();
                            }
                        });
                    }
                );
            }, __('KYC'));

            frm.add_custom_button(__('Reject KYC'), function() {
                frappe.prompt([
                    {fieldname: 'reason', fieldtype: 'Small Text', label: 'Rejection Reason', reqd: 1}
                ], function(values) {
                    frappe.call({
                        method: 'bizaxl_finance.customer_management.doctype.bizaxl_customer.bizaxl_customer.verify_kyc',
                        args: {
                            customer: frm.doc.name,
                            status: 'Rejected',
                            reason: values.reason
                        },
                        callback: function(r) {
                            frm.reload_doc();
                        }
                    });
                }, __('Reject KYC'), __('Submit'));
            }, __('KYC'));
        }
    },

    mobile_number: function(frm) {
        // Auto-format mobile number
        if (frm.doc.mobile_number) {
            frm.set_value('mobile_number', frm.doc.mobile_number.replace(/\D/g, ''));
        }
    },

    customer_name: function(frm) {
        // Auto-title case
        if (frm.doc.customer_name) {
            frm.set_value('customer_name', frm.doc.customer_name.replace(/\b\w/g, l => l.toUpperCase()));
        }
    }
});
