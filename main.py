import cv2
import mediapipe as mp
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import math
import time

# Initialize MediaPipe Hands for hand gesture recognition
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_drawing = mp.solutions.drawing_utils

# Access the system's audio device for volume control
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, 0, None)
volume = interface.QueryInterface(IAudioEndpointVolume)

# Set up camera 1 (change from default camera)
cap = cv2.VideoCapture(1)  # Use camera 1

# Variable to handle mute/unmute logic
last_fist_time = 0
is_muted = False
fist_closed = False

def is_fist(hand_landmarks):
    """Detects if the hand is a fist by checking the proximity of fingertips to palm."""
    for i in range(1, 5):  # Check the distances between the tips and base of the fingers
        finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark(i + 3)]
        finger_base = hand_landmarks.landmark[mp_hands.HandLandmark(i)]
        
        # If the finger tip is very close to the palm, it's likely a fist
        if math.sqrt((finger_tip.x - finger_base.x) ** 2 + (finger_tip.y - finger_base.y) ** 2) > 0.04:
            return False
    return True

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()

    if not ret:
        break

    # Flip the image horizontally for a later selfie-view display
    frame = cv2.flip(frame, 1)

    # Convert the BGR image to RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Process the frame and get hand landmarks
    results = hands.process(rgb_frame)

    if results.multi_hand_landmarks:
        if len(results.multi_hand_landmarks) == 1:
            hand_landmarks = results.multi_hand_landmarks[0]

            # Draw hand landmarks
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Check for fist gesture
            if is_fist(hand_landmarks):
                current_time = time.time()

                # If fist is detected for the first time, toggle mute/unmute
                if not fist_closed:
                    if is_muted:
                        # Unmute and set volume to 15%
                        volume.SetMute(0, None)  # Unmute
                        volume.SetMasterVolumeLevelScalar(0.15, None)  # Set volume to 15%
                        print("Unmuted and set volume to 15%")
                    else:
                        # Mute the volume
                        volume.SetMute(1, None)  # Mute
                        print("Muted")
                    is_muted = not is_muted
                    fist_closed = True  # Mark that fist has been closed
                    last_fist_time = current_time

            else:
                # If the hand is not in a fist, reset the fist_closed flag
                fist_closed = False

        # If two hands are detected, control volume based on wrist distance
        if len(results.multi_hand_landmarks) == 2:
            hand1_landmarks = results.multi_hand_landmarks[0]
            hand2_landmarks = results.multi_hand_landmarks[1]

            wrist1 = hand1_landmarks.landmark[mp_hands.HandLandmark.WRIST]
            wrist2 = hand2_landmarks.landmark[mp_hands.HandLandmark.WRIST]

            # Calculate the distance between the two wrists
            distance = math.sqrt((wrist2.x - wrist1.x)**2 + (wrist2.y - wrist1.y)**2)

            # Map this distance to a volume level
            min_distance = 0.1  # Minimum distance for volume change
            max_distance = 0.4  # Maximum distance for volume change

            if distance < min_distance:
                new_volume = 0.0  # Minimum volume
            elif distance > max_distance:
                new_volume = 1.0  # Maximum volume
            else:
                # Normalize the volume level based on distance
                new_volume = (distance - min_distance) / (max_distance - min_distance)

            # Set the system volume
            volume.SetMasterVolumeLevelScalar(new_volume, None)

    # Display the resulting frame
    cv2.imshow("Hand Gesture Volume Control", frame)

    # Break the loop if the user presses the 'q' key
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the capture and close OpenCV windows
cap.release()
cv2.destroyAllWindows()
