import io
import json
import os
import wave
import audioop
from collections import defaultdict

import face_recognition
import numpy as np


class Saver:
    def __init__(self):
        try:
            with open(os.path.join('data', 'data.json')) as f:
                self.data = defaultdict(dict,json.load(f))
        except json.JSONDecodeError:
            self.data = defaultdict(dict)
        except FileNotFoundError:
            self.data = defaultdict(dict)
    
    def add(self, uid, type_, filename, file_data):
        print(self.data)
        
        path = os.path.join(os.path.join('data', uid), type_)
        
        try:
            self.data[uid][type_].append(filename)
        except KeyError:
            self.data[uid][type_] = [filename]
        
        print(self.data)
        
        if not os.path.exists(path):
            os.makedirs(path)
            
        with open(os.path.join(path, filename), 'wb') as f:
            f.write(file_data)
            
    def save(self):
        with open(os.path.join('data', 'data.json'), 'w') as f:
            json.dump(self.data, f, indent=2)


def adjust_audio(audio):
    return audio


def is_face(image):
    faces = face_recognition.face_locations(face_recognition.load_image_file(io.BytesIO(image)))
    return bool(faces)


def main():
    print(is_face(open('test_data/test_img/games-the-witcher-3-wild-hunt-90309.jpg', 'rb').read()))
    pass


if __name__ == '__main__':
    main()
