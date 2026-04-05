# udp/packet_definitions.py
# F1 2025 UDP Packet Definitions

from dataclasses import dataclass, field
import struct
from enum import IntEnum
from typing import Optional


# ------------------------------------------------------------
# Constants
# ------------------------------------------------------------
MAX_CARS = 22


# ------------------------------------------------------------
# Enums
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
    TIME_TRIAL = 14
    LAP_POSITIONS = 15


class SessionType(IntEnum):
    UNKNOWN = 0
    PRACTICE_1 = 1
    PRACTICE_2 = 2
    PRACTICE_3 = 3
    SHORT_PRACTICE = 4
    QUALIFYING_1 = 5
    QUALIFYING_2 = 6
    QUALIFYING_3 = 7
    ONE_SHOT_QUALIFYING = 8
    PRACTICE = 9
    FORMATION_LAP = 10
    RACE = 11
    RACE_2 = 12
    TIME_TRIAL = 13


class Weather(IntEnum):
    CLEAR = 0
    LIGHT_CLOUD = 1
    OVERCAST = 2
    LIGHT_RAIN = 3
    HEAVY_RAIN = 4
    STORM = 5


class SafetyCarStatus(IntEnum):
    NONE = 0
    FULL = 1
    VIRTUAL = 2
    FORMATION = 3


class TractionControl(IntEnum):
    OFF = 0
    MEDIUM = 1
    FULL = 2


class ERSDeployMode(IntEnum):
    NONE = 0
    MEDIUM = 1
    HOTLAP = 2
    OVERTAKE = 3


class FIAFlag(IntEnum):
    INVALID = -1
    NONE = 0
    GREEN = 1
    BLUE = 2
    YELLOW = 3


class DriverStatus(IntEnum):
    GARAGE = 0
    FLYING_LAP = 1
    IN_LAP = 2
    OUT_LAP = 3
    ON_TRACK = 4


class ResultStatus(IntEnum):
    INVALID = 0
    INACTIVE = 1
    ACTIVE = 2
    FINISHED = 3
    DID_NOT_FINISH = 4
    DISQUALIFIED = 5
    NOT_CLASSIFIED = 6
    RETIRED = 7


class PitStatus(IntEnum):
    NONE = 0
    PITTING = 1
    IN_PIT_AREA = 2


class EventCode(IntEnum):
    SSTA = 0x53535441  # "SSTA" Session Started
    SEND = 0x53454E44  # "SEND" Session Ended
    FTLP = 0x46544C50  # "FTLP" Fastest Lap
    RTMT = 0x52544D54  # "RTMT" Retirement
    DRSE = 0x44525345  # "DRSE" DRS Enabled
    DRSD = 0x44525344  # "DRSD" DRS Disabled
    TMPT = 0x544D5054  # "TMPT" Team Mate In Pits
    CHQF = 0x43485146  # "CHQF" Chequered Flag
    RCWN = 0x5243574E  # "RCWN" Race Winner
    PENA = 0x50454E41  # "PENA" Penalty
    SPTP = 0x53505450  # "SPTP" Speed Trap
    STLG = 0x53544C47  # "STLG" Start Lights
    LGOT = 0x4C474F54  # "LGOT" Lights Out
    DTSV = 0x44545356  # "DTSV" Drive Through Served
    SGSV = 0x53475356  # "SGSV" Stop Go Served
    FLBK = 0x464C424B  # "FLBK" Flashback
    BUTN = 0x4255544E  # "BUTN" Button Status
    RDFL = 0x5244464C  # "RDFL" Red Flag
    OVTK = 0x4F56544B  # "OVTK" Overtake
    SCAR = 0x53434152  # "SCAR" Safety Car
    COLL = 0x434F4C4C  # "COLL" Collision


class TyreCompound(IntEnum):
    F1_MODERN_C5 = 16
    F1_MODERN_C4 = 17
    F1_MODERN_C3 = 18
    F1_MODERN_C2 = 19
    F1_MODERN_C1 = 20
    F1_MODERN_C0 = 21
    F1_MODERN_C6 = 22
    F1_MODERN_INTER = 7
    F1_MODERN_WET = 8
    F1_CLASSIC_DRY = 9
    F1_CLASSIC_WET = 10
    F2_SUPER_SOFT = 11
    F2_SOFT = 12
    F2_MEDIUM = 13
    F2_HARD = 14
    F2_WET = 15


class ReadyStatus(IntEnum):
    NOT_READY = 0
    READY = 1
    SPECTATING = 2


class Platform(IntEnum):
    STEAM = 1
    PLAYSTATION = 3
    XBOX = 4
    ORIGIN = 6
    UNKNOWN = 255


# ------------------------------------------------------------
# Struct Formats
# ------------------------------------------------------------

HEADER_FORMAT = "<HBBBBIIfIIBB"
HEADER_STRUCT = struct.Struct(HEADER_FORMAT)
HEADER_SIZE = HEADER_STRUCT.size  # 28 bytes


# ------------------------------------------------------------
# Packet Header
# ------------------------------------------------------------

@dataclass
class PacketHeader:
    m_packetFormat: int
    m_gameYear: int
    m_gameMajorVersion: int
    m_gameMinorVersion: int
    m_packetVersion: int
    m_packetId: int
    m_sessionUID: int
    m_sessionTime: float
    m_frameIdentifier: int
    m_overallFrameIdentifier: int
    m_playerCarIndex: int
    m_secondaryPlayerCarIndex: int

    @classmethod
    def from_bytes(cls, data: bytes) -> "PacketHeader":
        unpacked = HEADER_STRUCT.unpack(data[:HEADER_SIZE])
        return cls(
            m_packetFormat=unpacked[0],
            m_gameYear=unpacked[1],
            m_gameMajorVersion=unpacked[2],
            m_gameMinorVersion=unpacked[3],
            m_packetVersion=unpacked[4],
            m_packetId=unpacked[5],
            m_sessionUID=unpacked[6],
            m_sessionTime=unpacked[7],
            m_frameIdentifier=unpacked[8],
            m_overallFrameIdentifier=unpacked[9],
            m_playerCarIndex=unpacked[10],
            m_secondaryPlayerCarIndex=unpacked[11],
        )

    @property
    def packet_id(self) -> PacketID:
        return PacketID(self.m_packetId)

    @property
    def player_car_index(self) -> int:
        return self.m_playerCarIndex

    def is_valid(self) -> bool:
        return self.m_packetFormat == 2025 and self.m_packetId <= 15


# ------------------------------------------------------------
# Packet 0: Motion
# ------------------------------------------------------------

CAR_MOTION_FORMAT = "<fff fff hhh hhh fff fff"
CAR_MOTION_STRUCT = struct.Struct(CAR_MOTION_FORMAT)
CAR_MOTION_SIZE = CAR_MOTION_STRUCT.size  # 60 bytes

MOTION_PACKET_FORMAT = "<" \
    + "B" * MAX_CARS * 15  # 22 cars, 15 floats/h shorts
MOTION_PACKET_STRUCT = struct.Struct(MOTION_PACKET_FORMAT)


@dataclass
class CarMotionData:
    m_worldPositionX: float
    m_worldPositionY: float
    m_worldPositionZ: float
    m_worldVelocityX: float
    m_worldVelocityY: float
    m_worldVelocityZ: float
    m_worldForwardDirX: int
    m_worldForwardDirY: int
    m_worldForwardDirZ: int
    m_worldRightDirX: int
    m_worldRightDirY: int
    m_worldRightDirZ: int
    m_gForceLateral: float
    m_gForceLongitudinal: float
    m_gForceVertical: float
    m_yaw: float
    m_pitch: float
    m_roll: float

    @classmethod
    def from_bytes(cls, data: bytes) -> "CarMotionData":
        unpacked = CAR_MOTION_STRUCT.unpack(data[:CAR_MOTION_SIZE])
        return cls(
            m_worldPositionX=unpacked[0],
            m_worldPositionY=unpacked[1],
            m_worldPositionZ=unpacked[2],
            m_worldVelocityX=unpacked[3],
            m_worldVelocityY=unpacked[4],
            m_worldVelocityZ=unpacked[5],
            m_worldForwardDirX=unpacked[6],
            m_worldForwardDirY=unpacked[7],
            m_worldForwardDirZ=unpacked[8],
            m_worldRightDirX=unpacked[9],
            m_worldRightDirY=unpacked[10],
            m_worldRightDirZ=unpacked[11],
            m_gForceLateral=unpacked[12],
            m_gForceLongitudinal=unpacked[13],
            m_gForceVertical=unpacked[14],
            m_yaw=unpacked[15],
            m_pitch=unpacked[16],
            m_roll=unpacked[17],
        )


