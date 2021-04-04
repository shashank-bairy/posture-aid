class PostureAidConfig:
    __conf = {
        "PAD_X": 30,
        "PAD_Y": 30,
        "MODEL": 101,
        "CAM_ID": 0,
        "CORRECT_POS": (0,0,0,0),
        "SCALE_FACTOR": 0.7125,
        "ALARM_FILE": './data/audio/alarm_audio.wav'
    }
    __setters = []

    @staticmethod
    def config(key):
        return PostureAidConfig.__conf[key]

    @staticmethod
    def set(key, value):
        if key in PostureAidConfig.__setters:
            PostureAidConfig.__conf[key] = value
        else:
            raise KeyError("Key not accepted in set() method")