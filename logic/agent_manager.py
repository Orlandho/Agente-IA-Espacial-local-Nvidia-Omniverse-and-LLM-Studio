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

    async def process_prompt(self, prompt: str, update_callback=None) -> str:
        """
        Asynchronously processes a prompt, communicates with the LM, and handles the ReAct loop.

        Args:
            prompt (str): The user input prompt.
            update_callback (callable, optional): Callback to update UI during retries.

        Returns:
            str: The final response to be displayed on the UI.
        """
        self._messages.append({"role": "user", "content": prompt})

        max_retries = 2
        loop = asyncio.get_event_loop()

        for attempt in range(max_retries + 1):
            payload = {
                "model": "local-model",
                "messages": self._messages,
                "temperature": 0.7
            }

            try:
                # Run the synchronous request in a background thread
                result = await loop.run_in_executor(
                    None,
                    self._network_client.make_sync_request,
                    self._url,
                    payload
                )

                if result.get("success"):
                    data = result.get("data", {})
                    content = data.get('choices', [{}])[0].get('message', {}).get('content', '')

                    # Extract Python code using regex
                    match = re.search(r'```python\s*(.*?)\s*```', content, re.DOTALL)
                    if match:
                        extracted_code = match.group(1).strip()

                        exec_result = self._usd_controller.execute_code(extracted_code)

                        if exec_result.get("success"):
                            self._messages.append({"role": "assistant", "content": content})
                            return content + "\n\n[Sistema: Código ejecutado exitosamente]"
                        else:
                            error_msg = exec_result.get("error_msg")
                            print(f"[orlandoexplorer.ia_test] Error en la ejecución del código: {error_msg}")
                            print(f"[orlandoexplorer.ia_test] Código que falló:\n{extracted_code}")

                            if attempt < max_retries:
                                if update_callback:
                                    update_callback(f"Error detectado. Intento de autocorrección {attempt + 1} de {max_retries}...")
                                self._messages.append({"role": "assistant", "content": content})
                                self._messages.append({
                                    "role": "user",
                                    "content": f"El código falló con este error: {error_msg}. Por favor, analiza el problema y devuelve el código corregido dentro de las etiquetas ```python y ```."
                                })
                            else:
                                final_err = f"Se agotaron los reintentos. Último error: {error_msg}"
                                print(f"[orlandoexplorer.ia_test] {final_err}")
                                return final_err
                    else:
                        # No code block found, treat as normal conversation
                        self._messages.append({"role": "assistant", "content": content})
                        return content
                else:
                    error_type = result.get("error_type")
                    if error_type == "HTTPError":
                        return f"Error del servidor ({result.get('status')}): {result.get('message')}"
                    elif error_type == "URLError":
                        return f"Error de URL al conectar con LM Studio: {result.get('message')}"
                    else:
                        print(f"[orlandoexplorer.ia_test] Error: {result.get('message')}")
                        return f"Excepción al conectar con LM Studio: {result.get('message')}"

            except Exception as e:
                print(f"[orlandoexplorer.ia_test] Error asíncrono: {e}")
                return f"Excepción en la ejecución asíncrona: {str(e)}"

        return "Flujo finalizado inesperadamente."
