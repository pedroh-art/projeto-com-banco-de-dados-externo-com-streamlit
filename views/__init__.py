# views/__init__.py
from .membro_view import render_membro_view
from .admin_view import render_admin_view

__all__ = ["render_membro_view", "render_admin_view"]