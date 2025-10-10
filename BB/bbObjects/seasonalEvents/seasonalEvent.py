class SeasonalEvent:
    def activate(self):
        pass

    def deactivate(self):
        pass

    def __del__(self):
        self.deactivate()
