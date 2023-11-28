import cv2
import pyautogui
import numpy as np
import keyboard
import sys ,os

print("Here look!\nplay bot: ctrl & a\nstop bot: ctrl & s\nend bot: ctrl & x\n30 bullets: ctrl & q\n10 bullets: ctrl & w\nwait time(30ms): ctrl & e\nwait time(70ms): ctrl & r\nwait time(100ms): ctrl & t\n")
  
screen_width, screen_height = pyautogui.size()
scx= screen_width/2
scy= screen_height/2
hsz=160
input_size = 320
confThreshold =0.2
nmsThreshold =0.2
font_color = (0, 0, 255)
font_size = 0.5
font_thickness = 2
colors = (0, 255, 0)
# Middle cross line position
middle_line_position = 225   
up_line_position = middle_line_position - 15
down_line_position = middle_line_position + 15
required_class_index = [0]
max_bullet=30
bullet=max_bullet
wait_time=70

def resource_path(relative_path):
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_path, relative_path)
modelConfiguration = resource_path('F:\\me\\projects\\python\\yolo3-weight\\yolov3-320.cfg')
modelWeigheights = resource_path('F:\me\\projects\\python\\yolo3-weight\\yolov3-320.weights')


net = cv2.dnn.readNetFromDarknet(modelConfiguration, modelWeigheights)
# Configure the network backend
net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA) #----------gpu--------
net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA) #------------gpu---------
# Function for finding the center of a rectangle
def find_center(x, y, w, h):
    x1=int(w/2)
    y1=int(h/2)
    cx = x+x1
    cy=y+y1
    return cx, cy    

temp_up_list = []
temp_down_list = []
up_list = [0, 0, 0, 0]
down_list = [0, 0, 0, 0]
def count_vehicle(box_id, img):
    x, y, w, h, id, index = box_id
    center = find_center(x, y, w, h)
    ix, iy = center    
    if (iy > up_line_position) and (iy < middle_line_position):
        if id not in temp_up_list:
            temp_up_list.append(id)
    elif iy < down_line_position and iy > middle_line_position:
        if id not in temp_down_list:
            temp_down_list.append(id)            
    elif iy < up_line_position:
        if id in temp_down_list:
            temp_down_list.remove(id)
            up_list[index] = up_list[index]+1
    elif iy > down_line_position:
        if id in temp_up_list:
            temp_up_list.remove(id)
            down_list[index] = down_list[index] + 1
            
def postProcess(outputs,img):
    global bullet
    height, width = img.shape[:2]
    boxes = []
    classIds = []
    confidence_scores = []
    detection = []
    for output in outputs:
        for det in output:
            scores = det[5:]
            classId = np.argmax(scores)
            confidence = scores[classId]
            if classId in required_class_index:
                if confidence > confThreshold:
                    w,h = int(det[2]*width) , int(det[3]*height)
                    x,y = int((det[0]*width)-w/2) , int((det[1]*height)-h/2)
                    boxes.append([x,y,w,h])
                    classIds.append(classId)
                    confidence_scores.append(float(confidence))
    # Apply Non-Max Suppression
    indices = cv2.dnn.NMSBoxes(boxes, confidence_scores, confThreshold, nmsThreshold)
    if len(indices)>0:
        for i in indices.flatten():
            x, y, w, h = boxes[i][0], boxes[i][1], boxes[i][2], boxes[i][3]
            # Draw bounding rectangle
            x=scx-hsz+x
            y=scy-hsz+y
            # cv2.rectangle(img, (x, y), (x + w, y + h), colors, 1)
            detection.append([x, y, w, h, required_class_index.index(classIds[i])])
            cx,cy=find_center(x, y, w, h)
            pyautogui.click(cx,y+h/8.0)
            bullet-=1
            if bullet<=0:
                bullet=max_bullet
                pyautogui.press('r')
playing=0
def on_key_press(event):
    global playing, max_bullet, wait_time
    if event.name == ('ctrl' and 'a'):
        playing=1
        print("begin the game...")
    elif event.name == ('ctrl' and 's'):
        playing=0
        print("stop game...")
    elif event.name == ('ctrl' and 'x'):
        playing=-1
        print("Exiting the program...")
    elif event.name == ('ctrl' and 'q'):
        max_bullet=30
    elif event.name == ('ctrl' and 'w'):
        max_bullet=10
    elif event.name == ('ctrl' and 'e'):
        wait_time=30
    elif event.name == ('ctrl' and 'r'):
        wait_time=70
    elif event.name == ('ctrl' and 't'):
        wait_time=100
keyboard.on_press(on_key_press)
while playing!=-1:
    if playing==1:
        src = pyautogui.screenshot(region=(scx-hsz,scy-hsz,2*hsz,2*hsz))
        img = np.array(src)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        blob = cv2.dnn.blobFromImage(img, 1 / 255, (input_size, input_size), [0, 0, 0], 1, crop=False)
        net.setInput(blob)
        layersNames = net.getLayerNames()
        outputNames = [(layersNames[i - 1]) for i in net.getUnconnectedOutLayers()]
        outputs = net.forward(outputNames)
        postProcess(outputs,img)
    cv2.waitKey(wait_time)
    