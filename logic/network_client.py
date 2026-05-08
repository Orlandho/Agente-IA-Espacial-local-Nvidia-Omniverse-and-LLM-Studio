# -*- coding: utf-8 -*-

import urllib.request
import urllib.error
import json

class NetworkClient:
    """Handles network communication with external services."""

    def make_sync_request(self, url: str, payload: dict) -> dict:
        """
        Synchronous HTTP request using urllib.

        Args:
            url (str): The destination URL.
            payload (dict): The JSON payload.

        Returns:
            dict: Structured response indicating success, data, or error details.
        """
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(
            url,
            data=data,
            headers={'Content-Type': 'application/json; charset=utf-8'},
            method='POST'
        )

        try:
            # Enforce 600 seconds timeout as specified
            with urllib.request.urlopen(req, timeout=600) as response:
                response_body = response.read().decode('utf-8')
                return {"success": True, "data": json.loads(response_body)}
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8') if e.fp else str(e)
            return {"success": False, "error_type": "HTTPError", "status": e.code, "message": error_body}
        except urllib.error.URLError as e:
            return {"success": False, "error_type": "URLError", "message": str(e.reason)}
        except Exception as e:
            return {"success": False, "error_type": "Exception", "message": str(e)}
