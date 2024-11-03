import cv2
import numpy as np
import detect_open_mouth as mouth
import Communicator as comm


def get_contours(frame):
    # Convert frame to HSV color space
    frame_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # Define color mask range for detecting Snickers Minis
    mask = cv2.inRange(frame_hsv, (6, 63, 0), (23, 225, 81))
    
    # Optional: Apply morphological operations to clean up the mask
    frame_threshold = cv2.erode(mask, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2)))
    frame_threshold = cv2.dilate(frame_threshold, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2)))
    
    contours, _ = cv2.findContours(frame_threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    return contours

def get_stix_contours(frame):
    frame_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    mask1 = cv2.inRange(frame_hsv, (0, 70, 50), (10, 255, 255)) # red lower
    mask2 = cv2.inRange(frame_hsv, (170, 70, 50), (180, 255, 255)) # red upper
    frame_threshold = mask1 | mask2
    
    frame_threshold = cv2.erode(frame_threshold, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2)))
    frame_threshold = cv2.dilate(frame_threshold, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2)))

    frame_threshold = cv2.dilate(frame_threshold, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2)))
    frame_threshold = cv2.erode(frame_threshold, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2)))

    
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
    
    contours = get_stix_contours(frame)
    bounding_box = eligible(contours)
    
    # Draw bounding rectangles on eligible contours
    for contour in bounding_box:
        x, y, w, h = cv2.boundingRect(contour)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
    
    
    return frame

def get_target(frame):
    chocolate_contours = get_contours(frame)
    eligible_chocolates = eligible(chocolate_contours)
    tgt = find_closest_bbox([cv2.boundingRect(contour) for contour in eligible_chocolates],
                            cv2.boundingRect(eligible_chocolates[0]))
    
    return calculate_center(tgt)

def position_stix(frame):
    
    while has_target(frame):
        # Detect and filter chocolate contours
        chocolate_contours = get_contours(frame)
        eligible_chocolates = eligible(chocolate_contours)
        
        if not eligible_chocolates:
            print("No chocolate detected.")
            return
        
        # Find closest chocolate contour to the first one in the list
        tgt = find_closest_bbox([cv2.boundingRect(contour) for contour in eligible_chocolates],
                                cv2.boundingRect(eligible_chocolates[0]))

        if tgt is None:
            print("No valid chocolate target found.")
            return

        # Detect chopstick contours and ensure there are at least two
        chopstick_contours = get_stix_contours(frame)
        if len(chopstick_contours) < 2:
            print("Not enough chopstick contours detected.")
            return

        # Calculate centers of the two chopstick contours
        left_center = calculate_center(cv2.boundingRect(chopstick_contours[0]))
        right_center = calculate_center(cv2.boundingRect(chopstick_contours[1]))

        # Calculate midpoint between chopsticks
        current_aim = ((left_center[0] + right_center[0]) / 2, (left_center[1] + right_center[1]) / 2)

        # Set a buffer threshold for alignment tolerance
        buffer = 10

        # Adjust position based on chocolate target relative to chopstick midpoint
        tgt_center = calculate_center(tgt)
        if tgt_center[0] < (current_aim[0] - buffer):
            print("Move Right")
        elif tgt_center[0] > (current_aim[0] + buffer):
            print("Move Left")

        if tgt_center[1] < (current_aim[1] - buffer):
            print("Move Down")
        elif tgt_center[1] > (current_aim[1] + buffer):
            print("Move Up")
        

def has_target(frame):
    if(len(eligible(get_contours(frame))) > 0):
        return True
    else:
        return False
        


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
            
def put_in_mouth(frame):
    tgt = get_target(frame)
    center = mouth.center_mouth(mouth)
    
    buffer = 10
    
    while has_target(frame):
        while tgt[0] < (center[0] - buffer):
            print("Move Right")
        while tgt[0] > (center[0] + buffer):
            print("Move Left")

        while tgt[1] < (center[1] - buffer):
            print("Move Down")
        while tgt[1] > (center[1] + buffer):
            print("Move Up")

def main():
    # Open video capture
    cap = cv2.VideoCapture(0)
    
    while cap.isOpened():
        ret, frame = cap.read()
        
        if not ret:
            break
        
        # Set camera exposure settings
        cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0)
        cap.set(cv2.CAP_PROP_EXPOSURE, -4.7)
        
        # Process frame and draw rectangles around detected Snickers Minis
        frame = draw_rect(frame)
        
        position_stix(frame)
        comm.toggleSticks()
        
        # put_in_mouth(frame)
        # comm.toggleSticks
        
        # Display the frame with rectangles
        cv2.imshow('Snickers Minis Detection', frame)
        
        # Exit if 'q' key is pressed
        if cv2.waitKey(2) == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()

# Run the main function
main()
