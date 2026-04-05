# udp/packet_decoder.py

from .packet_definitions import (
    PacketID,
    PacketHeader,
    PacketMotionData,
    PacketSessionData,
    LapData,
    PacketLapData,
    PacketEventData,
    ParticipantData,
    PacketParticipantsData,
    CarSetupData,
    PacketCarSetupData,
    CarTelemetryData,
    PacketCarTelemetryData,
    CarStatusData,
    PacketCarStatusData,
    FinalClassificationData,
    PacketFinalClassificationData,
    LobbyInfoData,
    PacketLobbyInfoData,
    CarDamageData,
    PacketCarDamageData,
    PacketSessionHistoryData,
    TyreSetData,
    PacketTyreSetsData,
    PacketMotionExData,
    PacketTimeTrialData,
    PacketLapPositionsData,
    decode_packet,
)


class PacketDecoder:
    def decode(self, data: bytes):
        return decode_packet(data)

    def decode_header(self, data: bytes) -> PacketHeader | None:
        if len(data) < 28:
            return None
        return PacketHeader.from_bytes(data)

    def get_packet_id(self, data: bytes) -> int | None:
        """Extract packet ID from raw bytes without full decode."""
        if len(data) < 7:
            return None
        return data[6]
