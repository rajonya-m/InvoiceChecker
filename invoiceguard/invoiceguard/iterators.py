"""A hand-made iterator (CONCEPT: __iter__ and __next__)."""


class BatchIterator:
    """Splits a list into smaller lists of `size` items.

    for batch in BatchIterator([1,2,3,4,5], 2):  ->  [1,2] then [3,4] then [5]
    """

    def __init__(self, items, size):
        self.items = items
        self.size = size
        self.position = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.position >= len(self.items):
            raise StopIteration               # tells the for-loop to stop
        batch = self.items[self.position:self.position + self.size]
        self.position += self.size
        return batch