@dataclass
class PacketMotionData:
    header: PacketHeader
    car_motion_data: list[CarMotionData]

    @classmethod
    def from_bytes(cls, data: bytes) -> "PacketMotionData":
        header = PacketHeader.from_bytes(data)
        offset = HEADER_SIZE
        cars = []
        for _ in range(MAX_CARS):
            cars.append(CarMotionData.from_bytes(data[offset:offset + CAR_MOTION_SIZE]))
            offset += CAR_MOTION_SIZE
        return cls(header=header, car_motion_data=cars)

    def get_player_motion(self) -> CarMotionData:
        return self.car_motion_data[self.header.m_playerCarIndex]


# ------------------------------------------------------------
# Packet 1: Session
# ------------------------------------------------------------

MARSHAL_ZONE_FORMAT = "<fb"
MARSHAL_ZONE_STRUCT = struct.Struct(MARSHAL_ZONE_FORMAT)
MARSHAL_ZONE_SIZE = MARSHAL_ZONE_STRUCT.size  # 5 bytes

WEATHER_FORECAST_FORMAT = "<BBBbbbbB"
WEATHER_FORECAST_STRUCT = struct.Struct(WEATHER_FORECAST_FORMAT)
WEATHER_FORECAST_SIZE = WEATHER_FORECAST_STRUCT.size  # 8 bytes

MAX_MARSHAL_ZONES = 21
MAX_WEATHER_SAMPLES = 64

SESSION_PACKET_SIZE = 753


@dataclass
class MarshalZone:
    m_zoneStart: float
    m_zoneFlag: int

    @classmethod
    def from_bytes(cls, data: bytes) -> "MarshalZone":
        unpacked = MARSHAL_ZONE_STRUCT.unpack(data[:MARSHAL_ZONE_SIZE])
        return cls(m_zoneStart=unpacked[0], m_zoneFlag=unpacked[1])

    @property
    def flag(self) -> FIAFlag:
        return FIAFlag(self.m_zoneFlag)


@dataclass
class WeatherForecastSample:
    m_sessionType: int
    m_timeOffset: int
    m_weather: int
    m_trackTemperature: int
    m_trackTemperatureChange: int
    m_airTemperature: int
    m_airTemperatureChange: int
    m_rainPercentage: int

    @classmethod
    def from_bytes(cls, data: bytes) -> "WeatherForecastSample":
        unpacked = WEATHER_FORECAST_STRUCT.unpack(data[:WEATHER_FORECAST_SIZE])
        return cls(*unpacked)

    @property
    def weather_type(self) -> Weather:
        return Weather(self.m_weather)


@dataclass
class PacketSessionData:
    header: PacketHeader
    m_weather: int
    m_trackTemperature: int
    m_airTemperature: int
    m_totalLaps: int
    m_trackLength: int
    m_sessionType: int
    m_trackId: int
    m_formula: int
    m_sessionTimeLeft: int
    m_sessionDuration: int
    m_pitSpeedLimit: int
    m_gamePaused: int
    m_isSpectating: int
    m_spectatorCarIndex: int
    m_sliProNativeSupport: int
    m_numMarshalZones: int
    m_marshalZones: list[MarshalZone]
    m_safetyCarStatus: int
    m_networkGame: int
    m_numWeatherForecastSamples: int
    m_weatherForecastSamples: list[WeatherForecastSample]
    m_forecastAccuracy: int
    m_aiDifficulty: int
    m_seasonLinkIdentifier: int
    m_weekendLinkIdentifier: int
    m_sessionLinkIdentifier: int
    m_pitStopWindowIdealLap: int
    m_pitStopWindowLatestLap: int
    m_pitStopRejoinPosition: int
    m_steeringAssist: int
    m_brakingAssist: int
    m_gearboxAssist: int
    m_pitAssist: int
    m_pitReleaseAssist: int
    m_ersAssist: int
    m_drsAssist: int
    m_dynamicRacingLine: int
    m_dynamicRacingLineType: int
    m_gameMode: int
    m_ruleSet: int
    m_timeOfDay: int
    m_sessionLength: int
    m_speedUnitsLeadPlayer: int
    m_temperatureUnitsLeadPlayer: int
    m_speedUnitsSecondaryPlayer: int
    m_temperatureUnitsSecondaryPlayer: int
    m_numSafetyCarPeriods: int
    m_numVirtualSafetyCarPeriods: int
    m_numRedFlagPeriods: int
    m_equalCarPerformance: int
    m_recoveryMode: int
    m_flashbackLimit: int
    m_surfaceType: int
    m_lowFuelMode: int
    m_raceStarts: int
    m_tyreTemperature: int
    m_pitLaneTyreSim: int
    m_carDamage: int
    m_carDamageRate: int
    m_collisions: int
    m_collisionsOffForFirstLapOnly: int
    m_mpUnsafePitRelease: int
    m_mpOffForGriefing: int
    m_cornerCuttingStringency: int
    m_parcFermeRules: int
    m_pitStopExperience: int
    m_safetyCar: int
    m_safetyCarExperience: int
    m_formationLap: int
    m_formationLapExperience: int
    m_redFlags: int
    m_affectsLicenceLevelSolo: int
    m_affectsLicenceLevelMP: int
    m_numSessionsInWeekend: int
    m_weekendStructure: list[int]
    m_sector2LapDistanceStart: float
    m_sector3LapDistanceStart: float

    @classmethod
    def from_bytes(cls, data: bytes) -> "PacketSessionData":
        header = PacketHeader.from_bytes(data)
        offset = HEADER_SIZE

        basic = struct.unpack_from("<" +
            "BBB"    # weather, trackTemp, airTemp
            "BH"     # totalLaps, trackLength
            "Bb"     # sessionType, trackId
            "B"      # formula
            "HH"     # sessionTimeLeft, sessionDuration
            "BBBB"   # pitSpeedLimit, gamePaused, isSpectating, spectatorCarIndex
            "B"      # sliProNativeSupport
            "B"      # numMarshalZones
            , data, offset)
        offset += 21

        marshal_zones = []
        for _ in range(basic[10]):  # numMarshalZones
            marshal_zones.append(MarshalZone.from_bytes(data[offset:offset + MARSHAL_ZONE_SIZE]))
            offset += MARSHAL_ZONE_SIZE

        more = struct.unpack_from("<" +
            "BB"     # safetyCarStatus, networkGame
            "B"      # numWeatherForecastSamples
            , data, offset)
        offset += 3

        weather_samples = []
        for _ in range(more[2]):  # numWeatherForecastSamples
            weather_samples.append(WeatherForecastSample.from_bytes(
                data[offset:offset + WEATHER_FORECAST_SIZE]))
            offset += WEATHER_FORECAST_SIZE

        rest = struct.unpack_from("<" +
            "B"      # forecastAccuracy
            "I"      # aiDifficulty
            "III"    # seasonLinkIdentifier, weekendLinkIdentifier, sessionLinkIdentifier
            "BBB"    # pitStopWindowIdealLap, pitStopWindowLatestLap, pitStopRejoinPosition
            "BBBBBB" # steeringAssist, brakingAssist, gearboxAssist, pitAssist, pitReleaseAssist, ersAssist
            "BB"     # drsAssist, dynamicRacingLine
            "B"      # dynamicRacingLineType
            "BB"     # gameMode, ruleSet
            "I"      # timeOfDay
            "B"      # sessionLength
            "BBBB"   # speedUnitsLeadPlayer, temperatureUnitsLeadPlayer, speedUnitsSecondaryPlayer, temperatureUnitsSecondaryPlayer
            "BBB"    # numSafetyCarPeriods, numVirtualSafetyCarPeriods, numRedFlagPeriods
            "BBBB"   # equalCarPerformance, recoveryMode, flashbackLimit, surfaceType
            "BB"     # lowFuelMode, raceStarts
            "BBBBB"  # tyreTemperature, pitLaneTyreSim, carDamage, carDamageRate, collisions
            "BB"     # collisionsOffForFirstLapOnly, mpUnsafePitRelease
            "BB"     # mpOffForGriefing, cornerCuttingStringency
            "BB"     # parcFermeRules, pitStopExperience
            "BB"     # safetyCar, safetyCarExperience
            "BB"     # formationLap, formationLapExperience
            "BBBBB"  # redFlags, affectsLicenceLevelSolo, affectsLicenceLevelMP, numSessionsInWeekend
            , data, offset)
        offset += 66

        weekend_structure = list(data[offset:offset + 12])
        offset += 12

        final = struct.unpack_from("<" +
            "ff"     # sector2LapDistanceStart, sector3LapDistanceStart
            , data, offset)

        return cls(
            header=header,
            m_weather=basic[0],
            m_trackTemperature=basic[1],
            m_airTemperature=basic[2],
            m_totalLaps=basic[3],
            m_trackLength=basic[4],
            m_sessionType=basic[5],
            m_trackId=basic[6],
            m_formula=basic[7],
            m_sessionTimeLeft=basic[8],
            m_sessionDuration=basic[9],
            m_pitSpeedLimit=basic[10],
            m_gamePaused=basic[11],
            m_isSpectating=basic[12],
            m_spectatorCarIndex=basic[13],
            m_sliProNativeSupport=basic[14],
            m_numMarshalZones=basic[15],
            m_marshalZones=marshal_zones,
            m_safetyCarStatus=more[0],
            m_networkGame=more[1],
            m_numWeatherForecastSamples=more[2],
            m_weatherForecastSamples=weather_samples,
            m_forecastAccuracy=rest[0],
            m_aiDifficulty=rest[1],
            m_seasonLinkIdentifier=rest[2],
            m_weekendLinkIdentifier=rest[3],
            m_sessionLinkIdentifier=rest[4],
            m_pitStopWindowIdealLap=rest[5],
            m_pitStopWindowLatestLap=rest[6],
            m_pitStopRejoinPosition=rest[7],
            m_steeringAssist=rest[8],
            m_brakingAssist=rest[9],
            m_gearboxAssist=rest[10],
            m_pitAssist=rest[11],
            m_pitReleaseAssist=rest[12],
            m_ersAssist=rest[13],
            m_drsAssist=rest[14],
            m_dynamicRacingLine=rest[15],
            m_dynamicRacingLineType=rest[16],
            m_gameMode=rest[17],
            m_ruleSet=rest[18],
            m_timeOfDay=rest[19],
            m_sessionLength=rest[20],
            m_speedUnitsLeadPlayer=rest[21],
            m_temperatureUnitsLeadPlayer=rest[22],
            m_speedUnitsSecondaryPlayer=rest[23],
            m_temperatureUnitsSecondaryPlayer=rest[24],
            m_numSafetyCarPeriods=rest[25],
            m_numVirtualSafetyCarPeriods=rest[26],
            m_numRedFlagPeriods=rest[27],
            m_equalCarPerformance=rest[28],
            m_recoveryMode=rest[29],
            m_flashbackLimit=rest[30],
            m_surfaceType=rest[31],
            m_lowFuelMode=rest[32],
            m_raceStarts=rest[33],
            m_tyreTemperature=rest[34],
            m_pitLaneTyreSim=rest[35],
            m_carDamage=rest[36],
            m_carDamageRate=rest[37],
            m_collisions=rest[38],
            m_collisionsOffForFirstLapOnly=rest[39],
            m_mpUnsafePitRelease=rest[40],
            m_mpOffForGriefing=rest[41],
            m_cornerCuttingStringency=rest[42],
            m_parcFermeRules=rest[43],
            m_pitStopExperience=rest[44],
            m_safetyCar=rest[45],
            m_safetyCarExperience=rest[46],
            m_formationLap=rest[47],
            m_formationLapExperience=rest[48],
            m_redFlags=rest[49],
            m_affectsLicenceLevelSolo=rest[50],
            m_affectsLicenceLevelMP=rest[51],
            m_numSessionsInWeekend=rest[52],
            m_weekendStructure=weekend_structure,
            m_sector2LapDistanceStart=final[0],
            m_sector3LapDistanceStart=final[1],
        )

    @property
    def weather_string(self) -> str:
        return Weather(self.m_weather).name.replace("_", " ").title()

    @property
    def session_type_string(self) -> str:
        return SessionType(self.m_sessionType).name.replace("_", " ").title()

    @property
    def is_safety_car_active(self) -> bool:
        return self.m_safetyCarStatus == SafetyCarStatus.FULL

    @property
    def is_vsc_active(self) -> bool:
        return self.m_safetyCarStatus == SafetyCarStatus.VIRTUAL

    @property
    def is_formation_lap(self) -> bool:
        return self.m_safetyCarStatus == SafetyCarStatus.FORMATION


