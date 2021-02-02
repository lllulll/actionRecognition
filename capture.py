import cv2
import os
def handlevideo(filename):
    cap = cv2.VideoCapture(filename)
    ret,frame = cap.read()
    count = 1
    folder1 ="action/"
    if not os.path.exists(folder1):
        # 如果文件目录不存在则创建目录
        os.makedirs(folder1)
    count = 1
    while True:
        if count < 10:
            cv2.imwrite(folder1+str(0) + str(0) + str(count) + '.jpg', frame)
        elif count < 100:
            cv2.imwrite(folder1+str(0) + str(count) + '.jpg', frame)
        else:
            cv2.imwrite(folder1+str(count) + '.jpg', frame)
        ret,frame = cap.read()
        count +=1
        print(ret)
        if not ret:
            break
    f = open("test.list","w")
    f.write(folder1+" "+"0")
    f.close()