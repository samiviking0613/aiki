# AIKI-HOME Tools
"""
Verktøy for lokal AIKI-HOME installasjon.

Disse kjører på brukerens enhet (Raspberry Pi, PC, etc.)
og samler data som aldri forlater enheten (GDPR).
"""

from .input_activity_monitor import InputActivityMonitor

__all__ = ['InputActivityMonitor']