# ------------------------------------------------------------
# Packet 2: Lap Data
# ------------------------------------------------------------

LAP_DATA_FORMAT = "<II HB HB HB HB fff BBBB BBB BB B B HH B f B"
LAP_DATA_STRUCT = struct.Struct(LAP_DATA_FORMAT)
LAP_DATA_SIZE = LAP_DATA_STRUCT.size  # 87 bytes


@dataclass
class LapData:
    m_lastLapTimeInMS: int
    m_currentLapTimeInMS: int
    m_sector1TimeMSPart: int
    m_sector1TimeMinutesPart: int
    m_sector2TimeMSPart: int
    m_sector2TimeMinutesPart: int
    m_deltaToCarInFrontMSPart: int
    m_deltaToCarInFrontMinutesPart: int
    m_deltaToRaceLeaderMSPart: int
    m_deltaToRaceLeaderMinutesPart: int
    m_lapDistance: float
    m_totalDistance: float
    m_safetyCarDelta: float
    m_carPosition: int
    m_currentLapNum: int
    m_pitStatus: int
    m_numPitStops: int
    m_sector: int
    m_currentLapInvalid: int
    m_penalties: int
    m_totalWarnings: int
    m_cornerCuttingWarnings: int
    m_numUnservedDriveThroughPens: int
    m_numUnservedStopGoPens: int
    m_gridPosition: int
    m_driverStatus: int
    m_resultStatus: int
    m_pitLaneTimerActive: int
    m_pitLaneTimeInLaneInMS: int
    m_pitStopTimerInMS: int
    m_pitStopShouldServePen: int
    m_speedTrapFastestSpeed: float
    m_speedTrapFastestLap: int

    @classmethod
    def from_bytes(cls, data: bytes) -> "LapData":
        unpacked = LAP_DATA_STRUCT.unpack(data[:LAP_DATA_SIZE])
        return cls(*unpacked)

    @property
    def last_lap_seconds(self) -> float:
        return self.m_lastLapTimeInMS / 1000.0

    @property
    def current_lap_seconds(self) -> float:
        return self.m_currentLapTimeInMS / 1000.0

    @property
    def sector1_time_ms(self) -> int:
        return self.m_sector1TimeMinutesPart * 60000 + self.m_sector1TimeMSPart

    @property
    def sector1_time_seconds(self) -> float:
        return self.sector1_time_ms / 1000.0

    @property
    def sector2_time_ms(self) -> int:
        return self.m_sector2TimeMinutesPart * 60000 + self.m_sector2TimeMSPart

    @property
    def sector2_time_seconds(self) -> float:
        return self.sector2_time_ms / 1000.0

    @property
    def sector3_time_seconds(self) -> float:
        sector3_ms = self.m_currentLapTimeInMS - self.sector1_time_ms - self.sector2_time_ms
        return max(0, sector3_ms / 1000.0)

    @property
    def delta_to_car_in_front_seconds(self) -> float:
        total_ms = self.m_deltaToCarInFrontMinutesPart * 60000 + self.m_deltaToCarInFrontMSPart
        return total_ms / 1000.0

    @property
    def delta_to_race_leader_seconds(self) -> float:
        total_ms = self.m_deltaToRaceLeaderMinutesPart * 60000 + self.m_deltaToRaceLeaderMSPart
        return total_ms / 1000.0

    @property
    def is_pitting(self) -> bool:
        return self.m_pitStatus == PitStatus.PITTING

    @property
    def is_on_track(self) -> bool:
        return self.m_driverStatus == DriverStatus.ON_TRACK

    @property
    def is_valid_lap(self) -> bool:
        return self.m_currentLapInvalid == 0

    @property
    def status(self) -> DriverStatus:
        return DriverStatus(self.m_driverStatus)

    @property
    def result_status(self) -> ResultStatus:
        return ResultStatus(self.m_resultStatus)


