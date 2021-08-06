# -*- coding: utf-8 -*-
"""takeCaptureWebCam.ipynb
Automatically generated by Colaboratory.
Original file is located at
    https://colab.research.google.com/drive/1OJfagWPPLl80fVyYZxjMcUhWA2hSZ_Bd
"""


"""
코드 깔끔하게 수정할 수 있는 것
captureImage 스트링으로 변경?
메이크업 사진 선택 반복문
"""

import dlib
import matplotlib.pyplot as plt
import tensorflow.compat.v1 as tf
tf.disable_v2_behavior()
tf.disable_eager_execution()
import numpy as np
import cv2 as cv

"""# 모델 불러오기"""

detector = dlib.get_frontal_face_detector()
sp = dlib.shape_predictor('shape_predictor_5_face_landmarks.dat')

"""# 이미지 불러오기"""

webcam = True

cap = cv.VideoCapture(0)

while True:
    if webcam: success, frame = cap.read()
    else:
        # img = dlib.load_rgb_image('face.jpg')
        # plt.figure(figsize=(16,10))
        break

    cv.imshow('frame', frame)

    key = cv.waitKey(1)
    if key == 27:
        break
    elif key == ord('1'):
        cv.imwrite('captureImg.png', frame)
        img = cv.imread('captureImg.png')
        break

cv.destroyWindow('frame')

"""# 사용자에게 메이크업 사진 팝업 후 입력 받기"""

mkimg0 = dlib.load_rgb_image('test_data/makeup/vFG112.png')
mkimg1 = dlib.load_rgb_image('test_data/makeup/vFG756.png')
mkimg2 = dlib.load_rgb_image('test_data/makeup/XMY-014.png')
mkimg3 = dlib.load_rgb_image('test_data/makeup/XMY-074.png')
mkimg4 = dlib.load_rgb_image('test_data/makeup/XMY-266.png')

fig2, axe2s = plt.subplots(1, 5, figsize=(20,10))

#나중에 for문으로 변경
axe2s[0].set_title('1')
axe2s[0].imshow(mkimg0)
axe2s[1].set_title('2')
axe2s[1].imshow(mkimg1)
axe2s[2].set_title('3')
axe2s[2].imshow(mkimg2)
axe2s[3].set_title('4')
axe2s[3].imshow(mkimg3)
axe2s[4].set_title('5')
axe2s[4].imshow(mkimg4)

plt.show()

print("메이크업 하고 싶은 사진을 선택하세요")
val = input()
print("다음 메이크업 사진을 선택하셨습니다. ", val)

"""# 얼굴 수평 맞추기 함수화"""

def align_faces(img):
    dets = detector(img, 1) # 얼굴 검출

    objs = dlib.full_object_detections() # 얼굴 이목구비 검출

    for detection in dets:
        s = sp(img, detection)
        objs.append(s)

    faces = dlib.get_face_chips(img, objs, size=256, padding=0.35) # 검출한 이목구비로 영역 자르기 및 수평 맞추기

    return faces

"""# BeautyGAN 트레이닝 불러오기"""

sess = tf.Session()
sess.run(tf.global_variables_initializer())

saver = tf.train.import_meta_graph('models/model.meta') # 모델의 그래프 불러오기
saver.restore(sess, tf.train.latest_checkpoint('models')) # 모델의 가중치 로드
graph = tf.get_default_graph()

# 그래프에서 노드 이름으로 텐서 불러오기
X = graph.get_tensor_by_name('X:0') # source (no makeup)
Y = graph.get_tensor_by_name('Y:0') # reference (makeup)
Xs = graph.get_tensor_by_name('generator/xs:0') # output

"""# 전처리 및 후처리"""

def preprocess(img):
    # 0~255 사이 값에서 -1~1 사이의  float 값으로 변경
    return img.astype(np.float32) / 127.5 - 1.

def postprocess(img):
    return ((img + 1.) * 127.5).astype(np.uint8)

"""# 이미지 불러오기"""

img1 = dlib.load_rgb_image('captureImg.png')
img1_faces = align_faces(img1)

if val == '1':
    img2_faces = align_faces(mkimg0)
elif val == '2':
    img2_faces = align_faces(mkimg1)
elif val == '3':
    img2_faces = align_faces(mkimg2)
elif val == '4':
    img2_faces = align_faces(mkimg3)
elif val == '5':
    img2_faces = align_faces(mkimg4)

#fig, axes = plt.subplots(1, 2, figsize=(16,10))
#axes[0].imshow(img1_faces[0]) # 이미지에서 얼굴 여러개 검출하였을 수도 있으니까 그 중 가장 첫번째 하나만 불러옴
#axes[1].imshow(img2_faces[0])

"""# 실행"""

src_img = img1_faces[0]
ref_img = img2_faces[0]

X_img = preprocess(src_img) # (256,256,3)
X_img = np.expand_dims(X_img, axis=0) # 배열에 차원 추가해 (1,256,256,3)으로 변경
Y_img = preprocess(ref_img)
Y_img = np.expand_dims(Y_img, axis=0)

output = sess.run(Xs, feed_dict={
    X: X_img,
    Y: Y_img
})

output_img = postprocess(output[0])

fig, axes = plt.subplots(1, 3, figsize=(20,10))
axes[0].set_title('Source')
axes[0].imshow(src_img)
axes[1].set_title('Reference')
axes[1].imshow(ref_img)
axes[2].set_title('Result')
axes[2].imshow(output_img)
plt.show()