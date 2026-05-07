# SPDX-FileCopyrightText: Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: LicenseRef-NvidiaProprietary
#
# NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
# property and proprietary rights in and to this material, related
# documentation and any modifications thereto. Any use, reproduction,
# disclosure or distribution of this material and related documentation
# without an express license agreement from NVIDIA CORPORATION or
# its affiliates is strictly prohibited.

import asyncio
import urllib.request
import urllib.error
import json
import omni.ext
import omni.ui as ui


class MyExtension(omni.ext.IExt):
    """NVIDIA Omniverse Extension to communicate with LM Studio."""

    def on_startup(self, _ext_id):
        """Called when the extension is enabled."""
        print("[orlandoexplorer.ia_test] LM Studio Extension startup")

        self._window = ui.Window("IA Test LM Studio", width=400, height=450)
        
        with self._window.frame:
            with ui.VStack(spacing=10, padding=10):
                ui.Label("Prompt para LM Studio:", height=20)
                
                # Multi-line StringField for user input
                self._input_field = ui.StringField(multiline=True, height=150)
                self._input_field.model.set_value("Hola, ¿cómo estás?")
                
                # Send Button
                self._send_button = ui.Button(
                    "Enviar a LM Studio", 
                    clicked_fn=self._on_send_clicked,
                    height=40
                )
                
                ui.Label("Respuesta:", height=20)
                
                # Response Label with word wrap
                with ui.ScrollingFrame(height=200, style={"background_color": 0xFF222222}):
                    self._response_label = ui.Label(
                        "Esperando entrada...", 
                        word_wrap=True, 
                        alignment=ui.Alignment.LEFT_TOP
                    )

    def _on_send_clicked(self):
        """Callback for the button click."""
        prompt = self._input_field.model.get_value_as_string()
        if prompt:
            self._response_label.text = "Enviando petición a LM Studio..."
            # Launch the async task in the background
            asyncio.ensure_future(self._send_to_lm_studio(prompt))

    def _make_sync_request(self, url: str, payload: dict) -> dict:
        """Synchronous HTTP request using urllib."""
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'}, method='POST')

        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                response_body = response.read().decode('utf-8')
                return {"success": True, "data": json.loads(response_body)}
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8') if e.fp else str(e)
            return {"success": False, "error_type": "HTTPError", "status": e.code, "message": error_body}
        except urllib.error.URLError as e:
            return {"success": False, "error_type": "URLError", "message": str(e.reason)}
        except Exception as e:
            return {"success": False, "error_type": "Exception", "message": str(e)}

    async def _send_to_lm_studio(self, prompt: str):
        """Asynchronous HTTP request to LM Studio local server without blocking UI."""
        url = "http://localhost:1234/v1/chat/completions"
        payload = {
            "model": "local-model",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7
        }

        loop = asyncio.get_event_loop()

        try:
            # Run the synchronous request in a background thread
            result = await loop.run_in_executor(None, self._make_sync_request, url, payload)

            if result.get("success"):
                data = result.get("data", {})
                content = data.get('choices', [{}])[0].get('message', {}).get('content', '')
                self._response_label.text = content
            else:
                error_type = result.get("error_type")
                if error_type == "HTTPError":
                    self._response_label.text = f"Error del servidor ({result.get('status')}): {result.get('message')}"
                elif error_type == "URLError":
                    self._response_label.text = f"Error de URL al conectar con LM Studio: {result.get('message')}"
                else:
                    self._response_label.text = f"Excepción al conectar con LM Studio: {result.get('message')}"
                    print(f"[orlandoexplorer.ia_test] Error: {result.get('message')}")

        except Exception as e:
            self._response_label.text = f"Excepción en la ejecución asíncrona: {str(e)}"
            print(f"[orlandoexplorer.ia_test] Error asíncrono: {e}")

    def on_shutdown(self):
        """Called when the extension is disabled."""
        print("[orlandoexplorer.ia_test] LM Studio Extension shutdown")
        self._window = None