@dataclass
class PacketLapData:
    header: PacketHeader
    m_lapData: list[LapData]
    m_timeTrialPBCarIdx: int
    m_timeTrialRivalCarIdx: int

    @classmethod
    def from_bytes(cls, data: bytes) -> "PacketLapData":
        header = PacketHeader.from_bytes(data)
        offset = HEADER_SIZE

        laps = []
        for _ in range(MAX_CARS):
            laps.append(LapData.from_bytes(data[offset:offset + LAP_DATA_SIZE]))
            offset += LAP_DATA_SIZE

        final = struct.unpack_from("<BB", data, offset)
        return cls(
            header=header,
            m_lapData=laps,
            m_timeTrialPBCarIdx=final[0],
            m_timeTrialRivalCarIdx=final[1],
        )

    def get_player_lap_data(self) -> LapData:
        return self.m_lapData[self.header.m_playerCarIndex]

    @property
    def player_current_lap(self) -> int:
        return self.get_player_lap_data().m_currentLapNum

    @property
    def player_position(self) -> int:
        return self.get_player_lap_data().m_carPosition

    @property
    def player_sector(self) -> int:
        return self.get_player_lap_data().m_sector


# ------------------------------------------------------------
# Packet 3: Event
# ------------------------------------------------------------

EVENT_PACKET_SIZE = 45


@dataclass
class EventDataDetails:
    event_type: int
    data: dict

    @classmethod
    def from_bytes(cls, event_code: int, data: bytes) -> "EventDataDetails":
        offset = 4  # Skip event string code
        details = {}

        if event_code == EventCode.FTLP:
            unpacked = struct.unpack_from("<Bf", data, offset)
            details = {"vehicleIdx": unpacked[0], "lapTime": unpacked[1]}
        elif event_code == EventCode.RTMT:
            unpacked = struct.unpack_from("<BB", data, offset)
            details = {"vehicleIdx": unpacked[0], "reason": unpacked[1]}
        elif event_code == EventCode.DRSD:
            unpacked = struct.unpack_from("<B", data, offset)
            details = {"reason": unpacked[0]}
        elif event_code == EventCode.TMPT:
            unpacked = struct.unpack_from("<B", data, offset)
            details = {"vehicleIdx": unpacked[0]}
        elif event_code == EventCode.RCWN:
            unpacked = struct.unpack_from("<B", data, offset)
            details = {"vehicleIdx": unpacked[0]}
        elif event_code == EventCode.PENA:
            unpacked = struct.unpack_from("<BBBBBB", data, offset)
            details = {
                "penaltyType": unpacked[0],
                "infringementType": unpacked[1],
                "vehicleIdx": unpacked[2],
                "otherVehicleIdx": unpacked[3],
                "time": unpacked[4],
                "lapNum": unpacked[5],
                "placesGained": data[offset + 6],
            }
        elif event_code == EventCode.SPTP:
            unpacked = struct.unpack_from("<BfBBBf", data, offset)
            details = {
                "vehicleIdx": unpacked[0],
                "speed": unpacked[1],
                "isOverallFastestInSession": unpacked[2],
                "isDriverFastestInSession": unpacked[3],
                "fastestVehicleIdxInSession": unpacked[4],
                "fastestSpeedInSession": unpacked[5],
            }
        elif event_code == EventCode.STLG:
            unpacked = struct.unpack_from("<B", data, offset)
            details = {"numLights": unpacked[0]}
        elif event_code == EventCode.DTSV:
            unpacked = struct.unpack_from("<B", data, offset)
            details = {"vehicleIdx": unpacked[0]}
        elif event_code == EventCode.SGSV:
            unpacked = struct.unpack_from("<Bf", data, offset)
            details = {"vehicleIdx": unpacked[0], "stopTime": unpacked[1]}
        elif event_code == EventCode.FLBK:
            unpacked = struct.unpack_from("<If", data, offset)
            details = {"flashbackFrameIdentifier": unpacked[0], "flashbackSessionTime": unpacked[1]}
        elif event_code == EventCode.BUTN:
            unpacked = struct.unpack_from("<I", data, offset)
            details = {"buttonStatus": unpacked[0]}
        elif event_code == EventCode.OVTK:
            unpacked = struct.unpack_from("<BB", data, offset)
            details = {"overtakingVehicleIdx": unpacked[0], "beingOvertakenVehicleIdx": unpacked[1]}
        elif event_code == EventCode.SCAR:
            unpacked = struct.unpack_from("<BB", data, offset)
            details = {"safetyCarType": unpacked[0], "eventType": unpacked[1]}
        elif event_code == EventCode.COLL:
            unpacked = struct.unpack_from("<BB", data, offset)
            details = {"vehicle1Idx": unpacked[0], "vehicle2Idx": unpacked[1]}

        return cls(event_type=event_code, data=details)

    def get_fastest_lap_info(self) -> Optional[tuple[int, float]]:
        if self.event_type == EventCode.FTLP:
            return (self.data["vehicleIdx"], self.data["lapTime"])
        return None

    def get_penalty_info(self) -> Optional[dict]:
        if self.event_type == EventCode.PENA:
            return self.data
        return None


@dataclass
class PacketEventData:
    header: PacketHeader
    m_eventStringCode: bytes
    m_eventDetails: EventDataDetails

    @classmethod
    def from_bytes(cls, data: bytes) -> "PacketEventData":
        header = PacketHeader.from_bytes(data)
        event_code_bytes = data[HEADER_SIZE:HEADER_SIZE + 4]
        event_code_int = int.from_bytes(event_code_bytes, "little")

        details = EventDataDetails.from_bytes(event_code_int, data)

        return cls(
            header=header,
            m_eventStringCode=event_code_bytes,
            m_eventDetails=details,
        )

    @property
    def event_code_string(self) -> str:
        return self.m_eventStringCode.decode("utf-8", errors="replace").strip()

    @property
    def event_code(self) -> EventCode:
        try:
            return EventCode(self.m_eventDetails.event_type)
        except ValueError:
            return EventCode(0)


# ------------------------------------------------------------
# Packet 4: Participants
# ------------------------------------------------------------

LIVERY_COLOUR_FORMAT = "<BBB"
LIVERY_COLOUR_STRUCT = struct.Struct(LIVERY_COLOUR_FORMAT)
LIVERY_COLOUR_SIZE = LIVERY_COLOUR_STRUCT.size

PARTICIPANT_DATA_FORMAT = "<BBBB BBB 32s BBH BB"
PARTICIPANT_DATA_STRUCT = struct.Struct(PARTICIPANT_DATA_FORMAT)
PARTICIPANT_DATA_SIZE = PARTICIPANT_DATA_STRUCT.size  # 45 bytes


@dataclass
class LiveryColour:
    red: int
    green: int
    blue: int

    @classmethod
    def from_bytes(cls, data: bytes) -> "LiveryColour":
        unpacked = LIVERY_COLOUR_STRUCT.unpack(data[:LIVERY_COLOUR_SIZE])
        return cls(red=unpacked[0], green=unpacked[1], blue=unpacked[2])


@dataclass
class ParticipantData:
    m_aiControlled: int
    m_driverId: int
    m_networkId: int
    m_teamId: int
    m_myTeam: int
    m_raceNumber: int
    m_nationality: int
    m_name: str
    m_yourTelemetry: int
    m_showOnlineNames: int
    m_techLevel: int
    m_platform: int
    m_numColours: int
    m_liveryColours: list[LiveryColour]

    @classmethod
    def from_bytes(cls, data: bytes) -> "ParticipantData":
        unpacked = PARTICIPANT_DATA_STRUCT.unpack(data[:PARTICIPANT_DATA_SIZE])
        name = unpacked[7].decode("utf-8", errors="replace").strip("\x00")

        offset = PARTICIPANT_DATA_SIZE
        livery_colours = []
        for _ in range(min(unpacked[12], 4)):  # numColours
            livery_colours.append(LiveryColour.from_bytes(data[offset:offset + LIVERY_COLOUR_SIZE]))
            offset += LIVERY_COLOUR_SIZE

        return cls(
            m_aiControlled=unpacked[0],
            m_driverId=unpacked[1],
            m_networkId=unpacked[2],
            m_teamId=unpacked[3],
            m_myTeam=unpacked[4],
            m_raceNumber=unpacked[5],
            m_nationality=unpacked[6],
            m_name=name,
            m_yourTelemetry=unpacked[8],
            m_showOnlineNames=unpacked[9],
            m_techLevel=unpacked[10],
            m_platform=unpacked[11],
            m_numColours=unpacked[12],
            m_liveryColours=livery_colours,
        )

    @property
    def is_ai_controlled(self) -> bool:
        return self.m_aiControlled == 1

    @property
    def is_human_controlled(self) -> bool:
        return self.m_aiControlled == 0


