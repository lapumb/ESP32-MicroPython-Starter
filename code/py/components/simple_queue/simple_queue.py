class SimpleQueue:

    _max_size: int = 0
    _queue: list = list()

    def __init__(self, max_size: int) -> None:
        assert max_size > 0
        self._max_size = max_size

    def __str__(self) -> str:
        return str(self._queue)

    def enqueue(self, data) -> None:
        assert data is not None
        if self.current_number_of_elements() >= self._max_size:
            print("Queue (size: {}) is full, removing oldest element..".format(self._max_size))
            self._queue.pop(0)

        self._queue.append(data)

    def dequeue(self) -> Any:
        if self.current_number_of_elements() == 0:
            return None

        return self._queue.pop(0)

    def current_number_of_elements(self) -> int:
        return len(self._queue)

    def get_max_number_of_elements(self) -> int:
        return self._max_size