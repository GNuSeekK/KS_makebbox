# -*- coding: utf-8 -*-
"""
Created on Thu Sep 15 11:14:29 2022
v0.0.1 - 배포 시작

@author: user
"""
import cv2
import numpy as np
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
        thickness = int(img.shape[0] * img.shape[1] / 1000000 ) + 1
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