@dataclass
class PacketParticipantsData:
    header: PacketHeader
    m_numActiveCars: int
    m_participants: list[ParticipantData]

    @classmethod
    def from_bytes(cls, data: bytes) -> "PacketParticipantsData":
        header = PacketHeader.from_bytes(data)
        offset = HEADER_SIZE

        num_active = data[offset]
        offset += 1

        participants = []
        for _ in range(MAX_CARS):
            participants.append(ParticipantData.from_bytes(data[offset:offset + PARTICIPANT_DATA_SIZE + 12]))
            offset += PARTICIPANT_DATA_SIZE + 12

        return cls(
            header=header,
            m_numActiveCars=num_active,
            m_participants=participants,
        )

    def get_player_name(self) -> str:
        return self.m_participants[self.header.m_playerCarIndex].m_name

    def get_driver_name(self, car_index: int) -> str:
        return self.m_participants[car_index].m_name

    def is_ai_controlled(self, car_index: int) -> bool:
        return self.m_participants[car_index].is_ai_controlled


# ------------------------------------------------------------
# Packet 5: Car Setups
# ------------------------------------------------------------

CAR_SETUP_FORMAT = "<BB BB ffff BBBB BB BB B ffff B f"
CAR_SETUP_STRUCT = struct.Struct(CAR_SETUP_FORMAT)
CAR_SETUP_SIZE = CAR_SETUP_STRUCT.size  # 47 bytes


@dataclass
class CarSetupData:
    m_frontWing: int
    m_rearWing: int
    m_onThrottle: int
    m_offThrottle: int
    m_frontCamber: float
    m_rearCamber: float
    m_frontToe: float
    m_rearToe: float
    m_frontSuspension: int
    m_rearSuspension: int
    m_frontAntiRollBar: int
    m_rearAntiRollBar: int
    m_frontSuspensionHeight: int
    m_rearSuspensionHeight: int
    m_brakePressure: int
    m_brakeBias: int
    m_engineBraking: int
    m_rearLeftTyrePressure: float
    m_rearRightTyrePressure: float
    m_frontLeftTyrePressure: float
    m_frontRightTyrePressure: float
    m_ballast: int
    m_fuelLoad: float

    @classmethod
    def from_bytes(cls, data: bytes) -> "CarSetupData":
        unpacked = CAR_SETUP_STRUCT.unpack(data[:CAR_SETUP_SIZE])
        return cls(*unpacked)


@dataclass
class PacketCarSetupData:
    header: PacketHeader
    m_carSetups: list[CarSetupData]
    m_nextFrontWingValue: float

    @classmethod
    def from_bytes(cls, data: bytes) -> "PacketCarSetupData":
        header = PacketHeader.from_bytes(data)
        offset = HEADER_SIZE

        setups = []
        for _ in range(MAX_CARS):
            setups.append(CarSetupData.from_bytes(data[offset:offset + CAR_SETUP_SIZE]))
            offset += CAR_SETUP_SIZE

        next_wing = struct.unpack_from("<f", data, offset)[0]

        return cls(
            header=header,
            m_carSetups=setups,
            m_nextFrontWingValue=next_wing,
        )

    def get_player_setup(self) -> CarSetupData:
        return self.m_carSetups[self.header.m_playerCarIndex]


# ------------------------------------------------------------
# Packet 6: Car Telemetry
# ------------------------------------------------------------

CAR_TELEMETRY_FORMAT = "<H fff B b H BB H 4H 4B 4B H 4f 4B"
CAR_TELEMETRY_STRUCT = struct.Struct(CAR_TELEMETRY_FORMAT)
CAR_TELEMETRY_SIZE = CAR_TELEMETRY_STRUCT.size  # 60 bytes


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

    @classmethod
    def from_bytes(cls, data: bytes) -> "CarTelemetryData":
        unpacked = CAR_TELEMETRY_STRUCT.unpack(data[:CAR_TELEMETRY_SIZE])
        brakes_temp = tuple(unpacked[11:15])
        surface_temp = tuple(unpacked[15:19])
        inner_temp = tuple(unpacked[19:23])
        pressures = tuple(unpacked[24:28])
        surface_type = tuple(unpacked[28:32])
        return cls(
            m_speed=unpacked[0],
            m_throttle=unpacked[1],
            m_steer=unpacked[2],
            m_brake=unpacked[3],
            m_clutch=unpacked[4],
            m_gear=unpacked[5],
            m_engineRPM=unpacked[6],
            m_drs=unpacked[7],
            m_revLightsPercent=unpacked[8],
            m_revLightsBitValue=unpacked[9],
            m_brakesTemperature=brakes_temp,
            m_tyresSurfaceTemperature=surface_temp,
            m_tyresInnerTemperature=inner_temp,
            m_engineTemperature=unpacked[23],
            m_tyresPressure=pressures,
            m_surfaceType=surface_type,
        )

    @property
    def is_drs_open(self) -> bool:
        return self.m_drs == 1

    @property
    def gear_string(self) -> str:
        if self.m_gear == 0:
            return "N"
        elif self.m_gear == -1:
            return "R"
        return str(self.m_gear)


@dataclass
class PacketCarTelemetryData:
    header: PacketHeader
    m_carTelemetryData: list[CarTelemetryData]
    m_mfdPanelIndex: int
    m_mfdPanelIndexSecondaryPlayer: int
    m_suggestedGear: int

    @classmethod
    def from_bytes(cls, data: bytes) -> "PacketCarTelemetryData":
        header = PacketHeader.from_bytes(data)
        offset = HEADER_SIZE

        telemetry = []
        for _ in range(MAX_CARS):
            telemetry.append(CarTelemetryData.from_bytes(data[offset:offset + CAR_TELEMETRY_SIZE]))
            offset += CAR_TELEMETRY_SIZE

        final = struct.unpack_from("<BBb", data, offset)

        return cls(
            header=header,
            m_carTelemetryData=telemetry,
            m_mfdPanelIndex=final[0],
            m_mfdPanelIndexSecondaryPlayer=final[1],
            m_suggestedGear=final[2],
        )

    def get_player_telemetry(self) -> CarTelemetryData:
        return self.m_carTelemetryData[self.header.m_playerCarIndex]

    @property
    def player_speed(self) -> int:
        return self.get_player_telemetry().m_speed

    @property
    def player_gear(self) -> int:
        return self.get_player_telemetry().m_gear

    @property
    def player_throttle(self) -> float:
        return self.get_player_telemetry().m_throttle


# ------------------------------------------------------------
# Packet 7: Car Status
# ------------------------------------------------------------

CAR_STATUS_FORMAT = "<BBBB B ff f HH B B H BB B b fff B fff B"
CAR_STATUS_STRUCT = struct.Struct(CAR_STATUS_FORMAT)
CAR_STATUS_SIZE = CAR_STATUS_STRUCT.size  # 58 bytes


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

    @classmethod
    def from_bytes(cls, data: bytes) -> "CarStatusData":
        unpacked = CAR_STATUS_STRUCT.unpack(data[:CAR_STATUS_SIZE])
        return cls(*unpacked)

    @property
    def tyre_compound_name(self) -> str:
        try:
            return TyreCompound(self.m_actualTyreCompound).name
        except ValueError:
            return f"Unknown({self.m_actualTyreCompound})"

    @property
    def is_pit_limiter_on(self) -> bool:
        return self.m_pitLimiterStatus == 1

    @property
    def is_drs_allowed(self) -> bool:
        return self.m_drsAllowed == 1

    @property
    def ers_mode(self) -> ERSDeployMode:
        return ERSDeployMode(self.m_ersDeployMode)


@dataclass
class PacketCarStatusData:
    header: PacketHeader
    m_carStatusData: list[CarStatusData]

    @classmethod
    def from_bytes(cls, data: bytes) -> "PacketCarStatusData":
        header = PacketHeader.from_bytes(data)
        offset = HEADER_SIZE

        status = []
        for _ in range(MAX_CARS):
            status.append(CarStatusData.from_bytes(data[offset:offset + CAR_STATUS_SIZE]))
            offset += CAR_STATUS_SIZE

        return cls(header=header, m_carStatusData=status)

    def get_player_status(self) -> CarStatusData:
        return self.m_carStatusData[self.header.m_playerCarIndex]

    @property
    def player_tyre_compound(self) -> str:
        return self.get_player_status().tyre_compound_name

    @property
    def player_fuel_remaining_laps(self) -> float:
        return self.get_player_status().m_fuelRemainingLaps


