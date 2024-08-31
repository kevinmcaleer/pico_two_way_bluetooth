import aioble
import bluetooth
import uasyncio as asyncio

# Define UUIDs for the service and characteristic
_SERVICE_UUID = bluetooth.UUID(0x1848)
_CHARACTERISTIC_UUID = bluetooth.UUID(0x2A6E)

IAM = "Central"
ping_message = "Ping from Central"

def encode_message(message):
    return message.encode('utf-8')

def decode_message(message):
    return message.decode('utf-8')

async def notification_callback(characteristic, data):
    print(f"{IAM} received notification: {decode_message(data)}")

async def ble_scan():
    print(f"{IAM} scanning for peripheral...")

    async with aioble.scan(5000, interval_us=30000, window_us=30000, active=True) as scanner:
        async for result in scanner:
            if _SERVICE_UUID in result.services():
                print(f"Found peripheral with service UUID {_SERVICE_UUID}")
                return result.device
    return None

async def run_central_mode():
    device = await ble_scan()
    if not device:
        print(f"{IAM} could not find peripheral.")
        return

    print(f"Connecting to the peripheral...")

    try:
        connection = await device.connect()
        print(f"{IAM} connected to the peripheral.")

        await asyncio.sleep(1)

        services = await connection.services()
        service = services.get(_SERVICE_UUID)
        if not service:
            print("No service found")
            await connection.disconnect()
            return

        characteristic = await service.characteristic(_CHARACTERISTIC_UUID)
        print(f"Characteristic found.")

        # Subscribe to notifications on the characteristic
        await characteristic.subscribe(notification_callback)
        print(f"{IAM} subscribed to notifications.")

        # Send a ping message to the peripheral
        await characteristic.write(encode_message(ping_message))
        print(f"{IAM} sent: {ping_message}")

        # Wait for notifications indefinitely
        while connection.is_connected():
            await asyncio.sleep(1)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        await connection.disconnect()
        print(f"{IAM} disconnected from the peripheral.")

async def main():
    await run_central_mode()

asyncio.run(main())
