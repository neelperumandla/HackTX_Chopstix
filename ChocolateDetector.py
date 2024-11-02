import cv2
import numpy as np

def get_contours(frame):
    # Convert frame to HSV color space
    frame_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # Define color mask range for detecting Snickers Minis
    mask = cv2.inRange(frame_hsv, (10, 30, 140), (25, 140, 220))
    
    # Optional: Apply morphological operations to clean up the mask
    frame_threshold = cv2.erode(mask, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2)))
    frame_threshold = cv2.dilate(frame_threshold, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2)))
    
    contours, _ = cv2.findContours(frame_threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    return contours

def eligible(contours):
    # Filter out contours based on size
    colors = []
    max_area = 0
    
    # Find the maximum area among the contours
    for contour in contours:
        _, _, w, h = cv2.boundingRect(contour)
        area = w * h
        if area > max_area:
            max_area = area

    # Keep contours that are at least 50% of the max area
    for contour in contours:
        _, _, w, h = cv2.boundingRect(contour)
        if (w * h) > (max_area * 0.5):
            colors.append(contour)
    
    return colors

def calculate_center(bbox):
    x, y, w, h = bbox
    return (x + w // 2, y + h // 2)

def calculate_distance(center1, center2):
    return np.sqrt((center1[0] - center2[0])**2 + (center1[1] - center2[1])**2)

def find_closest_bbox(bboxes, reference_bbox):
    min_distance = float('inf')
    closest_bbox = None

    ref_center = calculate_center(reference_bbox)

    for bbox in bboxes:
        center = calculate_center(bbox)
        distance = calculate_distance(ref_center, center)

        if distance < min_distance:
            min_distance = distance
            closest_bbox = bbox

    return closest_bbox

def draw_rect(frame):
    # Detect contours
    contours = get_contours(frame)
    
    # Filter for eligible contours based on size
    bounding_box = eligible(contours)
    
    # Draw bounding rectangles on eligible contours
    for contour in bounding_box:
        x, y, w, h = cv2.boundingRect(contour)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
    
    return frame

def direction(frame):
    height, width, _ = frame.shape
    
    # Corrected center reference
    center = [width / 2, height / 2]
    contours = get_contours(frame)
    
    # Filter for eligible contours based on size
    bounding_box = eligible(contours)
    
    # Check if bounding_box has any elements before proceeding
    if not bounding_box:
        print("No eligible contours found.")
        return
    
    # Find the closest bounding box
    tgt = find_closest_bbox([cv2.boundingRect(contour) for contour in bounding_box], cv2.boundingRect(bounding_box[0]))
    
    # Ensure that tgt is not None
    if tgt:
        if tgt[0] > center[0]:
            print("Move Right")
        elif tgt[0] < center[0]:
            print("Move Left")
        if tgt[1] > center[1]:
            print("Move Up")
        elif tgt[1] < center[1]:
            print("Move Down")

def main():
    # Open video capture
    cap = cv2.VideoCapture(1)
    
    while cap.isOpened():
        ret, frame = cap.read()
        
        if not ret:
            break
        
        # Set camera exposure settings
        cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0)
        cap.set(cv2.CAP_PROP_EXPOSURE, -4.7)
        
        # Process frame and draw rectangles around detected Snickers Minis
        frame = draw_rect(frame)
        direction(frame)
        
        # Display the frame with rectangles
        cv2.imshow('Snickers Minis Detection', frame)
        
        # Exit if 'q' key is pressed
        if cv2.waitKey(2) == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()

# Run the main function
main()