# ------------------------------------------------------------
# Packet 8: Final Classification
# ------------------------------------------------------------

FINAL_CLASSIFICATION_FORMAT = "<BBBB BB B I d BBBB 8B 8B 8B"
FINAL_CLASSIFICATION_STRUCT = struct.Struct(FINAL_CLASSIFICATION_FORMAT)
FINAL_CLASSIFICATION_SIZE = FINAL_CLASSIFICATION_STRUCT.size  # 45 bytes


@dataclass
class FinalClassificationData:
    m_position: int
    m_numLaps: int
    m_gridPosition: int
    m_points: int
    m_numPitStops: int
    m_resultStatus: int
    m_resultReason: int
    m_bestLapTimeInMS: int
    m_totalRaceTime: float
    m_penaltiesTime: int
    m_numPenalties: int
    m_numTyreStints: int
    m_tyreStintsActual: list[int]
    m_tyreStintsVisual: list[int]
    m_tyreStintsEndLaps: list[int]

    @classmethod
    def from_bytes(cls, data: bytes) -> "FinalClassificationData":
        unpacked = FINAL_CLASSIFICATION_STRUCT.unpack(data[:FINAL_CLASSIFICATION_SIZE])
        actual = list(unpacked[13:21])
        visual = list(unpacked[21:29])
        end_laps = list(unpacked[29:37])
        return cls(
            m_position=unpacked[0],
            m_numLaps=unpacked[1],
            m_gridPosition=unpacked[2],
            m_points=unpacked[3],
            m_numPitStops=unpacked[4],
            m_resultStatus=unpacked[5],
            m_resultReason=unpacked[6],
            m_bestLapTimeInMS=unpacked[7],
            m_totalRaceTime=unpacked[8],
            m_penaltiesTime=unpacked[9],
            m_numPenalties=unpacked[10],
            m_numTyreStints=unpacked[11],
            m_tyreStintsActual=actual,
            m_tyreStintsVisual=visual,
            m_tyreStintsEndLaps=end_laps,
        )

    @property
    def best_lap_seconds(self) -> float:
        return self.m_bestLapTimeInMS / 1000.0

    @property
    def finished(self) -> bool:
        return self.m_resultStatus == ResultStatus.FINISHED


@dataclass
class PacketFinalClassificationData:
    header: PacketHeader
    m_numCars: int
    m_classificationData: list[FinalClassificationData]

    @classmethod
    def from_bytes(cls, data: bytes) -> "PacketFinalClassificationData":
        header = PacketHeader.from_bytes(data)
        offset = HEADER_SIZE

        num_cars = data[offset]
        offset += 1

        classifications = []
        for _ in range(MAX_CARS):
            classifications.append(FinalClassificationData.from_bytes(
                data[offset:offset + FINAL_CLASSIFICATION_SIZE]))
            offset += FINAL_CLASSIFICATION_SIZE

        return cls(
            header=header,
            m_numCars=num_cars,
            m_classificationData=classifications,
        )

    def get_player_classification(self) -> FinalClassificationData:
        return self.m_classificationData[self.header.m_playerCarIndex]


# ------------------------------------------------------------
# Packet 9: Lobby Info
# ------------------------------------------------------------

LOBBY_INFO_FORMAT = "<BBBB 32s BBB H B"
LOBBY_INFO_STRUCT = struct.Struct(LOBBY_INFO_FORMAT)
LOBBY_INFO_SIZE = LOBBY_INFO_STRUCT.size  # 44 bytes


@dataclass
class LobbyInfoData:
    m_aiControlled: int
    m_teamId: int
    m_nationality: int
    m_platform: int
    m_name: str
    m_carNumber: int
    m_yourTelemetry: int
    m_showOnlineNames: int
    m_techLevel: int
    m_readyStatus: int

    @classmethod
    def from_bytes(cls, data: bytes) -> "LobbyInfoData":
        unpacked = LOBBY_INFO_STRUCT.unpack(data[:LOBBY_INFO_SIZE])
        name = unpacked[4].decode("utf-8", errors="replace").strip("\x00")
        return cls(
            m_aiControlled=unpacked[0],
            m_teamId=unpacked[1],
            m_nationality=unpacked[2],
            m_platform=unpacked[3],
            m_name=name,
            m_carNumber=unpacked[5],
            m_yourTelemetry=unpacked[6],
            m_showOnlineNames=unpacked[7],
            m_techLevel=unpacked[8],
            m_readyStatus=unpacked[9],
        )

    @property
    def is_ready(self) -> bool:
        return self.m_readyStatus == ReadyStatus.READY


@dataclass
class PacketLobbyInfoData:
    header: PacketHeader
    m_numPlayers: int
    m_lobbyPlayers: list[LobbyInfoData]

    @classmethod
    def from_bytes(cls, data: bytes) -> "PacketLobbyInfoData":
        header = PacketHeader.from_bytes(data)
        offset = HEADER_SIZE

        num_players = data[offset]
        offset += 1

        players = []
        for _ in range(MAX_CARS):
            players.append(LobbyInfoData.from_bytes(data[offset:offset + LOBBY_INFO_SIZE]))
            offset += LOBBY_INFO_SIZE

        return cls(
            header=header,
            m_numPlayers=num_players,
            m_lobbyPlayers=players,
        )


# ------------------------------------------------------------
# Packet 10: Car Damage
# ------------------------------------------------------------

CAR_DAMAGE_FORMAT = "<4f 4B 4B 4B BBBB BB BB BBBB BBBB BB"
CAR_DAMAGE_STRUCT = struct.Struct(CAR_DAMAGE_FORMAT)
CAR_DAMAGE_SIZE = CAR_DAMAGE_STRUCT.size  # 57 bytes


@dataclass
class CarDamageData:
    m_tyresWear: tuple[float, float, float, float]
    m_tyresDamage: tuple[int, int, int, int]
    m_brakesDamage: tuple[int, int, int, int]
    m_tyreBlisters: tuple[int, int, int, int]
    m_frontLeftWingDamage: int
    m_frontRightWingDamage: int
    m_rearWingDamage: int
    m_floorDamage: int
    m_diffuserDamage: int
    m_sidepodDamage: int
    m_drsFault: int
    m_ersFault: int
    m_gearBoxDamage: int
    m_engineDamage: int
    m_engineMGUHWear: int
    m_engineESWear: int
    m_engineCEWear: int
    m_engineICEWear: int
    m_engineMGUKWear: int
    m_engineTCWear: int
    m_engineBlown: int
    m_engineSeized: int

    @classmethod
    def from_bytes(cls, data: bytes) -> "CarDamageData":
        unpacked = CAR_DAMAGE_STRUCT.unpack(data[:CAR_DAMAGE_SIZE])
        return cls(
            m_tyresWear=tuple(unpacked[0:4]),
            m_tyresDamage=tuple(unpacked[4:8]),
            m_brakesDamage=tuple(unpacked[8:12]),
            m_tyreBlisters=tuple(unpacked[12:16]),
            m_frontLeftWingDamage=unpacked[16],
            m_frontRightWingDamage=unpacked[17],
            m_rearWingDamage=unpacked[18],
            m_floorDamage=unpacked[19],
            m_diffuserDamage=unpacked[20],
            m_sidepodDamage=unpacked[21],
            m_drsFault=unpacked[22],
            m_ersFault=unpacked[23],
            m_gearBoxDamage=unpacked[24],
            m_engineDamage=unpacked[25],
            m_engineMGUHWear=unpacked[26],
            m_engineESWear=unpacked[27],
            m_engineCEWear=unpacked[28],
            m_engineICEWear=unpacked[29],
            m_engineMGUKWear=unpacked[30],
            m_engineTCWear=unpacked[31],
            m_engineBlown=unpacked[32],
            m_engineSeized=unpacked[33],
        )

    @property
    def has_drs_fault(self) -> bool:
        return self.m_drsFault == 1

    @property
    def has_ers_fault(self) -> bool:
        return self.m_ersFault == 1

    @property
    def has_engine_issue(self) -> bool:
        return self.m_engineBlown == 1 or self.m_engineSeized == 1

    @property
    def avg_tyre_wear(self) -> float:
        return sum(self.m_tyresWear) / 4.0


