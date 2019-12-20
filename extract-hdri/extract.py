#! /usr/bin/env python3

# Equirectangular projection
# https://stackoverflow.com/questions/51808714/try-using-equirectangular-projection-to-convert-2d-coordinates-to-3d-coordinates
# http://blog.nitishmutha.com/equirectangular/360degree/2017/06/12/How-to-project-Equirectangular-image-to-rectilinear-view.html

# Set light target
# https://forums.chaosgroup.com/forum/v-ray-for-maya-forums/v-ray-for-maya-problems/1011428-set-rect-light-target-position-via-python

import math
from collections import deque
import json
import os

import numpy as np
import cv2


def get_bright_spots(mat, threshold=0.7, blur_radius=23):
    gray = cv2.cvtColor(mat, cv2.COLOR_BGR2GRAY)
    gauss = cv2.GaussianBlur(gray, (blur_radius,)*2 , 0)
    canvas = np.zeros_like(gray)
    for row, col in zip(*np.where(gauss > threshold)):
        canvas[row][col] = 1
    return canvas


def get_neighbors(idx, radius=1):
    row, col = idx
    neighbors = []
    for i in range(1, radius + 1):
        neighbors.append((row - i, col))
        neighbors.append((row, col - i))
        neighbors.append((row - i, col - i))
        neighbors.append((row + i, col))
        neighbors.append((row, col + i))
        neighbors.append((row + i, col + i))
        neighbors.append((row + i, col - i))
        neighbors.append((row - i, col + i))
    return neighbors


def cluster_pixels(mask, min_cluster_size=300, min_neighbor_dist=20):
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
                neighbors = get_neighbors(pixel_idx, radius=min_neighbor_dist)
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

    # Returning coords in row major order (numpy)
    return (y1, x1), (y2, x2), (y3, x3), (y4, x4), (mid_y, mid_x)


# If this doesn't work you can get the position on the sphere through it's UVs
def inverse_equirectangular(x, y, radius=5):
    lon = x / radius
    lat = y / radius
    lambda_ = math.atan(math.tan(lat))

    x = radius * math.cos(lambda_) * math.cos(lon) + 0 * math.cos(lat) * math.cos(lon)
    y = radius * math.cos(lambda_) * math.sin(lon) + 0 * math.cos(lat) * math.sin(lon)
    z = radius * math.sin(lambda_) + 0 * math.sin(lat)

    return x, y, z

# That ^^^ didn't work :(
def fit_to_uv(mat_size, points):
    old_rows, old_cols = mat_size
    new_rows, new_cols = (max(mat_size),) * 2
    ratio_rows = new_rows / old_rows
    ratio_cols = new_cols / old_cols
    ratio = (ratio_rows, ratio_cols)

    new_points = [[ratio[idx] * val for idx, val in enumerate(point)] for point in points]
    uv_normalized = [(row / new_rows, col / new_cols) for row, col in new_points]
    uv_ordered = [(col, 1 - row) for row, col in uv_normalized]
    return uv_ordered

def crop(image, bbox):
    tl, _, br, _ = bbox
    x1, y1 = tl
    x2, y2 = br
    return image[x1:x2, y1:y2]

def fill(image, bbox, value=0):
    tl, _, br, _ = bbox
    x1, y1 = tl
    x2, y2 = br
    image[x1:x2, y1:y2] = value

def main(hdr_path):
    hdr = cv2.imread(hdr_path, -1)
    mask = get_bright_spots(hdr)
    clusters = cluster_pixels(mask)
    data = {}
    for idx, cluster in enumerate(clusters):
        pt1, pt2, pt3, pt4, mid = get_rect_points(cluster)
        cropped = crop(hdr, [pt1, pt2, pt3, pt4])
        path = f"{os.getcwd()}\\rect_tex_{idx}.hdr"
        cv2.imwrite(path, cropped)

        data[str(idx)] = {
                "bbox_points": [pt1, pt2, pt3, pt4],
                "mid_point": mid,
                "rect_tex": path
                }

        fill(hdr, [pt1, pt2, pt3, pt4])

    path = f"{os.getcwd()}\\patched_hdr.hdr"
    cv2.imwrite(path, hdr)
    data["hdr"] = path

    with open("extract-hdri.json", "w+") as f:
        json.dump(data, f)

main()
