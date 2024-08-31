import aioble
import bluetooth
import uasyncio as asyncio

# UUIDs for the service and characteristic
_SERVICE_UUID = bluetooth.UUID(0x181A)
_CHARACTERISTIC_UUID = bluetooth.UUID(0x2A6E)

# Device role configuration
IAM = "Peripheral"
MESSAGE = f"Hello back from {IAM}!"

# Bluetooth parameters
ble_name = f"Pico_{IAM}"

message_count = 0

def encode_message(message):
    return message.encode('utf-8')

def decode_message(message):
    return message.decode('utf-8')

async def handle_central_request(characteristic):
    global message_count
    try:
        # Wait for data to be written by the central
        data = await characteristic.read()
        if data:
            received_message = decode_message(data)
            print(f"{IAM} received: {received_message}")

            # Increment the counter and prepare the response
            message_count += 1
            response_message = f"{MESSAGE}, count: {message_count}"
            await characteristic.write(encode_message(response_message))
            print(f"{IAM} sent response: {response_message}")
    except Exception as e:
        print(f"Error: {e}")

async def run_peripheral_mode():
    # Create a BLE service and characteristic
    service = aioble.Service(_SERVICE_UUID)
    characteristic = aioble.Characteristic(
        service,
        _CHARACTERISTIC_UUID,
        read=True,
        write=True,
        notify=True
    )

    # Start advertising the service
    print(f"{IAM} starting to advertise as {ble_name}")

    while True:
        async with await aioble.advertise(
            2000,  # Advertising interval in milliseconds
            name=ble_name,
            services=[_SERVICE_UUID]
        ) as connection:
            print(f"{IAM} connected to {connection.device}")

            while connection.is_connected():
                await handle_central_request(characteristic)
                await asyncio.sleep(0.5)  # Small sleep to prevent tight looping

            print(f"{IAM} disconnected")

async def main():
    await run_peripheral_mode()

asyncio.run(main())
