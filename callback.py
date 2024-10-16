import pika
import json
import time
import uiautomator2
import subprocess
import requests
import os

FILE_PATH = 'devices.txt'

# Function to read device list from file
def read_devices():
    try:
        with open(FILE_PATH, 'r') as file:
            lines = file.readlines()
            if not lines:
                return None
            else:
                # Convert lines into a list and remove any whitespace/newline characters
                table_data = [line.strip() for line in lines]
                return table_data
    except FileNotFoundError:
        return None

# Function to process the ADB task and send a webhook on completion
def process_adb_task(task_data):
    try:
        username = task_data['username']
        device = task_data['device']
        token = task_data['token']
        pin = task_data['pin']
        timeout = task_data['timeout']
        webhook_url = task_data.get('webhook_url', None)

        start_sys = False
        devices = read_devices()
        if devices:
            for devicex in devices:
                if username == devicex:
                    start_sys = True
                    break
        if not start_sys:
            return

        # Start the timer to track task execution time
        start_time = time.time()
        link = f"https://kpaymentgateway-services.kasikornbank.com/KPGW-Redirect-Webapi/Appswitch/{token}"
        
        # Connect to the device via uiautomator2
        adb = uiautomator2.connect(device)

        # Ensure the screen is on and unlocked
        if adb.info['currentPackageName'] == "com.android.systemui":
            adb.screen_on()
            run_adb_command("input keyevent KEYCODE_WAKEUP")
            run_adb_command("input swipe 300 1000 300 500")  # Swipe to unlock
        
        # Stop the app if it's running and open the new URL
        package = 'com.kasikorn.retail.mbanking.wap'
        adb.app_stop(package)
        adb.open_url(link)

        # Check for invalid token or timeout
        while True:
            if time.time() - start_time >= timeout:
                adb.app_stop(package)
                result = {"status": False, "msg": "time_out"}
                print(result)
                send_webhook_notification(webhook_url, result)
                return  # Timeout condition
            
            try:
                if adb(text="ขออภัย").get_text(timeout=0.1):  # Invalid token check
                    adb.app_stop(package)
                    result = {"status": False, "msg": f"check token: {token}"}
                    print(result)
                    send_webhook_notification(webhook_url, result)
                    return  # Invalid token response
            except:
                pass

            try:
                if adb(text="กรุณาใส่รหัสผ่าน").get_text(timeout=0.1):  # Detect the PIN input screen
                    break
            except:
                pass

        time.sleep(1)
        # Enter the PIN
        for p in pin:
            adb(resourceId=f"com.kasikorn.retail.mbanking.wap:id/linear_layout_button_activity_{p}").click()
            time.sleep(0.5)

        # Extract transaction information and confirm the transaction
        data_json = {}
        while True:
            if time.time() - start_time >= timeout:
                adb.app_stop(package)
                result = {"status": False, "msg": "time_out"}
                print(result)
                send_webhook_notification(webhook_url, result)
                return
            
            try:
                adb(text="ยืนยันรายการ").get_text(timeout=0.1)  # Confirm screen detection
                data_info = adb(className="android.widget.TextView")
                data_json = {
                    "from": data_info[-5].get_text(),
                    "to": data_info[-4].get_text(),
                    "amount": data_info[-3].get_text(),
                    "fee": data_info[-2].get_text(),
                    "number": data_info[-1].get_text(),
                }
                break
            except:
                pass

        # Confirm the transaction
        while True:
            try:
                adb(text="ยืนยัน").click(timeout=0.5)
            except:
                pass
            try:
                adb(text="ดำเนินการเสร็จสิ้น").get_text(timeout=0.1)  # Transaction completion detection
                adb.app_stop(package)
                result = {"status": True, "msg": data_json}
                print(result)
                send_webhook_notification(webhook_url, result)
                return
            except:
                pass

    except Exception as e:
        result = {"status": False, "msg": f"error: {e}"}
        print(result)
        send_webhook_notification(webhook_url, result)

# Function to run an ADB command
def run_adb_command(cmd):
    result = subprocess.run(f"adb shell {cmd}", shell=True, capture_output=True, text=True)
    print(result.stdout)
    print(result.stderr)

# Function to send a webhook notification
def send_webhook_notification(webhook_url, data):
    if webhook_url:
        try:
            response = requests.post(webhook_url, json=data)
            if response.status_code == 200:
                print(f"Webhook sent successfully: {data}")
            else:
                print(f"Failed to send webhook: {response.status_code}, {response.text}")
        except Exception as e:
            print(f"Error sending webhook: {e}")
    else:
        print("No webhook URL provided, skipping notification.")

# Callback function to process messages from the queue
def callback(ch, method, properties, body):
    task_data = json.loads(body)
    print(f" [x] Received task: {task_data}")
    process_adb_task(task_data)
    
    # Acknowledge the message
    ch.basic_ack(delivery_tag=method.delivery_tag)

# Set up connection to RabbitMQ
credentials = pika.PlainCredentials('user', 'password')  # Update with RabbitMQ credentials
connection = pika.BlockingConnection(pika.ConnectionParameters(
    host='206.189.81.158',  # Update with your RabbitMQ server address
    port=5672,
    virtual_host='/',
    credentials=credentials
))

channel = connection.channel()

# Declare the queue to ensure it exists
channel.queue_declare(queue='adb_task_queue')

# Set up the consumer
channel.basic_consume(queue='adb_task_queue', on_message_callback=callback)

print(' [*] Waiting for messages. To exit press CTRL+C')

# Start consuming messages
channel.start_consuming()
