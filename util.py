from math import atan2, pi

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


def rad_between(p1, p2):
    x_diff = p2[0] - p1[0]
    y_diff = p2[1] - p1[1]

    return atan2(y_diff, x_diff)


def angle_between(p1, p2):
    rad = rad_between(p1, p2)
    return rad * (180.0 / pi)


def normalise_angle(angle):
    a = angle

    if a > 360:
        a = a % 360
    elif a < - 360:
        a = a % -360

    if angle < 0:
        a += 360

    return a


def circle_segment(angle):
    a = normalise_angle(angle)

    segments = [
        [157.5, 202.5, 1],
        [202.5, 247.5, 2],
        [247.5, 292.5, 3],
        [292.5, 337.5, 4],
        [337.5, 360, 5],
        [0, 22.5, 5],
        [22.5, 67.5, 6],
        [67.5, 112.5, 7],
        [112.5, 157.5, 8]
    ]

    result = [x[2] for x in segments if a >= x[0] and a <= x[1]]

    return result[0]


def test_rad_between():
    assert(rad_between([0, 0], [0, 1]) == 1.5707963267948966)


def test_angle_between():
    assert(angle_between([0, 0], [0, 1]) == 90.0)

