import os


class Config:
    def __init__(self):
        try:
            self.nats = os.environ["NATS_URL"]
        except Exception:
            self.nats = "nats://46.29.236.28:4222"
