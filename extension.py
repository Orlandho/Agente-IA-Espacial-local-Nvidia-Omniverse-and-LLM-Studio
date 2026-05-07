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
import re
import omni.ext
import omni.ui as ui
import pxr
from pxr import Usd, UsdGeom, Gf


class MyExtension(omni.ext.IExt):
    """NVIDIA Omniverse Extension to communicate with LM Studio."""

    def on_startup(self, _ext_id):
        """Called when the extension is enabled."""
        print("[orlandoexplorer.ia_test] LM Studio Extension startup")

        self._window = ui.Window("IA Test LM Studio", width=800, height=600)
        
        with self._window.frame:
            with ui.HStack():
                # Panel Izquierdo (Barra lateral)
                with ui.VStack(width=200, style={"background_color": 0xFF1E1E1E}, padding=10, spacing=10):
                    ui.Button("Nuevo Chat", height=30)
                    ui.Spacer()
                    ui.Button("Configuraciones", height=30)
                
                # Panel Derecho (Principal)
                with ui.VStack(width=ui.Fraction(1), spacing=10, padding=10):
                    # Historial de mensajes (ScrollingFrame)
                    with ui.ScrollingFrame(height=ui.Fraction(1), style={"background_color": 0xFF222222}):
                        self._response_label = ui.Label(
                            "Esperando entrada...",
                            word_wrap=True,
                            alignment=ui.Alignment.LEFT_TOP
                        )

                    # Controles de entrada (Abajo)
                    with ui.HStack(height=40, spacing=10):
                        # Botón "+" cuadrado
                        ui.Button(
                            "+",
                            width=40,
                            height=40,
                            clicked_fn=lambda: print("Abrir explorador de archivos")
                        )

                        # Campo de texto multilinea
                        self._input_field = ui.StringField(multiline=True, height=40, width=ui.Fraction(1))
                        self._input_field.model.set_value("Hola, ¿cómo estás?")

                        # Botón de enviar
                        self._send_button = ui.Button(
                            "Enviar",
                            width=100,
                            height=40,
                            clicked_fn=self._on_send_clicked
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

        system_prompt = (
            "Eres un experto desarrollador de Python para NVIDIA Omniverse. "
            "Tu tarea es generar código Python válido para manipular escenas en Omniverse basándote en la petición del usuario. "
            "Debes utilizar omni.usd.get_context().get_stage() y las clases correspondientes de pxr (como UsdGeom.Cube, UsdGeom.Sphere, etc.). "
            "Tienes prohibido incluir explicaciones, saludos o cualquier texto adicional. "
            "Debes responder única y estrictamente con un bloque de código Python delimitado por ```python y ```."
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]

        max_retries = 2
        loop = asyncio.get_event_loop()

        for attempt in range(max_retries + 1):
            payload = {
                "model": "local-model",
                "messages": messages,
                "temperature": 0.7
            }

            try:
                # Run the synchronous request in a background thread
                result = await loop.run_in_executor(None, self._make_sync_request, url, payload)

                if result.get("success"):
                    data = result.get("data", {})
                    content = data.get('choices', [{}])[0].get('message', {}).get('content', '')

                    # Extract Python code using regex
                    match = re.search(r'```python\s*(.*?)\s*```', content, re.DOTALL)
                    if match:
                        extracted_code = match.group(1).strip()

                        # Prepare execution environment
                        exec_globals = {
                            "omni": omni,
                            "pxr": pxr,
                            "Usd": Usd,
                            "UsdGeom": UsdGeom,
                            "Gf": Gf
                        }

                        try:
                            # Dynamically execute the extracted code
                            exec(extracted_code, exec_globals)
                            self._response_label.text = f"Código ejecutado exitosamente:\n{extracted_code}"
                            break  # Exit loop on success
                        except Exception as exec_err:
                            error_msg = str(exec_err)
                            print(f"[orlandoexplorer.ia_test] Error en la ejecución del código: {error_msg}")
                            print(f"[orlandoexplorer.ia_test] Código que falló:\n{extracted_code}")

                            if attempt < max_retries:
                                self._response_label.text = f"Error detectado. Intento de autocorrección {attempt + 1} de {max_retries}..."
                                messages.append({"role": "assistant", "content": content})
                                messages.append({
                                    "role": "user",
                                    "content": f"El código falló al ejecutarse en Omniverse con este error: {error_msg}. Analiza el error, asegúrate de usar correctamente la API de pxr/omni.usd y devuelve ÚNICAMENTE el código corregido dentro de ```python ... ```."
                                })
                            else:
                                final_err = f"Se agotaron los reintentos. Último error: {error_msg}"
                                self._response_label.text = final_err
                                print(f"[orlandoexplorer.ia_test] {final_err}")
                                break
                    else:
                        error_msg = "Error de formato: No se encontró ningún bloque de código ejecutable."
                        print(f"[orlandoexplorer.ia_test] {error_msg}\nRespuesta original:\n{content}")

                        if attempt < max_retries:
                            self._response_label.text = f"Error detectado. Intento de autocorrección {attempt + 1} de {max_retries}..."
                            messages.append({"role": "assistant", "content": content})
                            messages.append({
                                "role": "user",
                                "content": "Error de formato: No se encontró ningún bloque de código ejecutable. Recuerda tu instrucción principal: responde ÚNICAMENTE con código Python encerrado entre las etiquetas ```python y ```, sin texto adicional."
                            })
                        else:
                            final_err = f"Se agotaron los reintentos. Último error: {error_msg}"
                            self._response_label.text = final_err
                            print(f"[orlandoexplorer.ia_test] {final_err}")
                            break
                else:
                    error_type = result.get("error_type")
                    if error_type == "HTTPError":
                        self._response_label.text = f"Error del servidor ({result.get('status')}): {result.get('message')}"
                    elif error_type == "URLError":
                        self._response_label.text = f"Error de URL al conectar con LM Studio: {result.get('message')}"
                    else:
                        self._response_label.text = f"Excepción al conectar con LM Studio: {result.get('message')}"
                        print(f"[orlandoexplorer.ia_test] Error: {result.get('message')}")
                    break  # Break on network/API errors

            except Exception as e:
                self._response_label.text = f"Excepción en la ejecución asíncrona: {str(e)}"
                print(f"[orlandoexplorer.ia_test] Error asíncrono: {e}")
                break  # Break on unexpected asyncio errors

    def on_shutdown(self):
        """Called when the extension is disabled."""
        print("[orlandoexplorer.ia_test] LM Studio Extension shutdown")
        self._window = None
