# -*- coding: utf-8 -*-

import asyncio
import re
from .network_client import NetworkClient
from .usd_controller import USDController

class AgentManager:
    """Orchestrates conversations and Reflection Loop logic."""

    def __init__(self):
        self._network_client = NetworkClient()
        self._usd_controller = USDController()
        self._system_prompt = (
            "Eres un asistente de IA avanzado para NVIDIA Omniverse. Puedes conversar libremente y ayudar al usuario con cualquier duda. "
            "SIN EMBARGO, si el usuario te pide crear, instanciar o modificar objetos 3D, debes cumplir su orden escribiendo el código en Python "
            "usando omni.usd y pxr dentro de un bloque delimitado por ```python y ```. Puedes acompañar el código con una explicación amigable."
        )
        self._messages = [{"role": "system", "content": self._system_prompt}]
        self._url = "http://localhost:1234/v1/chat/completions"

    async def process_prompt(self, prompt: str, append_callback=None, ui_feedback_callback=None) -> str:
        """
        Asynchronously processes a prompt, communicates with the LM, and handles the ReAct loop.

        Args:
            prompt (str): The user input prompt.
            append_callback (callable, optional): Callback to append text chunks to the UI bubble.
            ui_feedback_callback (callable, optional): Callback to add a new message/bubble to the UI (e.g. for errors/system).

        Returns:
            str: The final response (used primarily for error handling or fallback if streaming fails).
        """
        self._messages.append({"role": "user", "content": prompt})

        max_retries = 2

        for attempt in range(max_retries + 1):
            payload = {
                "model": "local-model",
                "messages": self._messages,
                "temperature": 0.7
            }

            try:
                full_content = ""
                error_occurred = False
                error_message = ""

                # Stream the response
                async for chunk_obj in self._network_client.stream_request(self._url, payload):
                    if chunk_obj.get("success"):
                        data = chunk_obj.get("data", {})

                        # Handle different streaming JSON structures
                        choices = data.get('choices', [{}])
                        if choices:
                            delta = choices[0].get('delta', {})
                            chunk = delta.get('content', '')

                            if chunk:
                                full_content += chunk
                                if append_callback:
                                    append_callback(chunk)
                    else:
                        error_occurred = True
                        error_type = chunk_obj.get("error_type")
                        if error_type == "HTTPError":
                            error_message = f"Error del servidor ({chunk_obj.get('status')}): {chunk_obj.get('message')}"
                        elif error_type == "URLError":
                            error_message = f"Error de URL al conectar con LM Studio: {chunk_obj.get('message')}"
                        else:
                            print(f"[orlandoexplorer.ia_test] Error: {chunk_obj.get('message')}")
                            error_message = f"Excepción al conectar con LM Studio: {chunk_obj.get('message')}"
                        break

                if error_occurred:
                     return error_message

                # Wait slightly for UI to catch up after stream completion
                await asyncio.sleep(0.1)

                # Check for python code to execute
                match = re.search(r'```python\s*(.*?)\s*```', full_content, re.DOTALL)
                if match:
                    extracted_code = match.group(1).strip()
                    exec_result = self._usd_controller.execute_code(extracted_code)

                    if exec_result.get("success"):
                        self._messages.append({"role": "assistant", "content": full_content})
                        success_msg = "\n\n[Sistema: Código ejecutado exitosamente]"
                        if append_callback:
                            append_callback(success_msg)
                        return full_content + success_msg
                    else:
                        error_msg = exec_result.get("error_msg")
                        print(f"[orlandoexplorer.ia_test] Error en la ejecución del código: {error_msg}")
                        print(f"[orlandoexplorer.ia_test] Código que falló:\n{extracted_code}")

                        if attempt < max_retries:
                            retry_msg = f"\n\n[Sistema: Error detectado. Intento de autocorrección {attempt + 1} de {max_retries}...]"
                            if append_callback:
                                append_callback(retry_msg)

                            self._messages.append({"role": "assistant", "content": full_content})
                            self._messages.append({
                                "role": "user",
                                "content": f"El código falló con este error: {error_msg}. Por favor, analiza el problema y devuelve el código corregido dentro de las etiquetas ```python y ```."
                            })

                            # Give UI time to update before the next attempt starts streaming
                            await asyncio.sleep(0.5)

                            if ui_feedback_callback:
                                # Add a new empty bubble for the assistant's next response
                                ui_feedback_callback("assistant", "")
                        else:
                            final_err = f"\n\n[Sistema: Se agotaron los reintentos. Último error: {error_msg}]"
                            if append_callback:
                                append_callback(final_err)
                            print(f"[orlandoexplorer.ia_test] {final_err}")
                            return full_content + final_err
                else:
                    # No code block found, treat as normal conversation
                    self._messages.append({"role": "assistant", "content": full_content})
                    return full_content

            except Exception as e:
                print(f"[orlandoexplorer.ia_test] Error asíncrono: {e}")
                return f"Excepción en la ejecución asíncrona: {str(e)}"

        return "Flujo finalizado inesperadamente."
