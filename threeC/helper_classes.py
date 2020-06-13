class MaxValueTracker:
    def __init__(self):
        self.max_value = 0.0
        self.current_value = 0.0

    def reset_current_value(self):
        self.current_value = 0.0

    def add_current_value(self, val):
        self.current_value += val

    def update_max_value(self, current_val=None, reset=False):
        if current_val is None:
            current_val = self.current_value
        self.max_value = max(self.max_value, current_val)
        if reset:
            self.reset_current_value()
