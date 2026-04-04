# udp/packet_decoder.py

from .packet_definitions import (
    PacketID,
    PacketHeader,
    PacketMotionData,
    PacketSessionData,
    PacketLapData,
    PacketEventData,
    PacketParticipantsData,
    PacketCarSetupsData,
    PacketCarTelemetryData,
    PacketCarStatusData,
    PacketFinalClassificationData,
    PacketLobbyInfoData,
    PacketCarDamageData,
    PacketSessionHistoryData,
    PacketTyreSetsData,
    PacketMotionExData,
)


class PacketDecoder:
    def decode(self, data: bytes):
        header = PacketHeader.from_bytes(data)

        pid = header.raw[5]  # placeholder until header is defined

        if pid == PacketID.MOTION:
            return self.decode_motion(data, header)
        if pid == PacketID.SESSION:
            return self.decode_session(data, header)
        if pid == PacketID.LAP_DATA:
            return self.decode_lap_data(data, header)
        if pid == PacketID.EVENT:
            return self.decode_event(data, header)
        if pid == PacketID.PARTICIPANTS:
            return self.decode_participants(data, header)
        if pid == PacketID.CAR_SETUPS:
            return self.decode_car_setups(data, header)
        if pid == PacketID.CAR_TELEMETRY:
            return self.decode_car_telemetry(data, header)
        if pid == PacketID.CAR_STATUS:
            return self.decode_car_status(data, header)
        if pid == PacketID.FINAL_CLASSIFICATION:
            return self.decode_final_classification(data, header)
        if pid == PacketID.LOBBY_INFO:
            return self.decode_lobby_info(data, header)
        if pid == PacketID.CAR_DAMAGE:
            return self.decode_car_damage(data, header)
        if pid == PacketID.SESSION_HISTORY:
            return self.decode_session_history(data, header)
        if pid == PacketID.TYRE_SETS:
            return self.decode_tyre_sets(data, header)
        if pid == PacketID.MOTION_EX:
            return self.decode_motion_ex(data, header)

        return None


    # ------------------------------------------------------------
    # Packet decode stubs (we fill these once you send field tables)
    # ------------------------------------------------------------

    def decode_motion(self, data, header):
        return PacketMotionData(header)

    def decode_session(self, data, header):
        return PacketSessionData(header)

    def decode_lap_data(self, data, header):
        return PacketLapData(header, lap_data=[])

    def decode_event(self, data, header):
        return PacketEventData(header)

    def decode_participants(self, data, header):
        return PacketParticipantsData(header)

    def decode_car_setups(self, data, header):
        return PacketCarSetupsData(header)

    def decode_car_telemetry(self, data, header):
        offset = header.size

        cars = []
        for _ in range(22):
            fields = CAR_TELEMETRY_STRUCT.unpack_from(data, offset)
            offset += CAR_TELEMETRY_STRUCT.size

            car = CarTelemetryData(
                m_speed=fields[0],
                m_throttle=fields[1],
                m_steer=fields[2],
                m_brake=fields[3],
                m_clutch=fields[4],
                m_gear=fields[5],
                m_engineRPM=fields[6],
                m_drs=fields[7],
                m_revLightsPercent=fields[8],
                m_revLightsBitValue=fields[9],
                m_brakesTemperature=fields[10:14],
                m_tyresSurfaceTemperature=fields[14:18],
                m_tyresInnerTemperature=fields[18:22],
                m_engineTemperature=fields[22],
                m_tyresPressure=fields[23:27],
                m_surfaceType=fields[27:31],
            )
            cars.append(car)


        # Remaining fields
        mfd_primary = data[offset]
        mfd_secondary = data[offset + 1]
        suggested_gear = struct.unpack_from("<b", data, offset + 2)[0]

        return PacketCarTelemetryData(
            header=header,
            car_telemetry_data=cars,
            m_mfdPanelIndex=mfd_primary,
            m_mfdPanelIndexSecondaryPlayer=mfd_secondary,
            m_suggestedGear=suggested_gear,
        )

    def decode_car_status(self, data, header):
        offset = header.size  # once we fill header format

        car_status_list = []

        for _ in range(22):
            fields = CAR_STATUS_STRUCT.unpack_from(data, offset)
            offset += CAR_STATUS_STRUCT.size

            car_status_list.append(CarStatusData(*fields))

        return PacketCarStatusData(
            header=header,
            car_status_data=car_status_list
        )


    def decode_final_classification(self, data, header):
        return PacketFinalClassificationData(header)

    def decode_lobby_info(self, data, header):
        return PacketLobbyInfoData(header)

    def decode_car_damage(self, data, header):
        return PacketCarDamageData(header)

    def decode_session_history(self, data, header):
        return PacketSessionHistoryData(header)

    def decode_tyre_sets(self, data, header):
        return PacketTyreSetsData(header)

    def decode_motion_ex(self, data, header):
        return PacketMotionExData(header)
