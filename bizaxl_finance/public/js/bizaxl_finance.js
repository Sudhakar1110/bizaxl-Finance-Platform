// Bizaxl Finance Platform - Global Custom Scripts
frappe.provide('bizaxl_finance');

// Add custom utilities
bizaxl_finance.utils = {
    format_currency: function(amount, currency) {
        currency = currency || '₹';
        return currency + ' ' + Number(amount).toLocaleString('en-IN');
    },

    validate_upi: function(upi_id) {
        return /^[\w.-]+@[\w.-]+$/.test(upi_id);
    },

    validate_pan: function(pan) {
        return /^[A-Z]{5}[0-9]{4}[A-Z]{1}$/.test(pan);
    },

    validate_mobile: function(mobile) {
        return /^[6-9]\d{9}$/.test(mobile);
    }
};

// Add dashboard chart renderer
bizaxl_finance.render_portfolio_chart = function(data, element) {
    // Portfolio chart rendering logic
};
