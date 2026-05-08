# -*- coding: utf-8 -*-

import omni.ext
import pxr
from pxr import Usd, UsdGeom, Gf

class USDController:
    """Handles execution of dynamic USD python code."""

    def execute_code(self, python_code: str) -> dict:
        """
        Dynamically executes extracted python code within the Omniverse context.

        Args:
            python_code (str): The code block to execute.

        Returns:
            dict: Structured response indicating success or failure.
        """
        # Prepare execution environment
        exec_globals = {
            "omni": __import__('omni'),
            "pxr": pxr,
            "Usd": Usd,
            "UsdGeom": UsdGeom,
            "Gf": Gf
        }

        try:
            exec(python_code, exec_globals)
            return {"success": True}
        except Exception as exec_err:
            return {"success": False, "error_msg": str(exec_err)}
