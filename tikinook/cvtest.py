# TODO: Write this using OpenCV
# Load animation/tiki-nook-pixel-out-v02.mov

import numpy
import cv2

vid = cv2.VideoCapture('animation/tiki-nook-pixel-out-v02-short-11x5.mov')

if (vid.isOpened()):
	print("Loaded video")
else:
	print("Load failed")

frameCount = int(vid.get(cv2.CAP_PROP_FRAME_COUNT))
fps = vid.get(cv2.CAP_PROP_FPS)
waitPerFrameInMilliseconds = int(1/fps*1000/1)

print("frameCount: " + str(frameCount))
print("fps: " + str(fps))

for frame in range(frameCount):
	# Grabbing values from the frame tuple
	# 'ret' is a boolean for whether there's a frame at this index
	ret, frameImg = vid.read()
	print("frame: " + str(frame))
	if(ret):
		# print("shape: " + str(frameImg.shape))
		for y in range(frameImg.shape[0]):
			for x in range(frameImg.shape[1]):
				print(x, y)
				print(frameImg[y, x])