@dataclass
class PacketCarDamageData:
    header: PacketHeader
    m_carDamageData: list[CarDamageData]

    @classmethod
    def from_bytes(cls, data: bytes) -> "PacketCarDamageData":
        header = PacketHeader.from_bytes(data)
        offset = HEADER_SIZE

        damages = []
        for _ in range(MAX_CARS):
            damages.append(CarDamageData.from_bytes(data[offset:offset + CAR_DAMAGE_SIZE]))
            offset += CAR_DAMAGE_SIZE

        return cls(header=header, m_carDamageData=damages)

    def get_player_damage(self) -> CarDamageData:
        return self.m_carDamageData[self.header.m_playerCarIndex]

    @property
    def has_drs_fault(self) -> bool:
        return self.get_player_damage().has_drs_fault

    @property
    def has_ers_fault(self) -> bool:
        return self.get_player_damage().has_ers_fault

    @property
    def has_engine_issue(self) -> bool:
        return self.get_player_damage().has_engine_issue

    @property
    def avg_tyre_wear(self) -> float:
        return self.get_player_damage().avg_tyre_wear


# ------------------------------------------------------------
# Packet 11: Session History
# ------------------------------------------------------------

LAP_HISTORY_FORMAT = "<I HB HB HB B"
LAP_HISTORY_STRUCT = struct.Struct(LAP_HISTORY_FORMAT)
LAP_HISTORY_SIZE = LAP_HISTORY_STRUCT.size  # 16 bytes

TYRE_STINT_HISTORY_FORMAT = "<BBB"
TYRE_STINT_HISTORY_STRUCT = struct.Struct(TYRE_STINT_HISTORY_FORMAT)
TYRE_STINT_HISTORY_SIZE = TYRE_STINT_HISTORY_STRUCT.size  # 3 bytes

MAX_LAP_HISTORY = 100
MAX_TYRE_STINTS = 8


@dataclass
class LapHistoryData:
    m_lapTimeInMS: int
    m_sector1TimeMSPart: int
    m_sector1TimeMinutesPart: int
    m_sector2TimeMSPart: int
    m_sector2TimeMinutesPart: int
    m_sector3TimeMSPart: int
    m_sector3TimeMinutesPart: int
    m_lapValidBitFlags: int

    @classmethod
    def from_bytes(cls, data: bytes) -> "LapHistoryData":
        unpacked = LAP_HISTORY_STRUCT.unpack(data[:LAP_HISTORY_SIZE])
        return cls(*unpacked)

    @property
    def lap_time_seconds(self) -> float:
        return self.m_lapTimeInMS / 1000.0

    @property
    def is_lap_valid(self) -> bool:
        return (self.m_lapValidBitFlags & 0x01) != 0

    @property
    def sector1_valid(self) -> bool:
        return (self.m_lapValidBitFlags & 0x02) != 0

    @property
    def sector2_valid(self) -> bool:
        return (self.m_lapValidBitFlags & 0x04) != 0

    @property
    def sector3_valid(self) -> bool:
        return (self.m_lapValidBitFlags & 0x08) != 0


@dataclass
class TyreStintHistoryData:
    m_endLap: int
    m_tyreActualCompound: int
    m_tyreVisualCompound: int

    @classmethod
    def from_bytes(cls, data: bytes) -> "TyreStintHistoryData":
        unpacked = TYRE_STINT_HISTORY_STRUCT.unpack(data[:TYRE_STINT_HISTORY_SIZE])
        return cls(*unpacked)


@dataclass
class PacketSessionHistoryData:
    header: PacketHeader
    m_carIdx: int
    m_numLaps: int
    m_numTyreStints: int
    m_bestLapTimeLapNum: int
    m_bestSector1LapNum: int
    m_bestSector2LapNum: int
    m_bestSector3LapNum: int
    m_lapHistoryData: list[LapHistoryData]
    m_tyreStintsHistoryData: list[TyreStintHistoryData]

    @classmethod
    def from_bytes(cls, data: bytes) -> "PacketSessionHistoryData":
        header = PacketHeader.from_bytes(data)
        offset = HEADER_SIZE

        basic = struct.unpack_from("<BBBBBBBB", data, offset)
        offset += 8

        lap_history = []
        for i in range(MAX_LAP_HISTORY):
            if i < basic[1]:  # numLaps
                lap_history.append(LapHistoryData.from_bytes(data[offset:offset + LAP_HISTORY_SIZE]))
            else:
                lap_history.append(LapHistoryData(0, 0, 0, 0, 0, 0, 0, 0))
            offset += LAP_HISTORY_SIZE

        tyre_stints = []
        for i in range(MAX_TYRE_STINTS):
            if i < basic[2]:  # numTyreStints
                tyre_stints.append(TyreStintHistoryData.from_bytes(
                    data[offset:offset + TYRE_STINT_HISTORY_SIZE]))
            else:
                tyre_stints.append(TyreStintHistoryData(255, 0, 0))
            offset += TYRE_STINT_HISTORY_SIZE

        return cls(
            header=header,
            m_carIdx=basic[0],
            m_numLaps=basic[1],
            m_numTyreStints=basic[2],
            m_bestLapTimeLapNum=basic[3],
            m_bestSector1LapNum=basic[4],
            m_bestSector2LapNum=basic[5],
            m_bestSector3LapNum=basic[6],
            m_lapHistoryData=lap_history,
            m_tyreStintsHistoryData=tyre_stints,
        )


# ------------------------------------------------------------
# Packet 12: Tyre Sets
# ------------------------------------------------------------

TYRE_SET_FORMAT = "<BB BB BB B h B"
TYRE_SET_STRUCT = struct.Struct(TYRE_SET_FORMAT)
TYRE_SET_SIZE = TYRE_SET_STRUCT.size  # 10 bytes

MAX_TYRE_SETS = 20


@dataclass
class TyreSetData:
    m_actualTyreCompound: int
    m_visualTyreCompound: int
    m_wear: int
    m_available: int
    m_recommendedSession: int
    m_lifeSpan: int
    m_usableLife: int
    m_lapDeltaTime: int
    m_fitted: int

    @classmethod
    def from_bytes(cls, data: bytes) -> "TyreSetData":
        unpacked = TYRE_SET_STRUCT.unpack(data[:TYRE_SET_SIZE])
        return cls(*unpacked)

    @property
    def is_fitted(self) -> bool:
        return self.m_fitted == 1

    @property
    def is_available(self) -> bool:
        return self.m_available == 1


@dataclass
class PacketTyreSetsData:
    header: PacketHeader
    m_carIdx: int
    m_tyreSetData: list[TyreSetData]
    m_fittedIdx: int

    @classmethod
    def from_bytes(cls, data: bytes) -> "PacketTyreSetsData":
        header = PacketHeader.from_bytes(data)
        offset = HEADER_SIZE

        car_idx = data[offset]
        offset += 1

        tyre_sets = []
        for _ in range(MAX_TYRE_SETS):
            tyre_sets.append(TyreSetData.from_bytes(data[offset:offset + TYRE_SET_SIZE]))
            offset += TYRE_SET_SIZE

        fitted_idx = data[offset]

        return cls(
            header=header,
            m_carIdx=car_idx,
            m_tyreSetData=tyre_sets,
            m_fittedIdx=fitted_idx,
        )

    def get_fitted_tyre(self) -> TyreSetData:
        return self.m_tyreSetData[self.m_fittedIdx]


# ------------------------------------------------------------
# Packet 13: Motion Ex
# ------------------------------------------------------------

MOTION_EX_FORMAT = "<" + "f" * 62
MOTION_EX_STRUCT = struct.Struct(MOTION_EX_FORMAT)
MOTION_EX_SIZE = MOTION_EX_STRUCT.size  # 273 bytes


