# SPDX-FileCopyrightText: Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: LicenseRef-NvidiaProprietary
#
# NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
# property and proprietary rights in and to this material, related
# documentation and any modifications thereto. Any use, reproduction,
# disclosure or distribution of this material and related documentation
# without an express license agreement from NVIDIA CORPORATION or
# its affiliates is strictly prohibited.

# -*- coding: utf-8 -*-

import asyncio
import omni.ext
from .ui.chat_window import ChatWindow
from .logic.agent_manager import AgentManager

class MyExtension(omni.ext.IExt):
    """NVIDIA Omniverse Extension to communicate with LM Studio."""

    def on_startup(self, _ext_id):
        """Called when the extension is enabled."""
        print("[orlandoexplorer.ia_test] LM Studio Extension startup")
        
        self._agent_manager = AgentManager()
        self._chat_window = ChatWindow(on_send_callback=self._on_send_message_callback)

    def _on_send_message_callback(self, prompt: str):
        """Callback triggered by the UI when the user clicks 'Enviar'."""
        self._chat_window.set_response_text("Enviando petición a LM Studio...")
        self._chat_window.set_button_state(processing=True)
        # Launch the async task in the background
        asyncio.ensure_future(self._process_message_async(prompt))

    async def _process_message_async(self, prompt: str):
        """Background task to handle prompt processing without blocking UI."""
        try:
            # We pass a callback so the AgentManager can update the UI directly if retries happen
            final_response = await self._agent_manager.process_prompt(
                prompt,
                update_callback=self._chat_window.set_response_text
            )
            self._chat_window.set_response_text(final_response)
        except Exception as e:
            error_msg = f"Excepción grave en el orquestador: {str(e)}"
            print(f"[orlandoexplorer.ia_test] {error_msg}")
            self._chat_window.set_response_text(error_msg)
        finally:
            if self._chat_window:
                self._chat_window.set_button_state(processing=False)

    def on_shutdown(self):
        """Called when the extension is disabled."""
        print("[orlandoexplorer.ia_test] LM Studio Extension shutdown")
        if hasattr(self, '_chat_window') and self._chat_window:
            self._chat_window.destroy()
            self._chat_window = None
        self._agent_manager = None
