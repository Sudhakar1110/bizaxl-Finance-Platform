"""Base Connector — Abstract class for all external API integrations.

Every connector follows the stub-to-live pattern:
    - Stub mode: Works without API keys, returns realistic sample data
    - Live mode: When credentials exist in Integration Settings, makes real API calls

Usage:
    class MyConnector(BaseConnector):
        name = "my_integration"
        label = "My Integration"
        
        def get_data(self):
            if self.is_live:
                return self._live_get_data()
            return self._stub_get_data()
"""

import frappe
from frappe import _
from frappe.utils import today, now_datetime


class BaseConnector:
    """Abstract base for all integration connectors"""
    
    name = None          # Registry key (e.g. "mcx_gold")
    label = None         # Human-readable label (e.g. "MCX Live Gold Rate")
    settings_field = None  # Field name in Integration Settings that holds the API key
    
    def __init__(self):
        if not self.name:
            raise NotImplementedError("Subclass must define 'name'")
        if not self.settings_field:
            raise NotImplementedError("Subclass must define 'settings_field'")
        self._settings = None
    
    @property
    def is_live(self):
        """Check if this integration has credentials configured (live mode)"""
        try:
            settings = self.get_settings()
            return bool(getattr(settings, self.settings_field, None))
        except Exception:
            return False
    
    @property
    def mode(self):
        """Returns 'live' or 'stub'"""
        return "live" if self.is_live else "stub"
    
    def get_settings(self):
        """Get the Integration Settings singleton (lazy loaded)"""
        if not self._settings:
            try:
                self._settings = frappe.get_single_doc("Integration Settings")
            except Exception:
                self._settings = frappe._dict()
        return self._settings
    
    def log_error(self, message, data=None):
        """Log integration error with context"""
        frappe.log_error(
            title=f"[{self.label}] {message}",
            message=f"Mode: {self.mode}\nData: {frappe.as_json(data or {})}"
        )
    
    def http_request(self, method, url, headers=None, data=None, timeout=30):
        """Make an HTTP request with error handling.
        
        Only used in live mode. Protected against import errors.
        """
        try:
            import requests
            response = requests.request(
                method=method.upper(),
                url=url,
                headers=headers or {},
                json=data,
                timeout=timeout,
            )
            response.raise_for_status()
            return response.json()
        except ImportError:
            self.log_error("requests library not installed", {"url": url})
            return {"error": "requests library not available"}
        except Exception as e:
            self.log_error(f"HTTP request failed: {e}", {"url": url, "method": method})
            return {"error": str(e)}
    
    def stub_response(self, data, message="Simulated response (no API key configured)"):
        """Wrap stub data with metadata"""
        return {
            "mode": "stub",
            "message": message,
            "data": data,
            "timestamp": str(now_datetime()),
        }
