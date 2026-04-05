# f1/weather_manager.py

from core.events import EventType


class WeatherManager:
    """
    Detects weather-related state transitions:
    - current weather changes
    - forecast changes
    - rain prediction
    - crossover points (slicks → inters → wets)
    - track drying / worsening conditions
    Emits events to TelemetryState → EventRouter → EngineerBrain.
    """

    def __init__(self, telemetry_state):
        self.telemetry_state = telemetry_state

        # Cached state
        self.last_weather = None
        self.last_forecast = None
        self.last_rain_prediction = None
        self.last_track_wetness = None
        self.crossover_to_inters_announced = False
        self.crossover_to_slicks_announced = False
        self.crossover_to_wets_announced = False
        self.rain_announced = False
        self.last_track_drying = False
        self.last_track_worsening = False

    # ---------------------------------------------------------
    # Internal helper
    # ---------------------------------------------------------
    def _emit(self, event_type, **payload):
        self.telemetry_state._emit(event_type, **payload)

    # ---------------------------------------------------------
    # Main update loop
    # ---------------------------------------------------------
    def update(self, session, status, telemetry_state=None):
        """
        session: SessionData
        status: carStatus for player
        telemetry_state: TelemetryState (for stub properties)
        """

        # -----------------------------------------------------
        # CURRENT WEATHER
        # -----------------------------------------------------
        current_weather = session.m_weather
        track_wetness = telemetry_state.track_wetness if telemetry_state else 0

        if self.last_weather is None:
            self.last_weather = current_weather

        if current_weather != self.last_weather:
            self._emit(EventType.WEATHER_CHANGED,
                       old=self.last_weather,
                       new=current_weather)

        # -----------------------------------------------------
        # FORECAST CHANGES
        # -----------------------------------------------------
        forecast = list(session.m_weatherForecastSamples)

        if self.last_forecast is None:
            self.last_forecast = forecast

        # Compare segment-by-segment
        for i, seg in enumerate(forecast):
            if i >= len(self.last_forecast):
                continue

            old_seg = self.last_forecast[i]
            new_seg = seg

            # Weather type changed
            if new_seg.m_weather != old_seg.m_weather:
                self._emit(EventType.FORECAST_WEATHER_CHANGE,
                           segment=i,
                           old_weather=old_seg.m_weather,
                           new_weather=new_seg.m_weather)

            # Rain percentage change
            if new_seg.m_rainPercentage != old_seg.m_rainPercentage:
                self._emit(EventType.FORECAST_RAIN_CHANGE,
                           segment=i,
                           old_pct=old_seg.m_rainPercentage,
                           new_pct=new_seg.m_rainPercentage)

                # Rain coming soon
                if new_seg.m_rainPercentage > 50 and not self.rain_announced:
                    self.rain_announced = True
                    self._emit(EventType.RAIN_SOON,
                               minutes=new_seg.m_timeOffset)

        # -----------------------------------------------------
        # RAIN PREDICTION
        # -----------------------------------------------------
        rain_minutes = session.m_weatherForecastSamples[0].m_rainPercentage
        if rain_minutes > 50 and self.last_rain_prediction != rain_minutes:
            self.last_rain_prediction = rain_minutes
            self._emit(EventType.WEATHER_UPDATE,
                       minutes=rain_minutes)

        # -----------------------------------------------------
        # TRACK DRYING / WORSENING
        # -----------------------------------------------------
        if self.last_track_wetness is not None:
            if track_wetness < self.last_track_wetness and not self.last_track_drying:
                self._emit(EventType.TRACK_DRYING)
                self.last_track_drying = True
                self.last_track_worsening = False

            elif track_wetness > self.last_track_wetness and not self.last_track_worsening:
                self._emit(EventType.TRACK_WORSENING)
                self.last_track_worsening = True
                self.last_track_drying = False

        self.last_track_wetness = track_wetness

        # -----------------------------------------------------
        # CROSSOVER TO INTERMEDIATES
        # -----------------------------------------------------
        if track_wetness > 60 and not self.crossover_to_inters_announced:
            self._emit(EventType.CROSSOVER_TO_INTERS)
            self.crossover_to_inters_announced = True
            self.crossover_to_slicks_announced = False
            self.crossover_to_wets_announced = False

        # -----------------------------------------------------
        # CROSSOVER TO FULL WETS
        # -----------------------------------------------------
        if track_wetness > 85 and not self.crossover_to_wets_announced:
            self._emit(EventType.CROSSOVER_TO_FULL_WETS)
            self.crossover_to_wets_announced = True
            self.crossover_to_inters_announced = False
            self.crossover_to_slicks_announced = False

        # -----------------------------------------------------
        # CROSSOVER BACK TO SLICKS
        # -----------------------------------------------------
        if track_wetness < 30 and not self.crossover_to_slicks_announced:
            self._emit(EventType.CROSSOVER_TO_SLICKS)
            self.crossover_to_slicks_announced = True
            self.crossover_to_inters_announced = False
            self.crossover_to_wets_announced = False

        # -----------------------------------------------------
        # Update cached values
        # -----------------------------------------------------
        self.last_weather = current_weather
        self.last_forecast = forecast
