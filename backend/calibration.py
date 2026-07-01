class DistanceCalibration:
    def __init__(self, target_cm=130, tolerance=50):
        self.target_cm = target_cm
        self.tolerance = tolerance

    def evaluate(self, distance_cm):
        if distance_cm is None:
            return {
                "status": "NO_DATA",
                "message": "No distance detected"
            }

        diff = distance_cm - self.target_cm

        if abs(diff) <= self.tolerance:
            return {
                "status": "PERFECT",
                "message": "Perfect distance. You are well positioned."
            }

        elif distance_cm < self.target_cm:
            return {
                "status": "TOO_NEAR",
                "message": "You are too near. Move back from screen."
            }

        else:
            return {
                "status": "TOO_FAR",
                "message": "You are too far. Move closer to screen."
            }