# peripheral.py

import aioble
import bluetooth
import asyncio
import sys

# UUIDs for the service and characteristic
_SERVICE_UUID = bluetooth.UUID(0x181A)  # Environmental Sensing Service UUID
_CHARACTERISTIC_UUID = bluetooth.UUID(0x2A6E)  # Temperature Characteristic UUID

# Device role configuration
IAM = "Peripheral"
MESSAGE = f"Hello from {IAM}!"

message_count = 0

def encode_message(message):
    return message.encode('utf-8')

def decode_message(data):
    return data.decode('utf-8')

async def main():
    # Initialize BLE
    ble = bluetooth.BLE()
    aioble.register_ble(ble)

    # Create BLE service and characteristic
    service = aioble.Service(_SERVICE_UUID)
    characteristic = aioble.Characteristic(
        service,
        _CHARACTERISTIC_UUID,
        read=True,
        write=True,
        notify=True
    )
    aioble.register_services(service)

    print(f"{IAM}: Starting advertising...")

    # Start advertising
    async with aioble.advertise(
        interval_us=500_000,  # 500ms
        services=[_SERVICE_UUID],
        name="PicoPeripheral"
    ) as advertisement:
        print(f"{IAM}: Advertising now...")

        while True:
            # Wait for a connection
            connection = await aioble.accept()
            print(f"{IAM}: Connected to {connection.device}")

            try:
                while True:
                    # Wait for write requests
                    request = await characteristic.written()
                    if request:
                        global message_count
                        received_message = decode_message(request)
                        print(f"{IAM}: Received: {received_message}")

                        response_message = f"{MESSAGE}, count: {message_count}"
                        message_count += 1

                        # Send notification back to central
                        await characteristic.notify(connection, encode_message(response_message))
                        print(f"{IAM}: Sent response: {response_message}")

            except Exception as e:
                print(f"{IAM}: Connection error: {e}")
            finally:
                await connection.disconnect()
                print(f"{IAM}: Disconnected")

# Run the main event loop
asyncio.run(main())
