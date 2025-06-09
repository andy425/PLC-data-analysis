import threading
import time
from datetime import datetime

from flask import Flask, render_template
from sqlalchemy import func

from plc_client import PLCClient
from database import CycleTime, CellStatus, init_db


PollingInterval = 1.0  # seconds


class PLCMonitor(threading.Thread):
    def __init__(self, plc: PLCClient, Session):
        super().__init__(daemon=True)
        self.plc = plc
        self.Session = Session
        self.running = True

    def run(self):
        session = self.Session()
        try:
            self.plc.connect()
        except Exception as e:
            print(f"PLC connection failed: {e}")
            self.running = False
            session.close()
            return
        try:
            while self.running:
                timestamp = datetime.utcnow()
                cycles = self.plc.read_cycle_times()
                statuses = self.plc.read_status()
                for i, ct in enumerate(cycles):
                    session.add(CycleTime(timestamp=timestamp, cell=i, cycle_time=ct))
                for i, st in enumerate(statuses):
                    session.add(CellStatus(timestamp=timestamp, cell=i, status=st))
                session.commit()
                time.sleep(PollingInterval)
        finally:
            self.plc.disconnect()
            session.close()

    def stop(self):
        self.running = False


app = Flask(__name__)
Session = init_db()


def start_monitor(ip, rack=0, slot=1, cells=None):
    plc = PLCClient(ip, rack, slot, cells)
    monitor = PLCMonitor(plc, Session)
    monitor.start()
    return monitor


@app.route('/')
def index():
    session = Session()
    try:
        last_times = (session.query(CycleTime)
                       .order_by(CycleTime.timestamp.desc())
                       .limit(10)
                       .all())
        last_times.reverse()  # oldest first
        if last_times:
            average = sum(ct.cycle_time for ct in last_times) / len(last_times)
        else:
            average = 0
    finally:
        session.close()
    return render_template('index.html', cycle_times=last_times, average=average)


if __name__ == '__main__':
    # Update IP, rack, slot, cells as needed
    monitor = start_monitor('192.168.3.1', rack=0, slot=1)
    app.run(host='0.0.0.0', port=5000)
