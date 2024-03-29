
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 15 11:14:29 2022
v0.0.1 - 배포 시작
v0.0.2 - img_combine_polygon 추가
v0.0.3 - make_polygon 수정
v0.0.4 - get_thickness 추가, make_polygon 폴리곤 색칠에서 라인 그리기로 변경
v0.0.5 - make_polygon 폴리곤 색칠삭제
v0.0.6 - calc_IoU 추가, box_to_polygon 추가, polygon으로 모두 동작하게 함
v0.0.7 - box_to_polygon 수정 make_polygon fill 기능 추가
v0.0.8 - calc_IoU 오류 수정
v0.0.9 - calc_IoU zero division 오류 수정, calc_IoU => calc_iou로 변경
v0.1.0 - make_polygon 투명도 기능 추가
@author: user
"""
import cv2
import numpy as np
from typing import Union
import pandas
from shapely.geometry import Polygon

__version__ = 'v0.1.0'

def make_bbox(img: np.ndarray, x_list: list, y_list: list, color: tuple=(0, 0, 255), outline: bool=False, thickness=0):
    """_summary_

    Args:
        img (np.ndarray): cv2 이미지(numpy)
        x_list (list): x좌표값 리스트
        y_list (list): y좌표값 리스트
        color (tuple, optional): 색상. Defaults to (0, 0, 255).
        outline (bool, optional): 외각선. Defaults to False.
        thickness (int, optional): 두께. Defaults to 0. 0이면 자동 계산.

    Returns:
        np.ndarray: cv2 이미지
    """    
    x1, x2 = min(x_list), max(x_list)
    y1, y2 = min(y_list), max(y_list)
    if thickness == 0:
        thickness = get_thickness(img)
    if outline == True:
        img = cv2.rectangle(img, (x1, y1), (x2, y2), (0,0,0), thickness = int(thickness * 1.5) + 1)
    img = cv2.rectangle(img, (x1, y1), (x2, y2), color, thickness = thickness)
    return img

def make_point(img: np.ndarray, x: int, y: int, color: tuple=(0, 0, 255), outline: bool=True, thickness: int=5):
    """_summary_

    Args:
        img (np.ndarray): cv2 이미지(numpy)
        x (int): x좌표값
        y (int): y좌표값
        color (tuple, optional): 색상. Defaults to (0, 0, 255).
        outline (bool, optional): 외각선. Defaults to True.
        thickness (int, optional): 두께. Defaults to 5.

    Returns:
        np.ndarray: cv2 이미지
    """    
    if outline == True:
        img = cv2.line(img, (x, y), (x,  y), color=(0, 0, 0), thickness = thickness + 2)
    img = cv2.line(img, (x, y), (x,  y), color=color, thickness = thickness)
    return img

def make_polygon(
        img: np.ndarray, 
        polygon: Union[list, np.ndarray], 
        color: tuple=(0,0,255),
        fill: bool=False,
        fill_color: tuple=(0,0,0),
        thickness: int=0,
        shade: bool=False,
        opacity: float=0.5
    ):
    """_summary_

    Args:
        img (np.ndarray): cv2 이미지(numpy)
        polygon (Union[list, np.ndarray]): 폴리곤 값이 담긴 리스트
        color (tuple, optional): 색상. Defaults to (0, 0, 255).
        thickness (int, optional): 폴리곤의 두께
    Returns:
        np.ndarray: cv2 이미지
    """
    if thickness == 0:
        thickness = get_thickness(img)
    if type(polygon) != np.ndarray:
        try:
            iter(polygon[0])
            if type(polygon[0]) == str:
                polygon = list(map(lambda x: int(round(float(x), 0)), polygon))
            else:
                new_polygon = []
                for x, y in polygon:
                    x = int(round(float(x), 0))
                    y = int(round(float(y), 0))
                    new_polygon.append(x)
                    new_polygon.append(y)
                polygon = new_polygon
            polygon = np.array(polygon).reshape(len(polygon)//2, 2)
        except:
            # print(polygon)
            # 박스 좌표값이 들어온 경우
            if len(polygon) == 4:
                polygon = box_to_polygon(polygon)
            else: # 폴리곤 좌표값이 들어온 경우
                polygon = list(map(int, polygon))
                polygon = np.array(polygon).reshape(len(polygon)//2, 2)
    if fill and shade:
        add_img = img.copy()
        add_img = cv2.fillPoly(add_img, [polygon], color=fill_color)
        img = cv2.addWeighted(img, 1 - opacity, add_img, opacity, 0)
    elif fill:
        img = cv2.fillPoly(img, [polygon], color=fill_color)
    img = cv2.polylines(img, [polygon], isClosed=True, color=color, thickness=thickness)
        
    return img

def img_combine_polygon(ori_img: np.ndarray, comb_img: np.ndarray, polygon_list: list):
    """
    ori_img에 combine_img의 polygon 값을 복사한다.

    Args:
        ori_img (np.array): 원본 이미지
        comb_img (np.array): 병합 이미지
        polygon_list (list): np.ndarray로 이루어진 폴리곤 list

    Returns:
        _type_: np.array
    """    
    mask = np.zeros(comb_img.shape)
    mask = cv2.fillPoly(mask, polygon_list, (255, 255, 255))
    index_arr = np.where(mask == 255)
    ori_img[index_arr] = comb_img[index_arr]
    return ori_img

def get_thickness(img: np.ndarray):
    return int(img.shape[0] * img.shape[1] / 1000000 ) + 1

# calculating IoU of two polygons
def calc_iou(polygon1: list, polygon2: list):
    """
    두 폴리곤의 IoU를 계산한다.

    Args:
        polygon1 (list): 폴리곤1
        polygon2 (list): 폴리곤2

    Returns:
        _type_: float
    """    
    polygon1 = Polygon(polygon1)
    polygon2 = Polygon(polygon2)
    intersection = polygon1.intersection(polygon2)
    union = polygon1.union(polygon2)
    # error handling
    if intersection.is_empty:
        return 0.0
    else:
        return intersection.area / union.area
    

def box_to_polygon(box: list):
    """
    box를 폴리곤으로 변환한다.

    Args:
        box (list): [x1, y1, x2, y2]

    Returns:
        _type_: list
    """    
    x1, y1, x2, y2 = box
    return np.array([[x1, y1], [x2, y1], [x2, y2], [x1, y2]])



# def rotate_shape(ori_img):
#     gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#     thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

#     # Find contours, find rotated rectangle, obtain four verticies, and draw 
#     cnts = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
#     cnts = cnts[0] if len(cnts) == 2 else cnts[1]
#     rect = cv2.minAreaRect(cnts[0])
#     boxes = []
#     for idx in range(len(json_data['object']['object_2D'])//5):
#         datas = [
#             json_data['object']['object_2D'][idx*5],
#             json_data['object']['object_2D'][idx*5+1],
#             json_data['object']['object_2D'][idx*5+2],
#             json_data['object']['object_2D'][idx*5+3],
#             json_data['object']['object_2D'][idx*5+4],
#         ]
#         x, y, dx, dy = map(lambda x: int(round(x, 0)), datas[:4])
#         rot = datas[4]
#         box = np.int0(cv2.boxPoints([(x, y), (dx, dy), rot]))
#         # box = np.int0(cv2.boxPoints([(x + dx//2, y + dy//2), (dx, dy), rot]))
#         boxes.append(box)
        
#     img = cv2.polylines(img, boxes, True, (255, 0, 0), 3)