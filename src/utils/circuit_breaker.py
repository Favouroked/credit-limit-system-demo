import time

from src.config.errors import CircuitBreakerError


class CircuitBreaker:
    def __init__(
        self, failure_threshold=3, recovery_timeout=5, max_attempts=1
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.max_attempts = max_attempts
        self.failure_count = 0
        self.state = "CLOSED"  # Can be 'CLOSED', 'OPEN', or 'HALF-OPEN'
        self.last_failure_time = None

    def call(self, func, *args, **kwargs):
        if self.state == "OPEN":
            if self._recovery_period_elapsed():
                self.state = "HALF-OPEN"
            else:
                raise CircuitBreakerError("Service is unavailable. Try again later.")

        try:
            result = func(*args, **kwargs)
            self._reset()
            return result
        except Exception as e:
            self._record_failure()
            raise e

    def _record_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"

    def _recovery_period_elapsed(self):
        if self.last_failure_time is None:
            return False
        return time.time() - self.last_failure_time >= self.recovery_timeout

    def _reset(self):
        self.failure_count = 0
        self.state = "CLOSED"
        self.last_failure_time = None
