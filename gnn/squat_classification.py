import cv2
import numpy as np
import tensorflow as tf
import tensorflow_hub as hub

# Load MoveNet Model
movenet = hub.load("https://tfhub.dev/google/movenet/singlepose/thunder/4")

def extract_keypoints(video_path):
    """Extracts keypoints from a video using MoveNet and returns timestamped keypoints."""
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30  # Frames per second
    frame_count = 0
    keypoints_list = []

    while True:
        ret, frame = cap.read()
        if not ret:
            break  

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_resized = cv2.resize(frame_rgb, (256, 256))
        frame_tensor = tf.convert_to_tensor(frame_resized, dtype=tf.int32)
        frame_tensor = tf.expand_dims(frame_tensor, axis=0)  

        # Run MoveNet inference
        outputs = movenet.signatures["serving_default"](input=frame_tensor)
        keypoints = outputs["output_0"].numpy().reshape(17, 3)[:, :2]  

        # Get the timestamp of the frame
        timestamp = frame_count / fps  
        keypoints_list.append((timestamp, keypoints))

        frame_count += 1  

    cap.release()
    return keypoints_list

def predict_squat(keypoints_list):
    """Predicts squat correctness with only significant changes logged."""
    results = []
    last_status = None  
    last_phase = None  

    for i in range(1, len(keypoints_list), 5):  # Reduce frequency of checking
        timestamp, keypoints = keypoints_list[i]
        prev_timestamp, prev_keypoints = keypoints_list[i - 1]

        left_knee = keypoints[13]
        right_knee = keypoints[14]
        hip = keypoints[11]
        left_ankle = keypoints[15]
        right_ankle = keypoints[16]
        torso = keypoints[5]  # Shoulder

        prev_hip = prev_keypoints[11]  # Previous frame hip position

        # **Detect Squat Phase (Descending or Ascending)**
        phase = "Descending" if hip[1] > prev_hip[1] else "Ascending"

        # **Classify Squat Correctness**
        squat_status = "Correct"
        issues = []

        # **Check Squat Depth (Hip Below Knees)**
        if hip[1] > left_knee[1] and hip[1] > right_knee[1]:
            squat_status = "Incorrect"
            issues.append("Squat too shallow")

        # **Check Knee Valgus (Knees Moving Inward)**
        if left_knee[0] > left_ankle[0] or right_knee[0] < right_ankle[0]:
            squat_status = "Incorrect"
            issues.append("Knees moving inward")

        # **Check Torso Leaning Forward**
        if torso[1] > hip[1]:
            squat_status = "Incorrect"
            issues.append("Leaning too forward")

        # **Store only if a major change occurs**
        explanation = ", ".join(issues) if issues else "Good form"
        if squat_status != last_status or phase != last_phase:
            results.append((timestamp, phase, squat_status, explanation))
            last_status = squat_status
            last_phase = phase  

    return results


# Process Video & Get Results
video_path = "test.mp4"
keypoints_list = extract_keypoints(video_path)
squat_results = predict_squat(keypoints_list)

# Save Results to a File
output_file = "squat_results.txt"
with open(output_file, "w") as f:
    f.write("Squat Classification Results\n")
    f.write("-----------------------------\n")
    for timestamp, phase, status, explanation in squat_results:
        f.write(f"Time: {timestamp:.2f}s | Phase: {phase} | Squat: {status} | Reason: {explanation}\n")

print(f"Squat classification results saved in {output_file}")
