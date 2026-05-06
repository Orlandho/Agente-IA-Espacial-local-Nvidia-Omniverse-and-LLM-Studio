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
import aiohttp
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
                        alignment=ui.Alignment.TOP_LEFT
                    )

    def _on_send_clicked(self):
        """Callback for the button click."""
        prompt = self._input_field.model.get_value_as_string()
        if prompt:
            self._response_label.text = "Enviando petición a LM Studio..."
            # Launch the async task in the background
            asyncio.ensure_future(self._send_to_lm_studio(prompt))

    async def _send_to_lm_studio(self, prompt: str):
        """Asynchronous HTTP request to LM Studio local server."""
        url = "http://localhost:1234/v1/chat/completions"
        payload = {
            "model": "local-model",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, timeout=30) as response:
                    if response.status == 200:
                        data = await response.json()
                        # Extract the message content from the JSON response
                        content = data['choices'][0]['message']['content']
                        self._response_label.text = content
                    else:
                        error_text = await response.text()
                        self._response_label.text = f"Error del servidor ({response.status}): {error_text}"
        except Exception as e:
            self._response_label.text = f"Excepción al conectar con LM Studio: {str(e)}"
            print(f"[orlandoexplorer.ia_test] Error: {e}")

    def on_shutdown(self):
        """Called when the extension is disabled."""
        print("[orlandoexplorer.ia_test] LM Studio Extension shutdown")
        self._window = None
