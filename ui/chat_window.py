# -*- coding: utf-8 -*-

import omni.ui as ui

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
                            clicked_fn=self._handle_send_clicked
                        )

    def _handle_send_clicked(self):
        """Internal callback for the send button."""
        prompt = self._input_field.model.get_value_as_string()
        if prompt and self._on_send_callback:
            self._on_send_callback(prompt)

    def set_response_text(self, text: str):
        """Updates the main response label."""
        self._response_label.text = text

    def set_button_state(self, processing: bool):
        """
        Toggles the send button state.

        Args:
            processing (bool): If True, disables button and changes text to 'Procesando...'.
        """
        if processing:
            self._send_button.text = "Procesando..."
            self._send_button.enabled = False
        else:
            self._send_button.text = "Enviar"
            self._send_button.enabled = True

    def destroy(self):
        """Cleanup."""
        self._window = None
