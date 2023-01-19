import cv2 
import numpy as np 
'''
This is the code that performs single object tracking in two-dimensional surfaces used by the animal tracking interface.
The largest moving object on either a live or pre-recorded video is the one 
whose x and y positions will be stored on an external txt file.
'''

def capture(kind,camera,file_name,number1,number2):
	'''
	General function to capture and track the object's movement.

	:param kind: kind of video feed, either live or pre-recorded
	:param camera: non-negative integer code assigned to the camera
	:param file_name: name of the file where the object's coordinates will be stored
	:param number1: largest dimension, either height or width, of the object seen from the camera's angle
	:param number2: remaining dimension, either height or width, of the object seen from the camera's angle
	'''
	if kind == 'live':
		cap = cv2.VideoCapture(camera)
	elif kind == 'rec':
		cap = cv2.VideoCapture(str(camera))
	height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
	width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
	fps = cap.get(cv2.CAP_PROP_FPS)
	
	save = cv2.VideoWriter(str(file_name)+'.mp4',cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height), isColor=True)
	back_sub = cv2.createBackgroundSubtractorKNN()
	kernel = np.ones((30,30),np.uint8)
	file = open(str(file_name)+'.txt','w') 
	n_frames = 0
	while(True):
		n_frames += 1
		ret, frame = cap.read()
		if not ret:
			break

		
		fg_mask = back_sub.apply(frame) 

		fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, kernel) 

		fg_mask = cv2.medianBlur(fg_mask, 5)  

		_, fg_mask = cv2.threshold(fg_mask,127,255,cv2.THRESH_BINARY) 

		fg_mask_bb = fg_mask 
		contours, hierarchy = cv2.findContours(fg_mask_bb,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)[-2:] 
		areas = [cv2.contourArea(c) for c in contours] 


		if len(areas) < 1:

			continue

		else:

			max_index = np.argmax(areas)

		cnt = contours[max_index]
		x,y,w,h = cv2.boundingRect(cnt)
		cv2.rectangle(frame,(x,y),(x+w,y+h),(0,0,255),3)

		if w > h:
			px_per_cm = w/float(number1)
		elif w < h:
			px_per_cm = h/float(number1)

		x2 = x + int(w/2)
		y2 = y + int(h/2)
		file.write(str(np.round(n_frames/fps,2))+','+str(np.round(x2/px_per_cm,1))+','+str(np.round(y2/px_per_cm,1))+'\n') 			
		
		cv2.circle(frame,(x2,y2),4,(0,255,0),-1)

		text = "x: " + str(np.round(x2/px_per_cm,1)) + ", y: " + str(np.round(y2/px_per_cm,1)) 
		cv2.putText(frame, text, (x2, y2), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0 ,255), 2)		
		
		fps_text = 'Tempo = ' + str(np.round(n_frames/fps,2))
		cv2.putText(frame,fps_text,(120,80),cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,255), 2)

		stop_text = 'Press "q" to stop tracking'
		cv2.putText(frame,stop_text,(120,120),cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,255), 2)

		save.write(frame)
		cv2.line(frame,(0,0),(511,0),(255,0,0),5)
		cv2.line(frame,(0,0),(0,511),(255,0,0),5)
		cv2.imshow('frame',frame)
		if cv2.waitKey(1) & 0xFF == ord('q'):
			break

	cap.release()
	cv2.destroyAllWindows()
	file.close()
	save.release()
	
if __name__ == '__main__':
    capture()