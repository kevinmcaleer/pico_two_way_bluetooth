import aioble
import bluetooth
import uasyncio as asyncio

# UUIDs for the service and characteristic
_SERVICE_UUID = bluetooth.UUID(0x181A)
_CHARACTERISTIC_UUID = bluetooth.UUID(0x2A6E)

# Device role configuration
IAM = "Central"
ping_message = "Ping from Central"

# Bluetooth parameters
ble_name = f"Pico_{IAM}"

def encode_message(message):
    return message.encode('utf-8')

def decode_message(message):
    return message.decode('utf-8')

async def ble_scan():
    print(f"{IAM} scanning for peripheral...")

    async with aioble.scan(5000, interval_us=30000, window_us=30000, active=True) as scanner:
        async for result in scanner:
            if _SERVICE_UUID in result.services():
                print(f"Found peripheral: {result.name()} with service UUID {_SERVICE_UUID}")
                return result
    return None

async def run_central_mode():
    device = await ble_scan()
    if not device:
        print(f"{IAM} could not find peripheral.")
        return

    print(f"Connecting to {device.name()}")

    try:
        connection = await device.connect()
        print(f"{IAM} connected to {device.name()}")

        service = await connection.service(_SERVICE_UUID)
        if not service:
            print("No service found")
            await connection.disconnect()
            return

        characteristic = await service.characteristic(_CHARACTERISTIC_UUID)
        print(f"Characteristic found: {characteristic}")

        # Send a ping message to the peripheral
        await characteristic.write(encode_message(ping_message))
        print(f"{IAM} sent: {ping_message}")

        # Read the response from the peripheral
        response = await characteristic.read()
        if response:
            print(f"{IAM} received response: {decode_message(response)}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        await connection.disconnect()
        print(f"{IAM} disconnected from {device.name()}")

async def main():
    await run_central_mode()

asyncio.run(main())
