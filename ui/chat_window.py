# -*- coding: utf-8 -*-

import omni.ui as ui
import asyncio

class ChatWindow:
    """Handles the UI setup and element state modifications."""

    def __init__(self, on_send_callback):
        """
        Initializes the UI.

        Args:
            on_send_callback (callable): Function to call when the send button is clicked.
        """
        self._on_send_callback = on_send_callback
        self._window = ui.Window("IA Test LM Studio", width=800, height=600)
        self._message_labels = [] # To keep track of the labels representing messages

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
                    self._scrolling_frame = ui.ScrollingFrame(
                        height=ui.Fraction(1),
                        style={"background_color": 0xFF222222},
                        horizontal_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_OFF,
                        vertical_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_AS_NEEDED,
                    )
                    with self._scrolling_frame:
                        self._messages_stack = ui.VStack(spacing=10, padding=10)

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
                        self._input_field.model.set_value("")

                        # Botón de enviar
                        self._send_button = ui.Button(
                            "Enviar",
                            width=100,
                            height=40,
                            clicked_fn=self._handle_send_clicked
                        )

    def _handle_send_clicked(self):
        """Internal callback for the send button."""
        prompt = self._input_field.model.get_value_as_string()
        if prompt and prompt.strip() and self._on_send_callback:
            self._input_field.model.set_value("") # Clear input
            self._on_send_callback(prompt)

    def _scroll_to_bottom(self):
        """Forces the ScrollingFrame to scroll to the bottom."""
        # Using a slight delay allows the layout to update before scrolling
        async def scroll_down():
            await asyncio.sleep(0.01)
            try:
                if self._scrolling_frame:
                    self._scrolling_frame.scroll_y_max = 1000000.0 # Force max recalculation
                    self._scrolling_frame.scroll_y = self._scrolling_frame.scroll_y_max
            except Exception:
                pass

        asyncio.ensure_future(scroll_down())

    def add_message_bubble(self, role: str, text: str = ""):
        """
        Creates a new message bubble in the UI.

        Args:
            role (str): "user" or "assistant".
            text (str): Initial text of the bubble.
        """
        is_user = (role == "user")

        # Determine alignment and colors
        alignment = ui.Alignment.RIGHT if is_user else ui.Alignment.LEFT
        bg_color = 0xFF444444 if is_user else 0xFF2A2A2A
        margin_width = ui.Fraction(1)

        with self._messages_stack:
            with ui.HStack():
                if is_user:
                    ui.Spacer(width=margin_width)

                with ui.ZStack(width=0): # Auto-sizing container
                    ui.Rectangle(style={"background_color": bg_color, "border_radius": 8})
                    with ui.VStack(padding=10):
                        label = ui.Label(
                            text,
                            word_wrap=True,
                            alignment=ui.Alignment.LEFT_TOP,
                            style={"color": 0xFFFFFFFF, "font_size": 14}
                        )
                        # We keep a reference if we need to stream into it.
                        # We only stream to assistant, but we keep track anyway.
                        if role == "assistant":
                            self._message_labels.append(label)

                if not is_user:
                    ui.Spacer(width=margin_width)

        self._scroll_to_bottom()

    def append_to_last_message(self, chunk: str):
        """
        Appends text to the last assistant message bubble.

        Args:
            chunk (str): The text chunk to append.
        """
        if self._message_labels:
            last_label = self._message_labels[-1]
            last_label.text += chunk
            self._scroll_to_bottom()

    def set_button_state(self, processing: bool):
        """
        Toggles the send button state.

        Args:
            processing (bool): If True, disables button and changes text to 'Procesando...'.
        """
        try:
            if processing:
                self._send_button.text = "Procesando..."
                self._send_button.enabled = False
            else:
                self._send_button.text = "Enviar"
                self._send_button.enabled = True
        finally:
            # Ensure safe exit if things go wrong
            pass

    def destroy(self):
        """Cleanup."""
        self._window = None
