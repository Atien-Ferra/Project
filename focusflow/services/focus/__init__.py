"""
Focus session service module.
Handles focus session modes and recording.
"""
from .session import get_focus_modes, record_focus_session, FOCUS_MODES

__all__ = ['get_focus_modes', 'record_focus_session', 'FOCUS_MODES']
