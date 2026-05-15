# -*- coding: utf-8 -*-

import omni.ui as ui
import omni.appwindow
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
                    with ui.HStack(height=80, spacing=10):
                        # Botón "+" cuadrado (centrado abajo si es necesario, o lo dejamos estirar. Usamos alignment para que se quede arriba o centrado, pero como no hay, por defecto se estirará o no)
                        with ui.VStack(width=40):
                            ui.Spacer()
                            ui.Button(
                                "+",
                                width=40,
                                height=40,
                                clicked_fn=lambda: print("Abrir explorador de archivos")
                            )

                        # Campo de texto multilinea (más alto para permitir saltos de línea visibles sin scrollear a la izquierda infinito)
                        self._input_field = ui.StringField(multiline=True, height=80, width=ui.Fraction(1), style={"word_wrap": True})
                        self._input_field.model.set_value("")

                        # Botón de enviar
                        with ui.VStack(width=100):
                            ui.Spacer()
                            self._send_button = ui.Button(
                                "Enviar",
                                width=100,
                                height=40,
                                clicked_fn=self._handle_send_clicked
                            )

    def _copy_to_clipboard(self, text_label):
        """Copies the text of a given label to the system clipboard.

        Args:
            text_label (omni.ui.Label): The label widget containing the text to copy.
        """
        try:
            if text_label and hasattr(text_label, "text"):
                app_window = omni.appwindow.get_default_app_window()
                app_window.set_clipboard(text_label.text)
        except Exception as e:
            print(f"Error copying to clipboard: {e}")

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
        """Creates a new message bubble in the UI.

        Args:
            role (str): The role of the message sender. Must be "user" or "assistant".
            text (str, optional): The initial text content of the message bubble. Defaults to "".
        """
        is_user = (role == "user")

        # Determine colors and alignment
        bg_color = 0xFF2B5278 if is_user else 0xFF3A3A3A
        margin_fraction = ui.Fraction(1)
        bubble_fraction = ui.Fraction(4)  # 80% max width (4 out of 5)

        with self._messages_stack:
            with ui.HStack(height=0):
                if is_user:
                    ui.Spacer(width=margin_fraction)

                # VStack acts as a max-width container (80%)
                with ui.VStack(width=bubble_fraction):
                    with ui.HStack(height=0):
                        if is_user:
                            ui.Spacer()

                        # HStack to hold button and bubble side-by-side
                        with ui.HStack(width=0, spacing=5):
                            if is_user:
                                # User copy button on the left
                                with ui.VStack(width=20):
                                    ui.Spacer()
                                    copy_btn = ui.Button(
                                        "",
                                        width=20, height=20,
                                        tooltip="Copiar texto",
                                        style={"font_family": "FontAwesome5Free-Regular", "font_size": 14}
                                    )

                            # The bubble itself. width=0 allows adjusting to content (if short),
                            # but the word_wrap=True allows long text to wrap instead of overflowing horizontally,
                            # confined by the parent VStack(bubble_fraction).
                            with ui.ZStack(width=0):
                                ui.Rectangle(style={"background_color": bg_color, "border_radius": 8})
                                with ui.VStack(padding=10, height=0):
                                    label = ui.Label(
                                        text,
                                        word_wrap=True,
                                        alignment=ui.Alignment.LEFT_TOP,
                                        style={"color": 0xFFFFFFFF, "font_size": 14}
                                    )
                                    if not is_user:
                                        self._message_labels.append(label)

                            if not is_user:
                                # Assistant copy button on the right
                                with ui.VStack(width=20):
                                    ui.Spacer()
                                    copy_btn = ui.Button(
                                        "",
                                        width=20, height=20,
                                        tooltip="Copiar texto",
                                        style={"font_family": "FontAwesome5Free-Regular", "font_size": 14}
                                    )

                            copy_btn.set_clicked_fn(lambda l=label: self._copy_to_clipboard(l))

                        if not is_user:
                            ui.Spacer()

                if not is_user:
                    ui.Spacer(width=margin_fraction)

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
