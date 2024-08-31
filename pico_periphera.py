import aioble
import bluetooth
import uasyncio as asyncio

# Define UUIDs for the service and characteristic
_SERVICE_UUID = bluetooth.UUID(0x1848)
_CHARACTERISTIC_UUID = bluetooth.UUID(0x2A6E)

IAM = "Peripheral"
MESSAGE = f"Hello back from {IAM}!"

# Bluetooth parameters
ble_name = f"{IAM}"
ble_svc_uuid = bluetooth.UUID(0x181A)
ble_characteristic_uuid = bluetooth.UUID(0x2A6E)
ble_advertising_interval = 2000
message_count = 0

def encode_message(message):
    return message.encode('utf-8')

def decode_message(message):
    return message.decode('utf-8')

async def handle_central_request(characteristic, connection):
    global message_count
    try:
        # Wait for data from the central
        data = await characteristic.read()
        if data:
            received_message = decode_message(data)
            print(f"{IAM} received: {received_message}")
            message_count += 1

            # Prepare a notification response
            response_message = f"{MESSAGE}, count: {message_count}"
            await characteristic.notify(connection, encode_message(response_message))
            print(f"{IAM} notified response: {response_message}")

    except Exception as e:
        print(f"Error: {e}")

async def run_peripheral_mode():
    # Set up the Bluetooth service and characteristic
    service = aioble.Service(ble_svc_uuid)
    characteristic = aioble.Characteristic(
        service,
        ble_characteristic_uuid,
        read=True,
        notify=True  # Enable notifications on this characteristic
    )
    aioble.register_services(service)

    print(f"{ble_name} starting to advertise")

    while True:
        connection = await aioble.advertise(
            ble_advertising_interval,
            name=ble_name,
            services=[ble_svc_uuid]
        )
        print(f"{ble_name} connected to another device: {connection.device}")

        # Handle requests from the central
        while connection.is_connected():
            await handle_central_request(characteristic, connection)
            await asyncio.sleep(0.5)

        print(f"{IAM} disconnected")

async def main():
    await run_peripheral_mode()

asyncio.run(main())
