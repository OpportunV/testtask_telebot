import io
import json
import os
from collections import defaultdict
from threading import Timer

import face_recognition


class Saver:
    def __init__(self, interval=3600):
        try:
            with open(os.path.join('data', 'data.json')) as f:
                self.data = defaultdict(dict,json.load(f))
        except json.JSONDecodeError:
            self.data = defaultdict(dict)
        except FileNotFoundError:
            self.data = defaultdict(dict)
        
        # Calling save function every "interval" seconds
        Timer(interval, self.save).start()
    
    def add(self, uid: str, type_: str, filename: str, file_data: bytes):
        """
        Adds data to dict object and saves file
        :param uid: string, user directory
        :param type_: string, either 'audio' or 'video' , subdirectory for user directory
        :param filename: string
        :param file_data: bytes
        :return: None
        """
        path = os.path.join(os.path.join('data', uid), type_)

        if not os.path.exists(path):
            os.makedirs(path)

        with open(os.path.join(path, filename), 'wb') as f:
            f.write(file_data)
        
        if type_ == 'audio':
            convert_audio(path, filename)
            filename = f'{filename.rsplit(".", 1)[0]}.wav'
        
        try:
            self.data[uid][type_].append(filename)
        except KeyError:
            self.data[uid][type_] = [filename]
        
    def save(self):
        """
        saves dict object to json file
        :return: None
        """
        with open(os.path.join('data', 'data.json'), 'w') as f:
            json.dump(self.data, f, indent=2)


def convert_audio(path: str, filename:str, rate: int = 16000):
    """
    Converts audio executing console ffmpeg command
    :param path: string
    :param filename: string
    :param rate: int, output rate, default to 16000
    :return: None
    """
    full_path = os.path.join(path, filename)
    full_path_out = f'{full_path.rsplit(".", 1)[0]}.wav'
    if not os.path.exists(full_path_out):
        os.system(f'ffmpeg -loglevel quiet -i {full_path} -ar {rate} {full_path_out}')
    os.remove(full_path)


def contains_face(image: bytes) -> bool:
    """
    Checks if there is at least one face on the image or not
    :param image: bytes
    :return: bool
    """
    faces = face_recognition.face_locations(face_recognition.load_image_file(io.BytesIO(image)))
    return bool(faces)
