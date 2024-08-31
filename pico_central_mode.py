import aioble
import bluetooth
import asyncio

# Define UUIDs for the service and characteristic
_SERVICE_UUID = bluetooth.UUID(0x1848)
_CHARACTERISTIC_UUID = bluetooth.UUID(0x2A6E)

# Device role configuration
IAM = "Central"  # Change to "Central" or "Peripheral"
MESSAGE = f"Hello from {IAM}!"

# Bluetooth parameters
ble_name = f"Pico_{IAM}"
ble_svc_uuid = bluetooth.UUID(0x181A)
ble_characteristic_uuid = bluetooth.UUID(0x2A6E)
ble_advertising_interval = 2000

# Global message count for the peripheral
message_count = 0

def encode_message(message):
    return message.encode('utf-8')

def decode_message(message):
    return message.decode('utf-8')

async def handle_write_request(characteristic):
    global message_count
    data = await characteristic.read()
    if data:
        received_message = decode_message(data)
        print(f"{IAM} received: {received_message}")
        response_message = f"{MESSAGE}, count: {message_count}"
        await characteristic.write(encode_message(response_message), response=True)
        print(f"{IAM} sent response: {response_message}")
        message_count += 1

async def run_peripheral_mode():
    ble_service = aioble.Service(ble_svc_uuid)
    characteristic = aioble.Characteristic(
        ble_service,
        ble_characteristic_uuid,
        read=True,
        write=True,
        notify=True
    )
    aioble.register_services(ble_service)

    print(f"{IAM} starting to advertise as {ble_name}")

    while True:
        async with await aioble.advertise(
            ble_advertising_interval,
            name=ble_name,
            services=[ble_svc_uuid]) as connection:
            print(f"{IAM} connected to another device: {connection.device}")

            while connection.is_connected():
                await handle_write_request(characteristic)
            print(f"{IAM} disconnected")
            break

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

            # Central sends a message to the peripheral
            request_message = "Requesting data"
            message_count += 1
            await characteristic.write(encode_message(request_message))
            print(f"{IAM} sent: {request_message}")

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
    if IAM == "Peripheral":
        await run_peripheral_mode()
    elif IAM == "Central":
        await run_central_mode()
    else:
        print("Invalid role defined. Please set IAM to 'Central' or 'Peripheral'.")

asyncio.run(main())
