# Agentic AI Chat for NVIDIA Omniverse

This project is an advanced implementation to integrate **Spatial AI Agents** within the NVIDIA Omniverse ecosystem. It acts as a hybrid assistant capable of maintaining natural conversations and dynamically generating, executing, and correcting Python code to manipulate 3D geometry in OpenUSD.

## System Architecture
The system employs an asynchronous and fault-tolerant architecture to ensure the performance of the rendering engine:
* **Frontend UI:** Modern chat-style interface built with the NVIDIA Omniverse Kit SDK (`omni.ui`), including message history and support for long dynamic wait times.
* **Native Communication:** Asynchronous requests strictly implemented with standard Python libraries (`urllib` and `asyncio` with `run_in_executor`) to avoid external dependencies that break the engine's closed environment, without blocking the main rendering thread.
* **Reflection Loop (Self-Healing):** A feedback system where, if the AI generates invalid OpenUSD code, the agent captures Omniverse's internal `stack trace` and sends it back to itself to attempt autonomous self-correction.
* **Inference Engine:** Compatible with any endpoint that respects the OpenAI API structure. Primarily designed for total privacy using locally run LLMs (e.g., LM Studio, Ollama), but easily scalable to cloud APIs.

## Key Features
* **Hybrid Agent:** Capable of answering general questions conversationally, or instantiating and manipulating stages directly when code is requested.
* **Dynamic Execution:** Uses `exec()` by injecting global contexts (`omni`, `pxr.Usd`, `pxr.UsdGeom`, `pxr.Gf`) to run scripts on the fly.
* **Local Inference (Air-Gapped Ready):** Absolute data privacy by processing parameters on the local network.
* **Professional Interface:** Decoupled panels, buttons with state feedback ("Processing..."), and dynamic timeout (configurable to 10+ minutes for local hardware).

## Requirements
* Windows 11.
* NVIDIA RTX graphics card (40 Series or higher with Ada Lovelace support recommended for heavy local models).
* NVIDIA Omniverse Launcher & Kit App Template.
* Active inference server (e.g., LM Studio running a model on port `1234`).

## Installation and Execution
1. Clone the repository locally.
2. Run `.\repo.bat build` in the terminal to resolve SDK symlinks and build the modules.
3. Launch the development environment using the command `.\repo.bat launch`.
4. Go to the **Window > Extensions** menu and enable the `orlandoexplorer.ia_test` extension.
