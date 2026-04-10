# udp/telemetry_state.py

import threading
from typing import Protocol, List, Optional
from core.events import EventType
from udp.packet_definitions import (
    PacketMotionData,
    PacketSessionData,
    PacketLapData,
    PacketEventData,
    PacketParticipantsData,
    PacketCarSetupData,
    PacketCarTelemetryData,
    PacketCarStatusData,
    PacketFinalClassificationData,
    PacketLobbyInfoData,
    PacketCarDamageData,
    PacketSessionHistoryData,
    PacketTyreSetsData,
    PacketMotionExData,
    PacketTimeTrialData,
    PacketLapPositionsData,
    SafetyCarStatus,
)


TEAM_NAMES = {
    0: "Mercedes",
    1: "Ferrari",
    2: "Red Bull",
    3: "McLaren",
    4: "Aston Martin",
    5: "Alpine",
    6: "Williams",
    7: "Haas",
    8: "Kick Sauber",
    9: "Racing Bulls",
}


class EventListener(Protocol):
    def handle_event(self, event_type: EventType, **payload):
        ...


class TelemetryState:
    """
    Central telemetry state + event emitter.
    Thread-safe via RLock for multi-threaded access.
    """

    def __init__(self):
        self._lock = threading.RLock()
        self._listeners: List[EventListener] = []

        # Flags
        self._participants_ready = False

        # Cached packets
        self.motion: Optional[PacketMotionData] = None
        self.session: Optional[PacketSessionData] = None
        self.lap_data: Optional[PacketLapData] = None
        self.event: Optional[PacketEventData] = None
        self.participants: Optional[PacketParticipantsData] = None
        self.car_setups: Optional[PacketCarSetupData] = None
        self.car_telemetry: Optional[PacketCarTelemetryData] = None
        self.car_status: Optional[PacketCarStatusData] = None
        self.final_classification: Optional[PacketFinalClassificationData] = None
        self.lobby_info: Optional[PacketLobbyInfoData] = None
        self.car_damage: Optional[PacketCarDamageData] = None
        self.session_history: Optional[PacketSessionHistoryData] = None
        self.tyre_sets: Optional[PacketTyreSetsData] = None
        self.motion_ex: Optional[PacketMotionExData] = None
        self.time_trial: Optional[PacketTimeTrialData] = None
        self.lap_positions: Optional[PacketLapPositionsData] = None

        # Player index (updated when session/participants packets arrive)
        self.player_index: int = 0

        # Lap tracking for LAP_START event
        self._last_lap = None

        # Latest raw packet (for polling)
        self._latest_packet = None

    # ------------------------------------------------------------
    # Listener registration
    # ------------------------------------------------------------
    def register_listener(self, listener: EventListener):
        with self._lock:
            self._listeners.append(listener)

    def _emit(self, event_type: EventType, **payload):
        with self._lock:
            listeners = list(self._listeners)
        for listener in listeners:
            listener.handle_event(event_type, **payload)

    # ------------------------------------------------------------
    # Packet routing (thread-safe)
    # ------------------------------------------------------------
    def update_from_packet(self, packet):
        with self._lock:
            self._latest_packet = packet

            # Always sync player_index from the packet header
            if hasattr(packet, 'header') and packet.header is not None:
                self.player_index = packet.header.m_playerCarIndex

            # Store packet by type
            if isinstance(packet, PacketMotionData):
                self.motion = packet

            elif isinstance(packet, PacketSessionData):
                self.session = packet

            elif isinstance(packet, PacketLapData):
                self._handle_lap_data(packet)

            elif isinstance(packet, PacketCarTelemetryData):
                self.car_telemetry = packet

            elif isinstance(packet, PacketCarStatusData):
                self.car_status = packet

            elif isinstance(packet, PacketParticipantsData):
                if not self._participants_ready:
                    self.participants = packet
                    self._build_driver_map(packet)
                    self._participants_ready = True
                    self._emit(EventType.PARTICIPANTS_READY)

            elif isinstance(packet, PacketEventData):
                self.event = packet

            elif isinstance(packet, PacketCarSetupData):
                self.car_setups = packet

            elif isinstance(packet, PacketFinalClassificationData):
                self.final_classification = packet

            elif isinstance(packet, PacketLobbyInfoData):
                self.lobby_info = packet

            elif isinstance(packet, PacketCarDamageData):
                self.car_damage = packet

            elif isinstance(packet, PacketSessionHistoryData):
                self.session_history = packet

            elif isinstance(packet, PacketTyreSetsData):
                self.tyre_sets = packet

            elif isinstance(packet, PacketMotionExData):
                self.motion_ex = packet

            elif isinstance(packet, PacketTimeTrialData):
                self.time_trial = packet

            elif isinstance(packet, PacketLapPositionsData):
                self.lap_positions = packet

    def get_latest_packet(self):
        with self._lock:
            pkt = self._latest_packet
            self._latest_packet = None
        return pkt

    # ------------------------------------------------------------
    # Lap handling + LAP_START event
    # ------------------------------------------------------------
    def _handle_lap_data(self, packet: PacketLapData):
        self.lap_data = packet

        try:
            player_lap = packet.get_player_lap_data()
            current_lap = player_lap.m_currentLapNum
        except Exception:
            current_lap = None

        if current_lap is not None and current_lap != self._last_lap:
            if self.session and self.session.m_sessionType not in (11, 15):
                self._last_lap = current_lap
                self._emit(EventType.LAP_START, lap=current_lap)
            else:
                self._last_lap = current_lap


    # ------------------------------------------------------------
    # High-level accessors Saul will use
    # ------------------------------------------------------------

    @property
    def session_time_left(self) -> Optional[int]:
        if not self.session:
            return None
        return self.session.m_sessionTimeLeft

    @property
    def session_type(self) -> Optional[int]:
        if not self.session:
            return None
        return self.session.m_sessionType

    @property
    def is_formation_lap(self) -> bool:
        if not self.session:
            return False
        return (self.session.m_safetyCarStatus == SafetyCarStatus.FORMATION or 
                self.session.m_formationLap == 1)

    @property
    def driver_status(self) -> Optional[int]:
        if not self.lap_data:
            return None
        try:
            return self.lap_data.get_player_lap_data().m_driverStatus
        except Exception:
            return None

    @property
    def pit_status(self) -> Optional[int]:
        if not self.lap_data:
            return None
        try:
            return self.lap_data.get_player_lap_data().m_pitStatus
        except Exception:
            return None

    @property
    def current_lap(self) -> Optional[int]:
        if not self.lap_data:
            return None
        try:
            return self.lap_data.get_player_lap_data().m_currentLapNum
        except Exception:
            return None

    @property
    def sector(self) -> Optional[int]:
        if not self.lap_data:
            return None
        try:
            return self.lap_data.get_player_lap_data().m_sector
        except Exception:
            return None

    @property
    def speed(self) -> Optional[int]:
        if not self.car_telemetry:
            return None
        try:
            return self.car_telemetry.get_player_telemetry().m_speed
        except Exception:
            return None

    @property
    def throttle(self) -> Optional[float]:
        if not self.car_telemetry:
            return None
        try:
            return self.car_telemetry.get_player_telemetry().m_throttle
        except Exception:
            return None

    @property
    def brake(self) -> Optional[float]:
        if not self.car_telemetry:
            return None
        try:
            return self.car_telemetry.get_player_telemetry().m_brake
        except Exception:
            return None

    @property
    def steer(self) -> Optional[float]:
        if not self.car_telemetry:
            return None
        try:
            return self.car_telemetry.get_player_telemetry().m_steer
        except Exception:
            return None

    @property
    def drs_allowed(self) -> Optional[int]:
        if not self.car_status:
            return None
        try:
            return self.car_status.get_player_status().m_drsAllowed
        except Exception:
            return None

    @property
    def drs_activation_distance(self) -> Optional[int]:
        if not self.car_status:
            return None
        try:
            return self.car_status.get_player_status().m_drsActivationDistance
        except Exception:
            return None

    # ------------------------------------------------------------
    # Driver name lookup
    # ------------------------------------------------------------

    @staticmethod
    def _safe_name_decode(name_field) -> str:
        """Safely decode name field that might be str or bytes."""
        if isinstance(name_field, str):
            name = name_field.rstrip('\x00')
        elif isinstance(name_field, bytes):
            name = name_field.decode('utf-8', errors='replace').rstrip('\x00')
        else:
            return ""
        # Convert to title case (e.g., "HAMILTON" -> "Hamilton")
        return name.title()

    def get_driver_name(self, driver_id: int) -> str:
        """Look up driver name by driver ID from participants data."""
        if not self.participants:
            return f"Driver_{driver_id}"
        try:
            for p in self.participants.m_participants:
                if p.m_driverId == driver_id:
                    name = self._safe_name_decode(p.m_name)
                    if name:
                        return name
            return f"Driver_{driver_id}"
        except Exception:
            return f"Driver_{driver_id}"

    # ------------------------------------------------------------
    # Stub properties for fields not in F1 25 UDP spec
    # (safer than AttributeError — returns empty/default values)
    # ------------------------------------------------------------

    @property
    def driver_standings(self) -> list:
        """Driver championship standings (not broadcast in F1 25 UDP)."""
        return []

    @property
    def team_standings(self) -> list:
        """Team championship standings (not broadcast in F1 25 UDP)."""
        return []

    @property
    def remaining_points(self) -> int:
        """Remaining points in championship (not broadcast in F1 25 UDP)."""
        return 0

    @property
    def points_for_win(self) -> int:
        """Points awarded for a race win (standard: 25)."""
        return 25

    @property
    def player_pit_entry_lap(self) -> int:
        """Lap number for pit entry (not in F1 25 UDP spec). Returns 0."""
        return 0

    @property
    def player_pit_exit_lap(self) -> int:
        """Lap number for pit exit (not in F1 25 UDP spec). Returns 0."""
        return 0

    @property
    def ideal_pit_lap(self) -> int:
        """Lap number for ideal pit window."""
        if not self.session:
            return 0
        return self.session.m_pitStopWindowIdealLap

    @property
    def pit_release_allowed(self) -> bool:
        """Whether pit release is allowed (not in F1 25 UDP spec)."""
        return False

    @property
    def is_delta_positive(self) -> bool:
        """Whether delta is currently positive (SC/VSC freeze)."""
        return False

    @property
    def track_wetness(self) -> int:
        """
        Infer track wetness from FIA flags and weather.
        F1 25 doesn't broadcast track wetness directly.
        m_vehicleFiaFlags: -1=unknown, 0=none, 1=green, 2=blue(yellow/wet), 3=yellow
        """
        wetness = 0

        # Infer from weather (session packet)
        if self.session:
            weather = getattr(self.session, 'm_weather', 0)
            if weather == 3:  # light rain
                wetness = 50
            elif weather == 4:  # heavy rain
                wetness = 80
            elif weather == 5:  # storm
                wetness = 100

        # Override with FIA flags if available
        if self.car_status:
            try:
                flags = self.car_status.get_player_status().m_vehicleFiaFlags
                if flags == 2:  # blue flag = wet track
                    wetness = max(wetness, 85)
                elif flags == 3:  # yellow flag
                    wetness = max(wetness, 50)
            except Exception:
                pass

        return wetness

    @property
    def car_damage_wear(self) -> tuple:
        """Player tyre wear from CarDamage packet as (FL, FR, RL, RR)."""
        if not self.car_damage:
            return (0.0, 0.0, 0.0, 0.0)
        try:
            dmg = self.car_damage.get_player_damage()
            return dmg.m_tyresWear
        except Exception:
            return (0.0, 0.0, 0.0, 0.0)

    # ------------------------------------------------------------
    # Driver name lookup helpers
    # ------------------------------------------------------------

    def get_driver_full_name(self, driver_id: int) -> str:
        """Full name e.g. 'Charles Leclerc'."""
        if not self.participants:
            return f"Driver_{driver_id}"
        try:
            for p in self.participants.m_participants:
                if p.m_driverId == driver_id:
                    name = self._safe_name_decode(p.m_name)
                    if name:
                        return name
            return f"Driver_{driver_id}"
        except Exception:
            return f"Driver_{driver_id}"

    def get_driver_first_name(self, driver_id: int) -> str:
        """First name e.g. 'Charles'. For teammate pitting."""
        full = self.get_driver_full_name(driver_id)
        return full.split()[0] if full else f"Driver_{driver_id}"

    def get_driver_last_name(self, driver_id: int) -> str:
        """Last name e.g. 'Leclerc'. For gap reports."""
        full = self.get_driver_full_name(driver_id)
        parts = full.split()
        return parts[-1] if parts else f"Driver_{driver_id}"

    def get_driver_name_by_participant_index(self, participant_index: int) -> str:
        """Get driver last name directly from participant index."""
        if not self.participants:
            return f"Driver_{participant_index}"
        try:
            p = self.participants.m_participants[participant_index]
            name = self._safe_name_decode(p.m_name)
            if name:
                parts = name.split()
                return parts[-1] if parts else f"Driver_{participant_index}"
            return f"Driver_{participant_index}"
        except (IndexError, AttributeError):
            return f"Driver_{participant_index}"

    def get_driver_first_name_by_participant_index(self, participant_index: int) -> str:
        """Get driver first name directly from participant index."""
        if not self.participants:
            return f"Driver_{participant_index}"
        try:
            p = self.participants.m_participants[participant_index]
            name = self._safe_name_decode(p.m_name)
            if name:
                parts = name.split()
                return parts[0] if parts else f"Driver_{participant_index}"
            return f"Driver_{participant_index}"
        except (IndexError, AttributeError):
            return f"Driver_{participant_index}"

    # ------------------------------------------------------------
    # Team name lookup
    # ------------------------------------------------------------

    def get_team_name(self, team_id: int) -> str:
        """Team name from known team IDs. Falls back to 'your team'."""
        return TEAM_NAMES.get(team_id, "your team")

    # ------------------------------------------------------------
    # Final classification helpers
    # ------------------------------------------------------------

    def get_player_final_classification(self):
        """Get the player's final classification data for race finish."""
        if not self.final_classification:
            return None
        try:
            return self.final_classification.m_classificationData[self.player_index]
        except (IndexError, AttributeError):
            return None

    def get_car_at_position(self, position: int):
        """Get LapData for car at a given position (1-indexed)."""
        if not self.lap_data:
            return None
        try:
            for lap in self.lap_data.m_lapData:
                if lap.m_carPosition == position:
                    return lap
        except Exception:
            pass
        return None

    def get_driver_id_at_position(self, position: int) -> Optional[int]:
        """Get driver ID for car at a given position (1-indexed)."""
        if not self.lap_data or not self.participants:
            return None
        try:
            car = self.get_car_at_position(position)
            if car is None:
                return None
            # Driver ID is participant index (car_index), not m_driverId
            # We need to find the participant whose position matches
            for idx, lap in enumerate(self.lap_data.m_lapData):
                if lap.m_carPosition == position:
                    # The participant at this index has the driver
                    p = self.participants.m_participants[idx]
                    return p.m_driverId
        except Exception:
            pass
        return None

    def get_lap_data_for_position(self, position: int):
        """Get LapData for the car at a given position (1-indexed)."""
        if not self.lap_data:
            return None
        try:
            for lap in self.lap_data.m_lapData:
                if lap.m_carPosition == position:
                    return lap
        except Exception:
            pass
        return None

    def get_driver_id_for_participant_index(self, participant_index: int) -> Optional[int]:
        """Get driver ID from participant index."""
        if not self.participants:
            return None
        try:
            p = self.participants.m_participants[participant_index]
            return p.m_driverId
        except (IndexError, AttributeError):
            return None

    # =========================================================
    # GAP WORKER HELPERS
    # =========================================================

    def get_player(self):
        """Get player lap data for gap calculations."""
        if not self.lap_data:
            return None
        try:
            return self.lap_data.get_player_lap_data()
        except Exception:
            return None

    def get_car_ahead(self):
        """Get lap data for car ahead of player."""
        player = self.get_player()
        if not player:
            return None
        position = player.m_carPosition
        if position <= 1:
            return None
        return self.get_lap_data_for_position(position - 1)

    def get_car_behind(self):
        """Get lap data for car behind player."""
        player = self.get_player()
        if not player:
            return None
        return self.get_lap_data_for_position(player.m_carPosition + 1)

    @property
    def track_length(self) -> float:
        """Get track length in meters."""
        if not self.session:
            return 0
        return getattr(self.session, 'm_trackLength', 0)

    # =========================================================
    # DRIVER ID BASED LOOKUPS (for GapWorker)
    # =========================================================

    def _build_driver_map(self, participants):
        """Build driver ID to name map and position to driver ID map from participants packet."""
        self._driver_id_to_name = {}
        self._position_to_driver_id = {}
        if not participants:
            return
        try:
            for p in participants.m_participants:
                if p and p.m_driverId < 255:
                    name = self._safe_name_decode(p.m_name)
                    if name:
                        self._driver_id_to_name[p.m_driverId] = name
                    
                    if p.m_racePosition > 0:
                        self._position_to_driver_id[p.m_racePosition] = p.m_driverId
        except Exception:
            pass

    def get_driver_name(self, driver_id: int) -> str:
        """Get driver full name by driver ID."""
        if hasattr(self, '_driver_id_to_name') and driver_id in self._driver_id_to_name:
            return self._driver_id_to_name[driver_id]
        return f"Driver_{driver_id}"

    # =========================================================
    # INDEX-BASED LOOKUPS (for GapWorker)
    # =========================================================

    def get_player_index(self):
        """Get player's participant index."""
        if not self.session:
            return None
        return getattr(self.session.header, 'm_playerCarIndex', None)

    def get_car_ahead_index(self):
        """Get participant index of car ahead of player."""
        idx = self.get_player_index()
        if idx is None or idx <= 0:
            return None
        return idx - 1

    def get_car_behind_index(self):
        """Get participant index of car behind player."""
        idx = self.get_player_index()
        if idx is None:
            return None
        return idx + 1

    def get_driver_id_by_index(self, index: int) -> int | None:
        """Get driver ID by participant index."""
        if not self.participants or index is None:
            return None
        try:
            return self.participants.m_participants[index].m_driverId
        except:
            return None

    def get_last_name_by_driver_id(self, driver_id: int) -> str:
        """Get driver last name by driver ID."""
        if not self.participants:
            return "Driver"
        try:
            for p in self.participants.m_participants:
                if p.m_driverId == driver_id:
                    name = self._safe_name_decode(p.m_name)
                    if name:
                        return name.split()[-1]
        except:
            pass
        return "Driver"

    def get_lap_data_by_driver_id(self, driver_id: int):
        """Get lap data for a specific driver ID."""
        if not self.lap_data:
            print(f"[DEBUG] No lap_data available")
            return None
        try:
            for lap in self.lap_data.m_lapData:
                if lap.m_driverId == driver_id:
                    return lap
        except Exception as e:
            print(f"[DEBUG] get_lap_data_by_driver_id error: {e}")
        return None
        return getattr(self.session, 'm_playerCarIndex', None)

    def get_car_ahead_index(self):
        """Get participant index of car ahead of player."""
        idx = self.get_player_index()
        if idx is None or idx <= 0:
            return None
        return idx - 1

    def get_car_behind_index(self):
        """Get participant index of car behind player."""
        idx = self.get_player_index()
        if idx is None:
            return None
        return idx + 1

    def get_driver_id_by_index(self, index: int) -> int | None:
        """Get driver ID by participant index."""
        if not self.participants or index is None:
            return None
        try:
            return self.participants.m_participants[index].m_driverId
        except:
            return None

    def get_last_name_by_driver_id(self, driver_id: int) -> str:
        """Get driver last name by driver ID."""
        if not self.participants:
            return "Driver"
        try:
            for p in self.participants.m_participants:
                if p.m_driverId == driver_id:
                    name = self._safe_name_decode(p.m_name)
                    if name:
                        return name.split()[-1]
        except:
            pass
        return "Driver"

    def get_car_in_front(self) -> int | None:
        """Get driver ID of car ahead of player."""
        player = self.get_player()
        if not player:
            return None
        position = player.m_carPosition
        if position <= 1:
            return None
        return self.get_driver_id_by_position(position - 1)

    def get_car_behind_id(self) -> int | None:
        """Get driver ID of car behind player."""
        player = self.get_player()
        if not player:
            return None
        behind_position = player.m_carPosition + 1
        return self.get_driver_id_by_position(behind_position)

    def get_lap_data_by_driver_id(self, driver_id: int):
        """Get lap data for a specific driver ID."""
        if not self.lap_data:
            return None
        try:
            for lap in self.lap_data.m_lapData:
                if lap.m_driverId == driver_id:
                    return lap
        except Exception:
            pass
        return None
