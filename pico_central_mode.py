import aioble
import bluetooth
import asyncio

# UUIDs for the service and characteristic
_SERVICE_UUID = bluetooth.UUID(0x1848)
_CHARACTERISTIC_UUID = bluetooth.UUID(0x2A6E)

# Device role configuration
IAM = "Central"  # Change to "Central" or "Peripheral"
MESSAGE = f"Hello back from {IAM}!"

message_count = 0

# Bluetooth parameters
ble_name = IAM
ble_svc_uuid = bluetooth.UUID(0x181A)
ble_characteristic_uuid = bluetooth.UUID(0x2A6E)

def encode_message(message):
    return message.encode('utf-8')

def decode_message(message):
    return message.decode('utf-8')

async def ble_scan():
    print(f"{IAM} scanning for peripheral...")

    async with aioble.scan(5000, interval_us=30000, window_us=30000, active=True) as scanner:
        async for result in scanner:
            if ble_svc_uuid in result.services():
                print(f"Found peripheral: {result.name()} with service UUID {ble_svc_uuid}")
                return result
    return None

async def run_central_mode():
    global message_count
    while True:
        device = await ble_scan()
        if not device:
            print(f"{IAM} could not find peripheral. Retrying...")
            await asyncio.sleep(2)  # Wait before retrying scan
            continue

        print(f"Connecting to {device.name()}")

        try:
            connection = await device.device.connect()
        except Exception as e:
            print(f"Connection error: {e}")
            await asyncio.sleep(2)  # Wait before retrying connection
            continue

        print(f"{IAM} connected to {device.name()}")

        try:
            service = await connection.service(ble_svc_uuid)
            if not service:
                print("No service found")
                await connection.disconnect()
                continue

            characteristic = await service.characteristic(ble_characteristic_uuid)
            print(f"Characteristic found: {characteristic}")

            while connection.is_connected():
                # Central writes a message to the peripheral
                request_message = f"Requesting data {message_count}"
                message_count += 1
                await characteristic.write(encode_message(request_message))
                print(f"{IAM} sent: {request_message}")

                # Central waits for a response from the peripheral
                response = await characteristic.read()
                if response:
                    print(f"{IAM} received response: {decode_message(response)}")

                await asyncio.sleep(2)  # Wait before sending the next request

        except Exception as e:
            print(f"Error during service/characteristic discovery: {e}")
            await connection.disconnect()
            continue

        print(f"{IAM} disconnected from {device.name()}")
        await asyncio.sleep(2)  # Wait before trying to reconnect

async def main():
    await run_central_mode()

asyncio.run(main())
