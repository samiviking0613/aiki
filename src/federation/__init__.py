# AIKI Federation - Pheromone Protocol
"""
Federation-lag for AIKI-HOME distribuert system.

Gir kommunikasjon mellom lokale AIKI-HOME instanser og sentral Prime.
"""

from .pheromone_protocol import PheromoneProtocol, PheromoneMessage, SyncDirection

__all__ = ['PheromoneProtocol', 'PheromoneMessage', 'SyncDirection']
