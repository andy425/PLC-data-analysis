import snap7
from snap7.util import get_dword, get_int
from datetime import datetime


class PLCClient:
    """Simple wrapper around snap7.client.Client."""

    CYCLE_TIME_DB = 9994
    STATUS_DB = 1505

    # Offsets (in bytes) of the cycle time values inside DB9994. Each entry
    # represents the start of a 4 byte TIME value for a cell.
    CYCLE_TIME_OFFSETS = [
        6, 24, 42, 60, 78, 96, 114, 132, 150,
        168, 186, 204, 222, 240, 258, 276
    ]

    def __init__(self, ip: str, rack: int = 0, slot: int = 1, cells: int | None = None):
        self.ip = ip
        self.rack = rack
        self.slot = slot
        # Default to reading all known offsets
        self.cells = cells if cells is not None else len(self.CYCLE_TIME_OFFSETS)
        self.client = snap7.client.Client()

    def connect(self):
        if not self.client.get_connected():
            self.client.connect(self.ip, self.rack, self.slot)

    def disconnect(self):
        if self.client.get_connected():
            self.client.disconnect()

    def read_cycle_times(self):
        """Read cycle times for all configured cells."""
        if self.cells > len(self.CYCLE_TIME_OFFSETS):
            raise ValueError("cells exceeds known cycle time offsets")
        # Read enough bytes to cover the highest offset
        max_offset = self.CYCLE_TIME_OFFSETS[self.cells - 1]
        data = self.client.db_read(self.CYCLE_TIME_DB, 0, max_offset + 4)
        cycle_times = [
            get_dword(data, off) / 1000.0  # TIME is in ms, convert to seconds
            for off in self.CYCLE_TIME_OFFSETS[:self.cells]
        ]
        return cycle_times

    def read_status(self):
        """Read status for all configured cells as INT."""
        size = self.cells * 2  # assuming INT (2 bytes) per cell
        data = self.client.db_read(self.STATUS_DB, 0, size)
        status = [get_int(data, i * 2) for i in range(self.cells)]
        return status

    def read_all(self):
        timestamp = datetime.utcnow()
        cycles = self.read_cycle_times()
        status = self.read_status()
        return timestamp, cycles, status
