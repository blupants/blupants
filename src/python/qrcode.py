import cv2
import time

max_tries = 100
index = 0
apiPreference = cv2.CAP_ANY

qr_decoder = cv2.QRCodeDetector()
cap = cv2.VideoCapture(index, apiPreference)
print("VideoCapture(index={}, apiPreference={})".format(index, apiPreference))
time.sleep(1)

# Check if camera opened successfully
if cap.isOpened():
    cap.set(cv2.CAP_PROP_FPS, 30)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
    time.sleep(1)
else:
    print("Error opening video stream or file")

count = 0
# Read until video is completed
while cap.isOpened():
    time.sleep(0.25)
    # Capture frame-by-frame
    ret, frame = cap.read()
    print(count)
    if ret:
        data, bbox, rectified_image = qr_decoder.detectAndDecode(frame)
        # cv2.imwrite("/root/capture/{}.png".format(str(count).zfill(4)), frame)
        if len(data) > 0:
            print("Decoded Data : {}".format(data))
            break
        else:
            print("QR Code not detected")
    count += 1
    if count >= max_tries:
        break
cap.release()
print("Done!")
