import aioble
import bluetooth
import asyncio

# UUIDs for the service and characteristic
_SERVICE_UUID = bluetooth.UUID(0x1848)
_CHARACTERISTIC_UUID = bluetooth.UUID(0x2A6E)

# Device role configuration
IAM = "Peripheral"  # Set to "Peripheral"
MESSAGE = f"Hello back from {IAM}!"

message_count = 0

# Bluetooth parameters
ble_name = f"Pico_{IAM}"
ble_svc_uuid = bluetooth.UUID(0x181A)
ble_characteristic_uuid = bluetooth.UUID(0x2A6E)

def encode_message(message):
    return message.encode('utf-8')

def decode_message(message):
    return message.decode('utf-8')

# Handle incoming write requests from the central
async def handle_write_request(request):
    global message_count
    received_message = decode_message(request.data)
    print(f"{IAM} received: {received_message}")
    response_message = f"{MESSAGE}, count: {message_count}"
    message_count += 1
    await request.characteristic.write(encode_message(response_message), response=True)
    print(f"{IAM} sent response: {response_message}")

async def run_peripheral_mode():
    ble_service = aioble.Service(ble_svc_uuid)
    characteristic = aioble.Characteristic(
        ble_service,
        ble_characteristic_uuid,
        read=True,
        write=True,
        notify=True
    )
    characteristic.on_write(handle_write_request)  # Register the write handler
    aioble.register_services(ble_service)

    print(f"{IAM} starting to advertise as {ble_name}")

    while True:
        async with await aioble.advertise(
            2000,
            name=ble_name,
            services=[ble_svc_uuid]) as connection:
            print(f"{IAM} connected to another device: {connection.device}")

            # Keep the connection active and handle incoming requests
            while connection.is_connected():
                await asyncio.sleep(1)  # Short sleep to keep the loop alive
            
            print(f"{IAM} disconnected")
            break

async def main():
    await run_peripheral_mode()

asyncio.run(main())
