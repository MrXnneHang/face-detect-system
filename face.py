import os
import cv2
import numpy as np
import torch
from facenet_pytorch import MTCNN, InceptionResnetV1
from PIL import Image
from datetime import datetime
from util import load_config, read_userdata_from_path, custom_round, read_users_from_database
from insert import insert




def upload_users(mtcnn,resnet,device):
    users = []
    user_data = []
    config = load_config()
    imgs_dir = config["imgs_dir"]
    imgs = os.listdir(imgs_dir)
    imgs = [img for img in imgs if ".jpg" in img]
    img_paths = [os.path.join(imgs_dir, img) for img in imgs]
    for img_path in img_paths:
        img = Image.open(img_path)
        img = mtcnn(img)
        img = img.unsqueeze(0).to(device)
        feature = resnet(img)
        feature = feature.cpu().detach().numpy()
        feature = [custom_round(float(f)) for f in feature[0]]
        user_data = read_userdata_from_path(img_path)
        user_data.append(feature)
        user_data = tuple(user_data)
        users.append(user_data)

    insert(users)
    return tuple(user_data)


def detect_user(mtcnn,resnet,device):
    users = read_users_from_database()
    data_features = [torch.tensor(users[i]["features"]).to(device) for i in range(len(users))]
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break

        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(img)
        imgs = mtcnn(pil_img)
        landmarks, _, _ = mtcnn.detect(pil_img, landmarks=True)
        box = 0
        flag = 0
        matched_name = ""

        if imgs is not None:
            imgs = imgs.unsqueeze(0).to(device)
            features = [resnet(face.unsqueeze(0)) for face in imgs]
            

            for i, feature in enumerate(features):
                no_match = 0
                for index, data_feature in enumerate(data_features):
                    similarity = torch.dist(feature, data_feature, p=2)
                    print(similarity)
                    if similarity < 0.78:
                        matched_name = users[index]["name"]
                        print("发现匹配人员:", matched_name, similarity)
                        current_time = datetime.now()
                        print("发现时间:", current_time.strftime("%Y-%m-%d %H:%M:%S"))
                        frame_box = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
                        landmark = landmarks[i]
                        x1, y1, x2, y2 = landmark[:4].astype(int)
                        cv2.rectangle(frame_box, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        box = frame_box
                        flag = 1
                    else:
                        no_match += 1
                        frame_box = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
                        landmark = landmarks[i]
                        x1, y1, x2, y2 = landmark[:4].astype(int)
                        cv2.rectangle(frame_box, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        box = frame_box
                        flag = 1
                    if no_match == len(data_features):
                        matched_name = "没有找到这个人员。"
                        print(matched_name)
                if len(data_features) == 0:
                    print("没有找到这个人")
                    matched_name = "没有找到这个人员。"

                    

        if flag == 0:
            yield frame, matched_name
        else:
            yield box, matched_name

    cap.release()
    cv2.destroyAllWindows()
