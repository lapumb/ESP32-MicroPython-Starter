class SimpleQueue:

    max_size: int = 0
    queue: list = list()

    def __init__(self, max_size: int) -> None:
        assert max_size >= 0
        self.max_size = max_size

    def __str__(self) -> str:
        return str(self.queue)

    def enqueue(self, data) -> None:
        assert data is not None
        if self.current_number_of_elements() >= self.max_size:
            print("Queue (size: {}) is full, removing oldest element..".format(self.max_size))
            self.queue.pop(0)

        self.queue.append(data)

    def dequeue(self):
        if self.current_number_of_elements() == 0:
            return None

        return self.queue.pop(0)

    def current_number_of_elements(self) -> int:
        return len(self.queue)