import aioble
import bluetooth
import asyncio
import struct
from sys import exit

# Define UUIDs for the service and characteristic
_SERVICE_UUID = bluetooth.UUID(0x1848)
_CHARACTERISTIC_UUID = bluetooth.UUID(0x2A6E)

# IAM = "Central" # Change to 'Peripheral' or 'Central'
IAM = "Peripheral"

if IAM not in ['Peripheral','Central']:
    print(f"IAM must be either Peripheral or Central")
    exit()

if IAM == "Central":
    IAM_SENDING_TO = "Peripheral"
else:
    IAM_SENDING_TO = "Central"

MESSAGE = f"Hello from {IAM}!"

# Bluetooth parameters
ble_name = f"{IAM}"  # You can dynamically change this if you want unique names
ble_svc_uuid = bluetooth.UUID(0x181A)
ble_characteristic_uuid = bluetooth.UUID(0x2A6E)
ble_appearance = 0x0300
ble_advertising_interval = 2000
ble_scan_length = 5000
ble_interval = 30000
ble_window = 30000

# state variables
message_count = 0
connected = False

def encode_message(message):
    return message.encode('utf-8')

def decode_message(message):
    return message.decode('utf-8')

async def send_data_task(connection, characteristic):
    global message_count
    while True:
        if not connection:
            print("error - no connection in send data")
            continue
        
        if not characteristic:
            print("error no characteristic provided in send data")
            continue
        
        message = f"{MESSAGE} {message_count}"
        message_count +=1
        print(f"sending {message}")
        
        try:
            response = characteristic.read()
            if response:
                response_message = decode_message(response)
                print(f"Response from Peripheral: {response_message}")
            msg = encode_message(message)
            print(f"msg {msg}")
            characteristic.write(msg)
            
            print(f"{IAM} sent: {message}, received {response}")
        except Exception as e:
            print(f"writing error {e}")
            continue
        
        await asyncio.sleep(0.5)
            
async def receive_data_task(connection, characteristic):
    global message_count
    while True:
        try:
            response = await characteristic.write(encode_message("I got it"))
            await asyncio.sleep(0.5)
            
            message_count += 1
            
        except asyncio.TimeoutError:
            print("Timeout waiting for data in {ble_name}.")
            break
        except Exception as e:
            print(f"Error receiving data: {e}")
            break
        
        try:
            data = await characteristic.read()
            if data:    
                print(f"{IAM} received: {decode_message(data)}, count: {message_count}")
#                 await asyncio.sleep(1)
        except Exception as e:
            print(f"Error sending response  data: {e}")
            break

async def run_peripheral_mode():
    # Set up the Bluetooth service and characteristic
    ble_service = aioble.Service(ble_svc_uuid)
    characteristic = aioble.Characteristic(
        ble_service,
        ble_characteristic_uuid,
        read=True,
        notify=True
    )
    aioble.register_services(ble_service)

    print(f"{ble_name} starting to advertise")

    while True:
        async with await aioble.advertise(
            ble_advertising_interval,
            name=ble_name,
            services=[ble_svc_uuid],
            appearance=ble_appearance) as connection:
            print(f"{ble_name} connected to another device: {connection.device}")

            tasks = [
                # asyncio.create_task(send_and_receive(connection, characteristic)),
                asyncio.create_task(send_data_task(connection, characteristic)),
#                 asyncio.create_task(receive_data_task(connection, characteristic)),
            ]
            await asyncio.gather(*tasks)
            print(f"{IAM} disconnected")
            break

async def ble_scan():
    print(f"Scanning for BLE Beacon named {ble_name}...")
    
    async with aioble.scan(5000, interval_us=30000, window_us=30000, active=True) as scanner:
        async for result in scanner:
            if result.name() == IAM_SENDING_TO and ble_svc_uuid in result.services():
                print(f"found {result.name()} with service uuid {ble_svc_uuid}")
                return result
    return None

async def run_central_mode():
    # Start scanning for a device with the matching service UUID
    while True:
        device = await ble_scan()
        
        if device is None:
            continue
        print(f"device is: {device}, name is {device.name()}")

        try:
            print(f"Connecting to {device.name()}")
            connection = await device.device.connect()
            
        except asyncio.TimeoutError:
            print("Timeout during connection")
            continue

        print(f"{IAM} connected to {connection}")


        # Discover services
        async with connection:
            try:
                service = await connection.service(ble_svc_uuid)
                characteristic = await service.characteristic(ble_characteristic_uuid)
            except (asyncio.TimeoutError, AttributeError):
                print("Timed out discovering services/characteristics")
                continue
            except Exception as e:
                print(f"Error discovering services {e}")
                await connection.disconnect()
                continue
        
            tasks = [
                asyncio.create_task(receive_data_task(connection, characteristic)),

            ]
            await asyncio.gather(*tasks)

            await connection.disconnected()
            print(f"{ble_name} disconnected from {device.name()}")
            break

async def main():
    while True:
        if IAM == "Central":    
            tasks = [
                asyncio.create_task(run_central_mode()),
            ]
        else:
            tasks = [
                asyncio.create_task(run_peripheral_mode()),
            ]
        
        await asyncio.gather(*tasks)
        
asyncio.run(main())





