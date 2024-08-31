import aioble
import bluetooth
import asyncio

# UUIDs for the service and characteristic
_SERVICE_UUID = bluetooth.UUID(0x1848)
_CHARACTERISTIC_UUID = bluetooth.UUID(0x2A6E)

# Central device identifiers
IAM = "Pico A"
IAM_SENDING_TO = "Pico B"

MESSAGE = f"Hello from {IAM}!"

# Bluetooth parameters
ble_name = IAM
ble_svc_uuid = bluetooth.UUID(0x181A)
ble_characteristic_uuid = bluetooth.UUID(0x2A6E)

def encode_message(message):
    return message.encode('utf-8')

def decode_message(message):
    return message.decode('utf-8')

async def ble_scan():
    print(f"Scanning for BLE Beacon named {IAM_SENDING_TO}...")

    async with aioble.scan(5000, interval_us=30000, window_us=30000, active=True) as scanner:
        async for result in scanner:
            if result.name() == IAM_SENDING_TO and ble_svc_uuid in result.services():
                print(f"Found {result.name()} with service UUID {ble_svc_uuid}")
                return result
    return None

async def run_central_mode():
    while True:
        device = await ble_scan()
        if not device:
            continue

        print(f"Connecting to {device.name()}")

        try:
            connection = await device.device.connect()
        except Exception as e:
            print(f"Connection error: {e}")
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

            # Central writes a message to the peripheral
            await characteristic.write(encode_message(MESSAGE))
            print(f"{IAM} sent: {MESSAGE}")

            # Central waits for a response from the peripheral
            response = await characteristic.read()
            if response:
                print(f"{IAM} received response: {decode_message(response)}")

        except Exception as e:
            print(f"Error during service/characteristic discovery: {e}")
            await connection.disconnect()
            continue

        await connection.disconnected()
        print(f"{IAM} disconnected from {device.name()}")
        break

async def main():
    await run_central_mode()

asyncio.run(main())
