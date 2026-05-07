# Agentic AI Chat for NVIDIA Omniverse

Este proyecto es una implementación avanzada para integrar **Agentes de IA Espacial** dentro del ecosistema de NVIDIA Omniverse. Actúa como un asistente híbrido capaz de mantener conversaciones naturales y generar, ejecutar y corregir código Python dinámicamente para manipular geometría 3D en OpenUSD.

## Arquitectura del Sistema
El sistema emplea una arquitectura asíncrona y tolerante a fallos para garantizar el rendimiento del motor de renderizado:
* **Frontend UI:** Interfaz moderna estilo chat construida con el NVIDIA Omniverse Kit SDK (`omni.ui`), que incluye historial de mensajes y soporte para esperas dinámicas prolongadas.
* **Comunicación Nativa:** Peticiones asíncronas implementadas estrictamente con librerías estándar de Python (`urllib` y `asyncio` con `run_in_executor`) para evitar dependencias externas que rompan el entorno cerrado del motor y sin bloquear el hilo de renderizado principal (Main Thread).
* **Bucle de Reflexión (Self-Healing):** Un sistema de retroalimentación donde, si la IA genera código de OpenUSD inválido, el agente captura el `stack trace` interno de Omniverse y se lo reenvía a sí mismo para intentar autocorregirse de forma autónoma.
* **Motor de Inferencia:** Compatible con cualquier endpoint que respete la estructura de la API de OpenAI. Diseñado principalmente para privacidad total mediante LLMs ejecutados localmente (ej. LM Studio, Ollama), pero fácilmente escalable a APIs en la nube.

## Características Principales
* **Agente Híbrido:** Capaz de responder preguntas generales de forma conversacional, o instanciar y manipular escenarios directamente cuando se le solicita código.
* **Ejecución Dinámica:** Utiliza `exec()` inyectando contextos globales (`omni`, `pxr.Usd`, `pxr.UsdGeom`, `pxr.Gf`) para ejecutar scripts al vuelo.
* **Inferencia Local (Air-Gapped Ready):** Privacidad de datos absoluta procesando parámetros en la red local.
* **Interfaz Profesional:** Paneles desacoplados, botones con retroalimentación de estado ("Procesando...") y timeout dinámico (configurable a +10 minutos para hardware local).

## Requisitos
* Windows 11.
* Tarjeta gráfica NVIDIA RTX (Serie 40 o superior con soporte Ada Lovelace recomendada para modelos pesados locales).
* NVIDIA Omniverse Launcher & Kit App Template.
* Servidor de inferencia activo (ej. LM Studio corriendo un modelo en el puerto `1234`).

## Instalación y Ejecución
1. Clonar el repositorio localmente.
2. Ejecutar `.\repo.bat build` en la terminal para resolver los enlaces simbólicos del SDK y compilar los módulos.
3. Lanzar el entorno de desarrollo mediante el comando `.\repo.bat launch`.
4. Ir al menú **Window > Extensions** y habilitar la extensión `orlandoexplorer.ia_test`.
