# udp/packet_definitions.py

from dataclasses import dataclass
import struct
from enum import IntEnum


# ------------------------------------------------------------
# Packet IDs (F1 2025 standard format)
# ------------------------------------------------------------
class PacketID(IntEnum):
    MOTION = 0
    SESSION = 1
    LAP_DATA = 2
    EVENT = 3
    PARTICIPANTS = 4
    CAR_SETUPS = 5
    CAR_TELEMETRY = 6
    CAR_STATUS = 7
    FINAL_CLASSIFICATION = 8
    LOBBY_INFO = 9
    CAR_DAMAGE = 10
    SESSION_HISTORY = 11
    TYRE_SETS = 12
    MOTION_EX = 13


# ------------------------------------------------------------
# Packet Header (structure will be filled once you send fields)
# ------------------------------------------------------------
HEADER_FORMAT = "<"  # placeholder until you send header table
HEADER_STRUCT = struct.Struct(HEADER_FORMAT)


@dataclass
class PacketHeader:
    # TODO: fill fields once you send header table
    raw: bytes

    @classmethod
    def from_bytes(cls, data: bytes):
        # TODO: unpack header once we have the real format
        return cls(raw=data[:HEADER_STRUCT.size])


# ------------------------------------------------------------
# Packet Data Classes (placeholders until you send field tables)
# ------------------------------------------------------------

@dataclass
class PacketMotionData:
    header: PacketHeader
    # TODO: add fields

@dataclass
class PacketSessionData:
    header: PacketHeader
    # TODO: add fields

@dataclass
class PacketLapData:
    header: PacketHeader
    lap_data: list  # will become list[LapData]

@dataclass
class PacketEventData:
    header: PacketHeader
    # TODO: add fields

@dataclass
class PacketParticipantsData:
    header: PacketHeader
    # TODO: add fields

@dataclass
class PacketCarSetupsData:
    header: PacketHeader
    # TODO: add fields

# ------------------------------------------------------------
# CarTelemetryData (FULLY IMPLEMENTED)
# ------------------------------------------------------------
@dataclass
class CarTelemetryData:
    m_speed: int
    m_throttle: float
    m_steer: float
    m_brake: float
    m_clutch: int
    m_gear: int
    m_engineRPM: int
    m_drs: int
    m_revLightsPercent: int
    m_revLightsBitValue: int
    m_brakesTemperature: tuple[int, int, int, int]
    m_tyresSurfaceTemperature: tuple[int, int, int, int]
    m_tyresInnerTemperature: tuple[int, int, int, int]
    m_engineTemperature: int
    m_tyresPressure: tuple[float, float, float, float]
    m_surfaceType: tuple[int, int, int, int]


CAR_TELEMETRY_STRUCT = struct.Struct(
    "<"
    "H"
    "fff"
    "B"
    "b"
    "H"
    "B"
    "B"
    "H"
    "4H"
    "4B"
    "4B"
    "H"
    "4f"
    "4B"
)


@dataclass
class PacketCarTelemetryData:
    header: PacketHeader
    car_telemetry_data: list[CarTelemetryData]
    m_mfdPanelIndex: int
    m_mfdPanelIndexSecondaryPlayer: int
    m_suggestedGear: int


@dataclass
class CarStatusData:
    m_tractionControl: int
    m_antiLockBrakes: int
    m_fuelMix: int
    m_frontBrakeBias: int
    m_pitLimiterStatus: int
    m_fuelInTank: float
    m_fuelCapacity: float
    m_fuelRemainingLaps: float
    m_maxRPM: int
    m_idleRPM: int
    m_maxGears: int
    m_drsAllowed: int
    m_drsActivationDistance: int
    m_actualTyreCompound: int
    m_visualTyreCompound: int
    m_tyresAgeLaps: int
    m_vehicleFiaFlags: int
    m_enginePowerICE: float
    m_enginePowerMGUK: float
    m_ersStoreEnergy: float
    m_ersDeployMode: int
    m_ersHarvestedThisLapMGUK: float
    m_ersHarvestedThisLapMGUH: float
    m_ersDeployedThisLap: float
    m_networkPaused: int


@dataclass
class PacketCarStatusData:
    header: PacketHeader
    car_status_data: list[CarStatusData]
\
@dataclass
class PacketFinalClassificationData:
    header: PacketHeader
    # TODO: add fields

@dataclass
class PacketLobbyInfoData:
    header: PacketHeader
    # TODO: add fields

@dataclass
class PacketCarDamageData:
    header: PacketHeader
    # TODO: add fields

@dataclass
class PacketSessionHistoryData:
    header: PacketHeader
    # TODO: add fields

@dataclass
class PacketTyreSetsData:
    header: PacketHeader
    # TODO: add fields

@dataclass
class PacketMotionExData:
    header: PacketHeader
    # TODO: add fields