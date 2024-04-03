import cv2
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pytesseract

image = cv2.imread(r'/home/bhavin/Pictures/Invoices Dataset/ARIHANT MARBLE2 (1).jpg', 0)
thresh, img_bin = cv2.threshold(image, 128, 255, cv2.THRESH_BINARY)
img_bin = 255 - img_bin
plotting = plt.imshow(img_bin, cmap='gray')
plt.title("Inverted Image with global thresh holding")
plt.show()

kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
print(kernel)

plt.figure(figsize=(30, 30))

vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, np.array(image).shape[1] // 100))
eroded_image = cv2.erode(img_bin, vertical_kernel, iterations=3)
plt.subplot(151), plt.imshow(eroded_image, cmap='gray')
plt.title('Image after erosion with vertical kernel'), plt.xticks([]), plt.yticks([])

vertical_lines = cv2.dilate(eroded_image, vertical_kernel, iterations=3)
plt.subplot(152), plt.imshow(vertical_lines, cmap='gray')
plt.title('Image after dilation with vertical kernel'), plt.xticks([]), plt.yticks([])

plt.show()

hor_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (np.array(image).shape[1] // 100, 1))
horizontal_lines = cv2.erode(img_bin, hor_kernel, iterations=5)
plt.subplot(153), plt.imshow(horizontal_lines, cmap='gray')
plt.title('Image after erosion with horizontal kernel'), plt.xticks([]), plt.yticks([])

horizontal_lines = cv2.dilate(horizontal_lines, hor_kernel, iterations=5)
plt.subplot(154), plt.imshow(horizontal_lines, cmap='gray')
plt.title('Image after dilation with horizontal kernel'), plt.xticks([]), plt.yticks([])

plt.show()

vertical_horizontal_lines = cv2.addWeighted(vertical_lines, 0.5, horizontal_lines, 0.5, 0.0)
vertical_horizontal_lines = cv2.erode(~vertical_horizontal_lines, kernel, iterations=3)
plt.subplot(151), plt.imshow(vertical_horizontal_lines, cmap='gray')
plt.title('Erosion'), plt.xticks([]), plt.yticks([])

thresh, vertical_horizontal_lines = cv2.threshold(vertical_horizontal_lines, 128, 255,
                                                  cv2.THRESH_BINARY)
plt.subplot(152), plt.imshow(vertical_horizontal_lines, cmap='gray')
plt.title('global and otsu thresholding'), plt.xticks([]), plt.yticks([])

bitxor = cv2.bitwise_xor(image, vertical_horizontal_lines)
plt.subplot(153), plt.imshow(bitxor, cmap='gray')
plt.title('Horizontal and vertical lines image bitxor'), plt.xticks([]), plt.yticks([])

bitnot = cv2.bitwise_not(bitxor)
plt.subplot(154), plt.imshow(bitnot, cmap='gray')
plt.title('Horizontal and vertical lines image with bitnot'), plt.xticks([]), plt.yticks([])

plt.show()

# gray_image = cv2.cvtColor(vertical_horizontal_lines, cv2.COLOR_BGR2GRAY)
# contours, hierarchy = cv2.findContours(gray_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
contours, hierarchy = cv2.findContours(vertical_horizontal_lines, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

boundingBoxes = [cv2.boundingRect(contour) for contour in contours]
(contours, boundingBoxes) = zip(*sorted(zip(contours, boundingBoxes), key=lambda x: x[1][1]))

boxes = []
for contour in contours:
    x, y, w, h = cv2.boundingRect(contour)
    if w < 1000 and h < 500:
        image = cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
        boxes.append([x, y, w, h])
plotting = plt.imshow(image, cmap='gray')
plt.title("Identified contours")
plt.show()

rows = []
columns = []
heights = [boundingBoxes[i][3] for i in range(len(boundingBoxes))]
mean = np.mean(heights)
print(mean)
columns.append(boxes[0])
previous = boxes[0]
for i in range(1, len(boxes)):
    if boxes[i][1] <= previous[1] + mean / 2:
        columns.append(boxes[i])
        previous = boxes[i]
        if i == len(boxes) - 1:
            rows.append(columns)
    else:
        rows.append(columns)
        columns = []
        previous = boxes[i]
        columns.append(boxes[i])
print("Rows")
for row in rows:
    print(row)

total_cells = 0
for i in range(len(row)):
    if len(row[i]) > total_cells:
        total_cells = len(row[i])
print(total_cells)

center = [int(rows[i][j][0] + rows[i][j][2] / 2) for j in range(len(rows[i])) if rows[0]]
print(center)

center = np.array(center)
center.sort()
print(center)

boxes_list = []
for i in range(len(rows)):
    l = []
    for k in range(total_cells):
        l.append([])
    for j in range(len(rows[i])):
        diff = abs(center - (rows[i][j][0] + rows[i][j][2] / 4))
        minimum = min(diff)
        indexing = list(diff).index(minimum)
        # print("Diff:", diff)
        # print("Minimum:", minimum)
        # print("Indexing:", indexing)
        l[indexing].append(rows[i][j])
    boxes_list.append(l)
for box in boxes_list:
    print(box)


dataframe_final = []
for i in range(len(boxes_list)):
    for j in range(len(boxes_list[i])):
        s = ''
        if len(boxes_list[i][j]) == 0:
            dataframe_final.append(' ')
        else:
            for k in range(len(boxes_list[i][j])):
                y, x, w, h = boxes_list[i][j][k][0], boxes_list[i][j][k][1], boxes_list[i][j][k][2], \
                    boxes_list[i][j][k][3]
                roi = bitnot[x:x + h, y:y + w]
                kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 1))
                border = cv2.copyMakeBorder(roi, 2, 2, 2, 2, cv2.BORDER_CONSTANT, value=[255, 255])
                resizing = cv2.resize(border, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
                dilation = cv2.dilate(resizing, kernel, iterations=1)
                erosion = cv2.erode(dilation, kernel, iterations=2)
                out = pytesseract.image_to_string(erosion)
                if len(out) == 0:
                    out = pytesseract.image_to_string(erosion)
                s = s + " " + out
            dataframe_final.append(s)
print(dataframe_final)

arr = np.array(dataframe_final)
print(arr)

dataframe = pd.DataFrame(arr.reshape(len(rows), total_cells))
data = dataframe.style.set_properties(align="left")
# print(data)
# print(dataframe)
d = []
for i in range(0, len(rows)):
    for j in range(0, total_cells):
        print(dataframe[i][j], end=" ")
    print()

print(dataframe)

dataframe.to_csv("output.csv")
