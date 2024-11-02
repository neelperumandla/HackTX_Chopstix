import cv2


def get_contours(frame):
    frame_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    mask = cv2.inRange(frame_hsv, (20, 100, 100), (30, 255, 255))
    
    frame_threshold = mask
    
    frame_threshold = cv2.erode(frame_threshold, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)))
    frame_threshold = cv2.dilate(frame_threshold, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)))

    frame_threshold = cv2.dilate(frame_threshold, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)))
    frame_threshold = cv2.erode(frame_threshold, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)))

    contours, _ = cv2.findContours(frame_threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    return contours

def draw_rect(frame):
    contours = get_contours(frame)
  
    bounding_box = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        
        
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
    
    return frame

def main():
    
    cap = cv2.VideoCapture(0)
    
    
    while cap.isOpened():
        ret, frame = cap.read()
        
        cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0)
        cap.set(cv2.CAP_PROP_EXPOSURE, -4.7)
        
        #contours = get_contours(frame)
        frame = draw_rect(frame)
        
        #cv2.drawContours(frame, contours, -1, (255, 50, 255),1)
        cv2.imshow('frame', frame)
        
        
        if cv2.waitKey(2) == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()

main()
        
        
        
    