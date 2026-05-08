# Patrones de Diseño en Omniverse

Este documento establece la micro-arquitectura y los patrones de diseño oficiales a seguir dentro de la capa del motor NVIDIA Omniverse, para mantener la predictibilidad, estabilidad y el control del estado dentro del entorno.

## 1. Patrón Model-Delegate-View (UI)

Toda interfaz gráfica creada dentro de la extensión debe regirse estrictamente bajo el patrón **Model-Delegate-View**, provisto y optimizado por la API de `omni.ui`.

**Justificación:**
Debemos erradicar el concepto de la arquitectura Model-View-Controller (MVC) tradicional del ámbito de desarrollo web al trabajar con la UI del motor de renderizado. El objetivo fundamental en Omniverse es desacoplar el *estado* del chat o flujo de la *representación visual*.
- **Model:** Actúa como la única fuente de verdad (Single Source of Truth) de los datos subyacentes.
- **Delegate:** Contiene la lógica responsable de leer los datos del Model y generar/administrar los componentes (Widgets) que se presentan en pantalla.
- **View:** Muestra la estructura visual construida.

La implementación en la carpeta `ui/` debe ser completamente reactiva y agnóstica de las operaciones, utilizando *Dependency Injection* (Inyección de Dependencias) para propagar los callbacks o notificaciones del usuario hacia los orquestadores externos.

## 2. Patrón de Comando (Command Pattern para OpenUSD)

La Inteligencia Artificial y cualquier módulo de automatización tienen **prohibido modificar la jerarquía OpenUSD directamente con scripts y métodos crudos de la API USD**. Cualquier mutación del estado geométrico o topológico de la escena debe ejecutarse a través de la API `omni.kit.commands`.

**Justificación:**
El uso del *Patrón de Comando* garantiza la persistencia segura de las operaciones. Envolver cada cambio de la IA en un comando de Omniverse es fundamental para registrar las alteraciones dentro del historial (Undo Stack) del motor. Esto permite a los usuarios humanos retroceder los cambios a través de **Ctrl+Z (Deshacer / Rehacer)** si los resultados de la IA son indeseados.

**Ejemplo de Comando de Omniverse (Snippet):**

```python
import omni.kit.commands
from pxr import Sdf

# Ejemplo: Creación asincrónica de un Mesh Primitive de forma segura a través del Command Pattern

def create_mesh_safely(path: str):
    # Nunca instanciar el mesh usando UsdGeom.Mesh.Define() directamente!
    # Envolver la operación dentro del sistema de historial del Kit
    success, result = omni.kit.commands.execute(
        'CreateMeshPrimWithDefaultXform',
        prim_type='Cube',
        prim_path=path,
        select_new_prim=True,
        prepend_default_xform=True
    )

    if success:
        omni.kit.app.get_app().print_and_log(f"Prim creado y registrado en historial: {path}")
    else:
        omni.kit.app.get_app().print_and_log(f"Fallo al ejecutar el comando OpenUSD en {path}", 2) # Error log
```
