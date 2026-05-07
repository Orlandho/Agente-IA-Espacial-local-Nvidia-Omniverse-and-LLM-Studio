# Local AI Chat For Nvidia Omniverse

Este proyecto es una implementación de investigación para integrar Agentes de IA Espacial dentro del ecosistema de NVIDIA Omniverse utilizando modelos de lenguaje (LLM) ejecutados localmente.

## Arquitectura del Sistema
El sistema emplea una arquitectura desacoplada para garantizar el rendimiento del motor de renderizado:
* **Frontend:** NVIDIA Omniverse Kit SDK (Python).
* **Comunicación:** Peticiones asíncronas vía `aiohttp` para evitar el bloqueo del hilo de renderizado principal.
* **Inferencia:** Servidor local compatible con OpenAI API (LM Studio) ejecutando Gemma 4.

## Características Principales
* **Interfaz Asíncrona:** UI construida con `omni.ui` que no se congela durante la inferencia de la IA.
* **Inferencia Local:** Privacidad total y baja latencia al procesar datos sin salir de la red local (Air-gapped ready).
* **Extensibilidad:** Diseñado como un módulo de Omniverse para futura manipulación de objetos OpenUSD mediante código generado por IA.

## Requisitos
* Windows 11.
* Tarjeta gráfica NVIDIA RTX (Serie 40 o superior con soporte Ada Lovelace).
* Kit App Template (NVIDIA Kit SDK).
* LM Studio con servidor activo en puerto 1234.

## Instalación y Ejecución
1. Clonar el repositorio.
2. Ejecutar `.\repo.bat build` para resolver las dependencias del SDK y compilar los módulos.
3. Lanzar el entorno de desarrollo con el comando `.\repo.bat launch`.
4. Habilitar la extensión `orlandoexplorer.ia_test` desde el Gestor de Extensiones.
