import machine
import time
from machine import I2C
from mpu6050 import MPU6050  # You'll need to install the 'mpu6050' library
from dht import DHT22
from machine import Pin

# Initialize DHT22
dht_sensor = DHT22(Pin(14))

TRIG = machine.Pin(10, machine.Pin.OUT)
ECHO = machine.Pin(11, machine.Pin.IN)
BUZZER = machine.Pin(12, machine.Pin.OUT)

# Initialize the I2C bus for the MPU6050 sensor
i2c = I2C(0, sda=machine.Pin(0), scl=machine.Pin(1))
mpu = MPU6050(i2c)


# Thresholds for fall detection
accel_threshold = 2.0  # Adjust this threshold based on your testing
gyro_threshold = 2.0  # Adjust this threshold based on your testing

def measure_distance():
    TRIG.value(0)
    time.sleep_us(2)
    TRIG.value(1)
    time.sleep_us(10)
    TRIG.value(0)

    while ECHO.value() == 0:
        pulse_start = time.ticks_us()

    while ECHO.value() == 1:
        pulse_end = time.ticks_us()

    pulse_duration = time.ticks_diff(pulse_end, pulse_start)
    distance = (pulse_duration / 2) / 29.1  # Calculate distance in cm

    return distance

def object_detection():
    # Add code here to capture an image using the camera and perform object detection
    # You'll need the 'picamera' library and an object detection model
    '''
    img = cv2.imread("image.jpg")
    height, width, channels = img.shape

    blob = cv2.dnn.blobFromImage(img, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
    net.setInput(blob)

    outs = net.forward(layer_names)

    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]

            if confidence > 0.5:
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)
                w = int(detection[2] * width)
                h = int(detection[3] * height)

                x = int(center_x - w / 2)
                y = int(center_y - h / 2)

                cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
                label = f"{classes[class_id]}: {confidence:.2f}"
                cv2.putText(img, label, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    cv2.imshow("Object Detection", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    '''


def fall_detection():

    accel_data = mpu.get_acc()
    gyro_data = mpu.get_gyro()

    # Calculate the magnitude of acceleration
    accel_magnitude = (accel_data[0] ** 2 + accel_data[0] ** 2 + accel_data[0] ** 2) ** 0.5

    # Calculate the magnitude of angular velocity (gyro)
    gyro_magnitude = (gyro_data[0] ** 2 + gyro_data[0] ** 2 + gyro_data[0] ** 2) ** 0.5

    print("Acceleration: ", accel_magnitude, ", angular velocity: ", gyro_magnitude)

    # Check for signs of a fall based on threshold values
    if accel_magnitude > accel_threshold and gyro_magnitude > gyro_threshold:
        print("Fall detected!")
        BUZZER.on()
        time.sleep(1)  # Buzz for 1 second
        BUZZER.off()

def humidity_based_detection():
    dht_sensor.measure()
    humidity = dht_sensor.humidity()
    print("Humidity: {:.2f}%".format(humidity))

    # Define a high humidity threshold
    high_humidity_threshold = 80  # Adjust this threshold based on your environment

    if humidity > high_humidity_threshold:
        print("High moisture level detected, possible puddle!")
        BUZZER.on()
        time.sleep(1)  # Buzz for 1 second
        BUZZER.off()

def main():
    while True:
        distance = measure_distance()
        print("Distance: {:.2f} cm".format(distance))

        fall_detection()
        humidity_based_detection()

        if distance < 50:
            # Perform object detection
            print("Obstacle Detected!")
            object_detection()

            # ADD GPS 

            # Trigger the buzzer to indicate a detected object or fall
            BUZZER.on()
            time.sleep(1)  # Buzz for 1 second
            BUZZER.off()

if __name__ == "__main__":
    main()
