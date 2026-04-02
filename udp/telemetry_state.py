# udp/telemetry_state.py

from typing import Protocol, List
from core.events import EventType


class EventListener(Protocol):
    def handle_event(self, event_type: EventType, **payload):
        ...


class TelemetryState:
    """
    Central telemetry state + event emitter.
    This will be fed by telemetry_manager / udp_listener.
    """

    def __init__(self):
        self._listeners: List[EventListener] = []
        self._last_lap = None
        # add more cached state here (flags, session, etc.)

    def register_listener(self, listener: EventListener):
        self._listeners.append(listener)

    def _emit(self, event_type: EventType, **payload):
        for listener in self._listeners:
            listener.handle_event(event_type, **payload)

    def update_from_packet(self, packet):
        """
        Called by telemetry_manager / udp_listener with decoded packet(s).
        """
        # Example: lap change → LAP_START
        current_lap = getattr(packet, "lap_number", None)
        if current_lap is not None and current_lap != self._last_lap:
            self._last_lap = current_lap
            self._emit(EventType.LAP_START, lap=current_lap)

        # TODO: detect SC/VSC/red flag, pit windows, teammate pitting, etc.
        # and call self._emit(...) with the appropriate EventType.