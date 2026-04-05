# udp/udp_listener.py

import socket
from typing import Optional


class UDPListener:
    """
    Low-level UDP socket listener.
    Non-blocking. Returns raw packet bytes or None.
    """

    def __init__(self, ip: str = "0.0.0.0", port: int = 20777):
        self.ip = ip
        self.port = port

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.ip, self.port))

        # Non-blocking so telemetry_manager can poll every frame
        self.sock.setblocking(False)

    def poll(self) -> Optional[bytes]:
        """
        Returns:
            bytes | None
        """
        try:
            data, _ = self.sock.recvfrom(8192)
            return data
        except BlockingIOError:
            return None
