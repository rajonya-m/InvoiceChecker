import pytest

from invoiceguard.decorators import retry
from invoiceguard.iterators import BatchIterator


def test_batch_iterator():
    assert list(BatchIterator([1, 2, 3, 4, 5], 2)) == [[1, 2], [3, 4], [5]]


def test_batch_iterator_empty():
    assert list(BatchIterator([], 3)) == []


def test_retry_succeeds_after_failures():
    calls = {"n": 0}

    @retry(times=3, delay=0)
    def flaky():
        calls["n"] += 1
        if calls["n"] < 3:
            raise ValueError("not yet")
        return "ok"

    assert flaky() == "ok" and calls["n"] == 3


def test_retry_gives_up():
    @retry(times=2, delay=0)
    def always_fails():
        raise ValueError("nope")

    with pytest.raises(ValueError):
        always_fails()
