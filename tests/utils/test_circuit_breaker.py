import time

import pytest

from src.config.errors import CircuitBreakerError
from src.utils.circuit_breaker import CircuitBreaker


class TestCircuitBreaker:

    @staticmethod
    def always_succeed():
        return "Success"

    @staticmethod
    def always_fail():
        raise Exception("Service failure")

    def test_circuit_closed_on_success(self):
        cb = CircuitBreaker(failure_threshold=3)
        result = cb.call(self.always_succeed)
        assert result == "Success"
        assert cb.state == "CLOSED"
        assert cb.failure_count == 0

    def test_circuit_opens_after_failures(self):
        cb = CircuitBreaker(failure_threshold=3)

        for _ in range(3):
            with pytest.raises(Exception, match="Service failure"):
                cb.call(self.always_fail)

        assert cb.state == "OPEN"
        assert cb.failure_count == 3

    def test_circuit_blocks_calls_when_open(self):
        cb = CircuitBreaker(failure_threshold=1)

        with pytest.raises(Exception, match="Service failure"):
            cb.call(self.always_fail)

        with pytest.raises(
            CircuitBreakerError, match="Service is unavailable. Try again later."
        ):
            cb.call(self.always_succeed)

        assert cb.state == "OPEN"

    def test_circuit_resets_after_success(self):
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout=1)

        with pytest.raises(Exception, match="Service failure"):
            cb.call(self.always_fail)

        assert cb.state == "OPEN"
        time.sleep(1.1)
        assert cb._recovery_period_elapsed() == True

        result = cb.call(self.always_succeed)
        assert result == "Success"
        assert cb.state == "CLOSED"
        assert cb.failure_count == 0

    def test_circuit_does_not_reset_on_failure_in_half_open(self):
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout=1)

        with pytest.raises(Exception, match="Service failure"):
            cb.call(self.always_fail)

        assert cb.state == "OPEN"
        time.sleep(1.1)
        assert cb._recovery_period_elapsed() == True

        with pytest.raises(Exception, match="Service failure"):
            cb.call(self.always_fail)

        assert cb.state == "OPEN"

    def test_circuit_half_open_after_timeout(self):
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout=1)

        with pytest.raises(Exception, match="Service failure"):
            cb.call(self.always_fail)

        assert cb.state == "OPEN"
        time.sleep(1.1)
        assert cb._recovery_period_elapsed() == True

        cb.call(self.always_succeed)
        assert cb.state == "CLOSED"

    def test_failure_threshold_not_exceeded(self):
        cb = CircuitBreaker(failure_threshold=3)

        with pytest.raises(Exception, match="Service failure"):
            cb.call(self.always_fail)

        with pytest.raises(Exception, match="Service failure"):
            cb.call(self.always_fail)

        assert cb.state == "CLOSED"
        assert cb.failure_count == 2

        with pytest.raises(Exception, match="Service failure"):
            cb.call(self.always_fail)

        assert cb.state == "OPEN"
        assert cb.failure_count == 3