@dataclass
class PacketMotionExData:
    header: PacketHeader
    m_suspensionPosition: tuple[float, float, float, float]
    m_suspensionVelocity: tuple[float, float, float, float]
    m_suspensionAcceleration: tuple[float, float, float, float]
    m_wheelSpeed: tuple[float, float, float, float]
    m_wheelSlipRatio: tuple[float, float, float, float]
    m_wheelSlipAngle: tuple[float, float, float, float]
    m_wheelLatForce: tuple[float, float, float, float]
    m_wheelLongForce: tuple[float, float, float, float]
    m_heightOfCOGAboveGround: float
    m_localVelocityX: float
    m_localVelocityY: float
    m_localVelocityZ: float
    m_angularVelocityX: float
    m_angularVelocityY: float
    m_angularVelocityZ: float
    m_angularAccelerationX: float
    m_angularAccelerationY: float
    m_angularAccelerationZ: float
    m_frontWheelsAngle: float
    m_wheelVertForce: tuple[float, float, float, float]
    m_frontAeroHeight: float
    m_rearAeroHeight: float
    m_frontRollAngle: float
    m_rearRollAngle: float
    m_chassisYaw: float
    m_chassisPitch: float
    m_wheelCamber: tuple[float, float, float, float]
    m_wheelCamberGain: tuple[float, float, float, float]

    @classmethod
    def from_bytes(cls, data: bytes) -> "PacketMotionExData":
        header = PacketHeader.from_bytes(data)
        offset = HEADER_SIZE

        unpacked = list(MOTION_EX_STRUCT.unpack(data[offset:offset + MOTION_EX_SIZE]))

        def get_floats(n: int) -> tuple[float, ...]:
            return tuple(unpacked[:n])

        pos = tuple(unpacked[0:4])
        vel = tuple(unpacked[4:8])
        acc = tuple(unpacked[8:12])
        speed = tuple(unpacked[12:16])
        slip_ratio = tuple(unpacked[16:20])
        slip_angle = tuple(unpacked[20:24])
        lat_force = tuple(unpacked[24:28])
        long_force = tuple(unpacked[28:32])
        vert_force = tuple(unpacked[32:36])

        return cls(
            header=header,
            m_suspensionPosition=pos,
            m_suspensionVelocity=vel,
            m_suspensionAcceleration=acc,
            m_wheelSpeed=speed,
            m_wheelSlipRatio=slip_ratio,
            m_wheelSlipAngle=slip_angle,
            m_wheelLatForce=lat_force,
            m_wheelLongForce=long_force,
            m_heightOfCOGAboveGround=unpacked[36],
            m_localVelocityX=unpacked[37],
            m_localVelocityY=unpacked[38],
            m_localVelocityZ=unpacked[39],
            m_angularVelocityX=unpacked[40],
            m_angularVelocityY=unpacked[41],
            m_angularVelocityZ=unpacked[42],
            m_angularAccelerationX=unpacked[43],
            m_angularAccelerationY=unpacked[44],
            m_angularAccelerationZ=unpacked[45],
            m_frontWheelsAngle=unpacked[46],
            m_wheelVertForce=vert_force,
            m_frontAeroHeight=unpacked[47],
            m_rearAeroHeight=unpacked[48],
            m_frontRollAngle=unpacked[49],
            m_rearRollAngle=unpacked[50],
            m_chassisYaw=unpacked[51],
            m_chassisPitch=unpacked[52],
            m_wheelCamber=tuple(unpacked[53:57]),
            m_wheelCamberGain=tuple(unpacked[57:61]),
        )


# ------------------------------------------------------------
# Packet 14: Time Trial
# ------------------------------------------------------------

TIME_TRIAL_DATASET_FORMAT = "<BB I III BBBB BB"
TIME_TRIAL_DATASET_STRUCT = struct.Struct(TIME_TRIAL_DATASET_FORMAT)
TIME_TRIAL_DATASET_SIZE = TIME_TRIAL_DATASET_STRUCT.size  # 22 bytes


@dataclass
class TimeTrialDataSet:
    m_carIdx: int
    m_teamId: int
    m_lapTimeInMS: int
    m_sector1TimeInMS: int
    m_sector2TimeInMS: int
    m_sector3TimeInMS: int
    m_tractionControl: int
    m_gearboxAssist: int
    m_antiLockBrakes: int
    m_equalCarPerformance: int
    m_customSetup: int
    m_valid: int

    @classmethod
    def from_bytes(cls, data: bytes) -> "TimeTrialDataSet":
        unpacked = TIME_TRIAL_DATASET_STRUCT.unpack(data[:TIME_TRIAL_DATASET_SIZE])
        return cls(*unpacked)

    @property
    def lap_time_seconds(self) -> float:
        return self.m_lapTimeInMS / 1000.0


@dataclass
class PacketTimeTrialData:
    header: PacketHeader
    m_playerSessionBestDataSet: TimeTrialDataSet
    m_personalBestDataSet: TimeTrialDataSet
    m_rivalDataSet: TimeTrialDataSet

    @classmethod
    def from_bytes(cls, data: bytes) -> "PacketTimeTrialData":
        header = PacketHeader.from_bytes(data)
        offset = HEADER_SIZE

        player_best = TimeTrialDataSet.from_bytes(data[offset:offset + TIME_TRIAL_DATASET_SIZE])
        offset += TIME_TRIAL_DATASET_SIZE

        personal_best = TimeTrialDataSet.from_bytes(data[offset:offset + TIME_TRIAL_DATASET_SIZE])
        offset += TIME_TRIAL_DATASET_SIZE

        rival = TimeTrialDataSet.from_bytes(data[offset:offset + TIME_TRIAL_DATASET_SIZE])

        return cls(
            header=header,
            m_playerSessionBestDataSet=player_best,
            m_personalBestDataSet=personal_best,
            m_rivalDataSet=rival,
        )


# ------------------------------------------------------------
# Packet 15: Lap Positions
# ------------------------------------------------------------

MAX_LAP_POSITIONS = 50


@dataclass
class PacketLapPositionsData:
    header: PacketHeader
    m_numLaps: int
    m_lapStart: int
    m_positionForVehicleIdx: list[list[int]]

    @classmethod
    def from_bytes(cls, data: bytes) -> "PacketLapPositionsData":
        header = PacketHeader.from_bytes(data)
        offset = HEADER_SIZE

        num_laps = data[offset]
        offset += 1

        lap_start = data[offset]
        offset += 1

        positions = []
        for _ in range(MAX_LAP_POSITIONS):
            lap_positions = []
            for _ in range(MAX_CARS):
                lap_positions.append(data[offset])
                offset += 1
            positions.append(lap_positions)

        return cls(
            header=header,
            m_numLaps=num_laps,
            m_lapStart=lap_start,
            m_positionForVehicleIdx=positions,
        )

    def get_position_at_lap(self, lap_index: int, car_index: int) -> int:
        if 0 <= lap_index < len(self.m_positionForVehicleIdx):
            if 0 <= car_index < len(self.m_positionForVehicleIdx[lap_index]):
                return self.m_positionForVehicleIdx[lap_index][car_index]
        return 0


# ------------------------------------------------------------
# Unified Decoder
# ------------------------------------------------------------

PACKET_DECODERS = {
    PacketID.MOTION: PacketMotionData.from_bytes,
    PacketID.SESSION: PacketSessionData.from_bytes,
    PacketID.LAP_DATA: PacketLapData.from_bytes,
    PacketID.EVENT: PacketEventData.from_bytes,
    PacketID.PARTICIPANTS: PacketParticipantsData.from_bytes,
    PacketID.CAR_SETUPS: PacketCarSetupData.from_bytes,
    PacketID.CAR_TELEMETRY: PacketCarTelemetryData.from_bytes,
    PacketID.CAR_STATUS: PacketCarStatusData.from_bytes,
    PacketID.FINAL_CLASSIFICATION: PacketFinalClassificationData.from_bytes,
    PacketID.LOBBY_INFO: PacketLobbyInfoData.from_bytes,
    PacketID.CAR_DAMAGE: PacketCarDamageData.from_bytes,
    PacketID.SESSION_HISTORY: PacketSessionHistoryData.from_bytes,
    PacketID.TYRE_SETS: PacketTyreSetsData.from_bytes,
    PacketID.MOTION_EX: PacketMotionExData.from_bytes,
    PacketID.TIME_TRIAL: PacketTimeTrialData.from_bytes,
    PacketID.LAP_POSITIONS: PacketLapPositionsData.from_bytes,
}


def decode_packet(data: bytes) -> Optional[object]:
    if len(data) < HEADER_SIZE:
        return None

    try:
        packet_id = PacketID(data[HEADER_SIZE - 2])
        decoder = PACKET_DECODERS.get(packet_id)
        if decoder:
            return decoder(data)
    except (ValueError, IndexError):
        pass

    return None
