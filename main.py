import cv2
import myframe
from service import Service
import time
# 定义变量

# 眼睛闭合判断
EYE_AR_THRESH = 0.15  # 眼睛长宽比
EYE_AR_CONSEC_FRAMES = 2  # 闪烁阈值

# 嘴巴开合判断
MAR_THRESH = 0.65  # 打哈欠长宽比
MOUTH_AR_CONSEC_FRAMES = 3  # 闪烁阈值

# 定义检测变量，并初始化
COUNTER = 0  # 眨眼帧计数器
TOTAL = 0  # 眨眼总数
mCOUNTER = 0  # 打哈欠帧计数器
mTOTAL = 0  # 打哈欠总数
ActionCOUNTER = 0  # 分心行为计数器器

# 疲劳判断变量
# Perclos模型
# perclos = (Rolleye/Roll) + (Rollmouth/Roll)*0.2
Roll = 0  # 整个循环内的帧技术
Rolleye = 0  # 循环内闭眼帧数
Rollmouth = 0  # 循环内打哈欠数

# 上次是啥
last_time = 0
LastAction = ''

enID = "oDRhudxKWJS09GLX0KX6If9uRcIH2TGTIbZ0PAsmPICuUA3f6hPbqIdrqbQKTy1nJYf0ZXZVoRtYdAnr5sMoe2DplIdIIvQgkI5JPtSvQyfiKetBYFobDgNfEvrn5WsZs1F29Gs151FKiViyTynvCbijfxLazmOR95RDY0oZ/ig="
api = Service(enID)

cap = cv2.VideoCapture(0)

while (1):
    success, frameSource = cap.read()
    frameSource = cv2.flip(frameSource, 1)  # 镜像操作
    if success:
        # 检测
        # 将摄像头读到的frame传入检测函数myframe.frametest()
        origen_frame = frameSource.copy()
        ret, frame = myframe.frametest(frameSource)
        lab, eye, mouth = ret
        # ret为检测结果，ret的格式为[lab,eye,mouth],lab为yolo的识别结果包含'phone' 'smoke' 'drink',eye为眼睛的开合程度（长宽比），mouth为嘴巴的开合程度
        # frame为标注了识别结果的帧画面，画上了标识框

        # 分心行为判断
        # 分心行为检测以15帧为一个循环
        ActionCOUNTER += 1

        # 如果检测到分心行为
        # 并加ActionCOUNTER减1，以延长循环时间
        if ActionCOUNTER > 0:
            for i in lab:
                if (i == "phone"):
                    if LastAction == 'phone' and time.time() - last_time < 5:
                        continue
                    print("正在用手机")
                    cv2.imwrite("phone.jpg", origen_frame)
                    last_time = time.time()
                    LastAction = 'phone'
                    api.newevent("phone", "phone.jpg")
                    ActionCOUNTER = -10
                elif (i == "smoke"):
                    if LastAction == 'smoke' and time.time() - last_time < 5:
                        continue
                    print("正在抽烟")
                    cv2.imwrite("smoke.jpg", origen_frame)
                    last_time = time.time()
                    LastAction = 'smoke'
                    api.newevent("smoke", "smoke.jpg")
                    ActionCOUNTER = -10
                elif (i == "drink"):
                    if LastAction == 'drink' and time.time() - last_time < 5:
                        continue
                    print("正在用喝水")
                    cv2.imwrite("drink.jpg", origen_frame)
                    last_time = time.time()
                    LastAction = 'drink'
                    api.newevent("drink", "drink.jpg")
                    ActionCOUNTER = -10

        # 如果超过15帧未检测到分心行为，将label修改为平时状态
        if ActionCOUNTER == 15:
            ActionCOUNTER = 0

        # 疲劳判断
        # 眨眼判断
        if eye < EYE_AR_THRESH:
            # 如果眼睛开合程度小于设定好的阈值
            # 则两个和眼睛相关的计数器加1
            COUNTER += 1
            Rolleye += 1
        else:
            # 如果连续2次都小于阈值，则表示进行了一次眨眼活动
            if COUNTER >= EYE_AR_CONSEC_FRAMES:
                TOTAL += 1
                print("眨眼次数：" + str(TOTAL))
                # 重置眼帧计数器
                COUNTER = 0

        # 哈欠判断，同上
        if mouth > MAR_THRESH:
            mCOUNTER += 1
            Rollmouth += 1
        else:
            # 如果连续3次都小于阈值，则表示打了一次哈欠
            if mCOUNTER >= MOUTH_AR_CONSEC_FRAMES:
                mTOTAL += 1
                print("哈欠次数：" + str(mTOTAL))
                # 重置嘴帧计数器
                mCOUNTER = 0

        # 将画面显示在前端UI上
        show = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        show = cv2.resize(frame, (640, 480))
        cv2.imshow("Video", show)

        # 疲劳模型
        # 疲劳模型以150帧为一个循环
        # 每一帧Roll加1
        Roll += 1
        # 当检测满150帧时，计算模型得分
        if Roll == 150:
            # 计算Perclos模型得分
            perclos = (Rolleye / Roll) + (Rollmouth / Roll) * 0.2
            # 在前端UI输出perclos值
            print("Perclos得分为：" + str(round(perclos, 3)))
            # 当过去的150帧中，Perclos模型得分超过0.38时，判断为疲劳状态
            if perclos > 0.5:
                print("当前处于疲劳状态")
                # 将疲劳状态的图片上传到云端
                cv2.imwrite("fatigue.jpg", origen_frame)
                api.newevent("fatigue", "fatigue.jpg")
            else:
                print("当前处于正常状态")

            # 归零
            # 将三个计数器归零
            # 重新开始新一轮的检测
            Roll = 0
            Rolleye = 0
            Rollmouth = 0
            print("\n")

    if (cv2.waitKey(1) & 0xFF) == ord('q'):
        break

cap.release()
