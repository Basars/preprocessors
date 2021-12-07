class Statistic:

    def __init__(self, *statistics):
        self._container = {}
        for statistic in statistics:
            for k, v in statistic.container.items():
                self.increase(k, v)
            pass

    @property
    def container(self) -> dict:
        return self._container

    def increase(self, k, v):
        if k in self._container:
            self._container[k] = self._container[k] + v
        else:
            self._container[k] = v

    @staticmethod
    def from_key_value(k, v):
        statistic = Statistic()
        statistic.increase(k, v)
        return statistic
