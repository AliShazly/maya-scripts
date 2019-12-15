#! /usr/bin/env python3

# Equirectangular projection
# https://stackoverflow.com/questions/51808714/try-using-equirectangular-projection-to-convert-2d-coordinates-to-3d-coordinates
# http://blog.nitishmutha.com/equirectangular/360degree/2017/06/12/How-to-project-Equirectangular-image-to-rectilinear-view.html

from __future__ import division

import math
from collections import deque
import numpy as np
import cv2


def get_bright_spots(mat, threshold=0.7, blur_radius=5):
    gray = cv2.cvtColor(mat, cv2.COLOR_BGR2GRAY)
    gauss = cv2.GaussianBlur(gray, (blur_radius,)*2 , 0)
    canvas = np.zeros_like(gray)
    for row, col in zip(*np.where(gauss > threshold)):
        canvas[row][col] = 1
    return canvas


def get_neighbors(idx):
    row, col = idx
    return [(row - 1, col),
            (row, col - 1),
            (row - 1, col - 1),
            (row + 1, col),
            (row, col + 1),
            (row + 1, col + 1),
            (row + 1, col - 1),
            (row - 1, col + 1)]


def cluster_pixels(mask, min_cluster_size=100):
    visited = np.zeros_like(mask)
    rows, cols = mask.shape
    queue = deque([])
    clusters = []
    for row in range(rows):
        for col in range(cols):

            # Starting the search if the pixel is part of the original mask, and not visited
            if mask[row][col] == 1 and visited[row][col] == 0:
                cluster_mask = np.zeros_like(mask) # Creating a seperate mask for each cluster
                visited[row][col] = 1
                queue.append((row, col))
                cluster_mask[row][col] = 1
            else:
                continue

            cluster_size = 0
            while queue:
                pixel_idx = queue.pop()
                neighbors = get_neighbors(pixel_idx)
                for idx in neighbors:
                    row_, col_ = idx
                    if mask[row_][col_] == 1 and visited[row_][col_] == 0:
                        visited[row_][col_] = 1
                        queue.append((row_, col_))
                        cluster_mask[row_][col_] = 1
                        cluster_size += 1

            if cluster_size > min_cluster_size:
                clusters.append(cluster_mask)

    return clusters


def get_rect_points(mask):
    points = cv2.findNonZero(mask)
    x1, y1, w, h = cv2.boundingRect(points)
    x2, y2 = ((x1 + w), y1)
    x3, y3 = (x1 + w, y1 + h)
    x4, y4 = (x1, (y1 + h))
    mid_x, mid_y = ((x1 + x3) // 2 , (y1 + y3) // 2)
    return (x1, y1), (x2, y2), (x3, y3), (x4, y4), (mid_x, mid_y)


def inverse_equirectangular(x, y, radius=5):
    lon = x / radius
    lat = y / radius
    lambda_ = math.atan(math.tan(lat))

    x = radius * math.cos(lambda_) * math.cos(lon) + 0 * math.cos(lat) * math.cos(lon)
    y = radius * math.cos(lambda_) * math.sin(lon) + 0 * math.cos(lat) * math.sin(lon)
    z = radius * math.sin(lambda_) + 0 * math.sin(lat)

    return x, y, z

hdr = cv2.imread("hdr2.hdr", -1)
mask = get_bright_spots(hdr)
clusters = cluster_pixels(mask)
for cluster in clusters:
    pt1, pt2, pt3, pt4, mid = get_rect_points(cluster)
    cv2.circle(cluster, pt1, 5, 255, -1) 
    cv2.circle(cluster, pt2, 5, 255, -1) 
    cv2.circle(cluster, pt3, 5, 255, -1) 
    cv2.circle(cluster, pt4, 5, 255, -1) 
    cv2.circle(cluster, mid, 5, 0, -1) 
    print(pt1, pt2, pt3, pt4, mid)
    cv2.imshow("mask", cluster)
    cv2.waitKey(0)
