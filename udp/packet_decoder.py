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
