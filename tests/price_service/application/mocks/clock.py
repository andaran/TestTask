class FixedClock:
    __timestamp: int

    def __init__(self, timestamp: int) -> None:
        self.__timestamp = timestamp

    def now(self) -> int:
        return self.__timestamp
