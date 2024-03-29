# face_recog.py
# 샘플 모은 후 인식하는 코드
#모듈불러오기
import face_recognition
import cv2
import camera
import os
import numpy as np

import Facial_Recognition_Part1
class FaceRecog():
    def __init__(self):
        # Using OpenCV to capture from device 0. If you have trouble capturing
        # from a webcam, comment the line below out and use a video file
        # instead.
        self.camera = camera.VideoCamera()
        self.known_face_encodings = []
        self.known_face_names = []
        # Load sample pictures and learn how to recognize it.

        #knowns 디렉토리에서 사진 파일을 읽습니다. 파일 이름으로부터 사람 이름을 추출합니다
        dirname = 'knowns'
        files = os.listdir(dirname)
        for filename in files:
            name, ext = os.path.splitext(filename)
            if ext == '.jpg':
                self.known_face_names.append(name)

                pathname = os.path.join(dirname, filename)
                # 사진에서 얼굴 영역을 알아내고, face landmarks라 불리는
                # 68개 얼굴 특징의 위치를 분석한 데이터를 known_face_encodings에 저장합니다.
                img = face_recognition.load_image_file(pathname)
                #face_encoding = face_recognition.face_encodings(img)[0]
                face_encodings = face_recognition.face_encodings(img)

                if len(face_encodings) > 0:
                    face_encoding = face_encodings[0]
                    self.known_face_encodings.append(face_encoding)

        # Initialize some variables
        self.face_locations = []
        self.face_encodings = []
        self.face_names = []
        self.process_this_frame = True

    def __del__(self):
        del self.camera

    def get_frame(self):
        # Grab a single frame of video
        #카메라로부터 frame을 읽어서 1/4 크기로 줄입니다. 이것은 계산양을 줄이기 위해서 입니다.
        frame = self.camera.get_frame()

        # Resize frame of video to 1/4 size for faster face recognition processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        rgb_small_frame = small_frame[:, :, ::-1]

        # Only process every other frame of video to save time
        #계산 양을 더 줄이기 위해서 두 frame당 1번씩만 계산합니다.
        if self.process_this_frame:
            # Find all the faces and face encodings in the current frame of video
            #읽은 frame에서 얼굴 영역과 특징을 추출합니다.
            self.face_locations = face_recognition.face_locations(rgb_small_frame)
            self.face_encodings = face_recognition.face_encodings(rgb_small_frame, self.face_locations)

            self.face_names = []
            for face_encoding in self.face_encodings:

                # See if the face is a match for the known face(s)
                #Frame에서 추출한 얼굴 특징과 knowns에 있던 사진 얼굴의 특징을 비교하여,
                # (얼마나 비슷한지) 거리 척도로 환산합니다.
                # 거리(distance)가 가깝다는 (작다는) 것은 서로 비슷한 얼굴이라는 의미 입니다.

                distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
                min_value = min(distances)

                # tolerance: How much distance between faces to consider it a match. Lower is more strict.
                # 0.6 is typical best performance.
                #실험상, 거리가 0.6 이면 다른 사람의 얼굴입니다. 이런 경우의 이름은 Unknown 입니다.
                #거리가 0.6 이하이고, 최소값을 가진 사람의 이름을 찾습니다.
                name = "Unknown"
                if min_value < 0.6:
                    index = np.argmin(distances)
                    name = self.known_face_names[index]

               # if name=="Unknown":
                #    exec(open(Facial_Recognition_Part1).read())


                self.face_names.append(name)

        self.process_this_frame = not self.process_this_frame
#찾은 사람의 얼굴 영역과 이름을 비디오 화면에 그립니다.
        # Display the results
        for (top, right, bottom, left), name in zip(self.face_locations, self.face_names):
            # Scale back up face locations since the frame we detected in was scaled to 1/4 size
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            # Draw a box around the face
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

            # Draw a label with a name below the face
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

        return frame

    def get_jpg_bytes(self):
        frame = self.get_frame()
        # We are using Motion JPEG, but OpenCV defaults to capture raw images,
        # so we must encode it into JPEG in order to correctly display the
        # video stream.
        ret, jpg = cv2.imencode('.jpg', frame)
        return jpg.tobytes()


if __name__ == '__main__':
    face_recog = FaceRecog()
    print(face_recog.known_face_names)
    while True:
        frame = face_recog.get_frame()
        # show the frame
        cv2.imshow("Frame", frame)
        key = cv2.waitKey(1) & 0xFF

        # if the `q` key was pressed, break from the loop
        if key == ord("q"):
            break

#########################################3
        if key == ord("t"):
            face_classifier = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
            def face_extractor(img):
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                faces = face_classifier.detectMultiScale(gray, 1.3, 5)

                if faces is ():
                    return None

                for (x, y, w, h) in faces:
                    cropped_face = img[y:y + h, x:x + w]

                return cropped_face


            cap = cv2.VideoCapture(0)
            count = 0

            while True:
                ret, frame = cap.read()
                if face_extractor(frame) is not None:
                    count += 1
                    face = cv2.resize(face_extractor(frame), (200, 200))
                    face = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)

                    file_name_path = 'knowns/user' + str(count) + '.jpg'
                    cv2.imwrite(file_name_path, face)

                    cv2.putText(face, str(count), (50, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)
                    cv2.imshow('Face Cropper', face)
                else:
                    print("Face not Found")
                    pass

                if cv2.waitKey(1) == 13 or count == 15:
                    break

            cap.release()
            print('Colleting Samples Complete!!!')




            break

    # do a bit of cleanup
    cv2.destroyAllWindows()
    print('finish')



