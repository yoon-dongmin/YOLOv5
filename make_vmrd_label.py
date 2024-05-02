import os
import math
import xml.etree.ElementTree as ET

classes = ['box', 'banana', 'notebook', 'screwdriver', 'toothpaste', 'apple',
            'stapler', 'mobile phone', 'bottle', 'pen', 'mouse', 'umbrella',
            'remote controller', 'cans', 'tape', 'knife', 'wrench', 'cup', 'charger',
            'badminton', 'wallet', 'wrist developer', 'glasses', 'pliers', 'headset',
            'toothbrush', 'card', 'paper', 'towel', 'shaver', 'watch']

def od_convert(size, box):
    x_center = ((box[0] + box[1]) / 2.0) / size[0]
    y_center = ((box[2] + box[3]) / 2.0) / size[1]
    w = (box[1] - box[0]) / size[0]
    h = (box[3] - box[2]) / size[1]
    return x_center, y_center, w, h

def gd_convert(size, box):
    x_center = ((box[0] + box[2] + box[4] + box[6]) / 4.0) / size[0]
    y_center = ((box[1] + box[3] + box[5] + box[7]) / 4.0) / size[1]
    a = math.sqrt((box[2] - box[0]) ** 2 + (box[3] - box[1]) ** 2)
    b = math.sqrt((box[6] - box[0]) ** 2 + (box[7] - box[1]) ** 2)
    if a >= b:
        w = a
        h = b
        angle = math.atan2(box[3] - box[1], box[2] - box[0])
    else:
        w = b
        h = a
        angle = math.atan2(box[7] - box[1], box[6] - box[0])
    w = w / size[0]
    h = h / size[1]
    if angle < 0:
        angle += math.pi
    return x_center, y_center, w, h, angle

def convert_annotation(image_id):
    obj_in_file = open('VMRD/Annotations/%s.xml' % image_id)
    obj_out_file = open('VMRD/labels/od/%s.txt' % image_id, 'w')
    tree = ET.parse(obj_in_file)
    root = tree.getroot()
    size = root.find('size')
    w = int(size.find('width').text)
    h = int(size.find('height').text)
    dic = {}
    for obj in root.iter('object'):
        cls = obj.find('name').text
        g_ind = obj.find('index').text
        cls_id = classes.index(cls)
        dic[g_ind] = cls_id
        xmlbox = obj.find('bndbox')
        b = (float(xmlbox.find('xmin').text), float(xmlbox.find('xmax').text),
             float(xmlbox.find('ymin').text), float(xmlbox.find('ymax').text))
        bb = od_convert((w, h), b)
        obj_out_file.write(str(cls_id) + " " + " ".join([str(a) for a in bb]) + '\n')
    grasp_in_file = open('VMRD/Grasps/%s.txt' % image_id).readlines()
    grasp_out_file = open('VMRD/labels/gd/%s.txt' % image_id, 'w')
    for i in grasp_in_file:
        values = i.strip().split()
        x1, y1, x2, y2, x3, y3, x4, y4, ind = map(float, values[:9])
        cls_id = dic[str(int(ind))]
        b = (float(x1), float(y1), float(x2), float(y2), float(x3), float(y3), float(x4), float(y4))
        bb = gd_convert((w, h), b)
        grasp_out_file.write(str(cls_id) + " " + " ".join([str(a) for a in bb]) + '\n')

if __name__ == '__main__':
    # 현재 디렉토리 정보
    wd = os.getcwd()
    
    if not os.path.exists('VMRD/labels/od'):
        os.makedirs('VMRD/labels/od')
    if not os.path.exists('VMRD/labels/gd'):
        os.makedirs('VMRD/labels/gd')
        
    for image_set in ['trainval', 'test']:
        image_ids = open('VMRD/ImageSets/Main/%s.txt' % image_set).read().strip().split()
        list_file = open('VMRD/%s_list.txt' % image_set, 'w')
        for image_id in image_ids:
            list_file.write('%s/VMRD/JPEGImages/%s.jpg\n' %(wd, image_id))
            convert_annotation(image_id)
        list_file.close()
        
    with open('VMRD/vmrd_classes.txt', 'w', encoding='utf-8') as f:
        for cls in classes:
            f.write(cls + '\n')

        