frappe.ui.form.on('Bill Payment', {
    refresh: function(frm) {
        if (frm.doc.docstatus == 0 && frm.doc.status == 'Overdue') {
            frm.add_custom_button(__('Pay Now'), function() {
                frm.savesubmit();
            }, __('Actions'));
        }
    },

    amount: function(frm) {
        frm.trigger('calculate_total');
    },

    late_fee: function(frm) {
        frm.trigger('calculate_total');
    },

    discount: function(frm) {
        frm.trigger('calculate_total');
    },

    calculate_total: function(frm) {
        var total = flt(frm.doc.amount) + flt(frm.doc.late_fee) - flt(frm.doc.discount);
        frm.set_value('total_amount', total);
    },

    bill_type: function(frm) {
        if (frm.doc.bill_type == 'Electricity') {
            frm.set_value('category', 'Utility');
        } else if (frm.doc.bill_type == 'Mobile Prepaid') {
            frm.set_value('category', 'Mobile Recharge');
        }
    }
});
