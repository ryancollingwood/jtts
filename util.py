class TimeLimitedKeyTester(object):
    def __init__(self, keys, delay):
        self.time_accumulator = delay * 2
        self.keys = keys
        self.delay = delay

    def update(self, dt, keystate):
        self.time_accumulator += dt
        if any(keystate[key] for key in self.keys):
            if self.time_accumulator > self.delay:
                self.time_accumulator = 0.0
                return True
        return False


class SpacingTrigger(object):
    def __init__(self, delay):
        self.time_accumulator = delay * 2
        self.delay = delay

    def update(self, dt):
        self.time_accumulator += dt

    def attempt(self):
        if self.time_accumulator > self.delay:
            self.time_accumulator = 0.0
            return True
        return False


def distSq(a, b):
    (ax, ay), (bx, by) = a, b
    return (ax - bx) ** 2 + (ay - by) ** 2
