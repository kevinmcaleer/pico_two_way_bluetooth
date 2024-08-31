import aioble
import bluetooth
import asyncio

# UUIDs for the service and characteristic
_SERVICE_UUID = bluetooth.UUID(0x1848)
_CHARACTERISTIC_UUID = bluetooth.UUID(0x2A6E)

# Peripheral device identifiers
IAM = "Pico B"
MESSAGE = f"Hello back from {IAM}!"

# Bluetooth parameters
ble_name = IAM
ble_svc_uuid = bluetooth.UUID(0x181A)
ble_characteristic_uuid = bluetooth.UUID(0x2A6E)

def encode_message(message):
    return message.encode('utf-8')

def decode_message(message):
    return message.decode('utf-8')

async def handle_write_request(characteristic):
    data = await characteristic.read()
    if data:
        print(f"{IAM} received: {decode_message(data)}")
        response_message = MESSAGE
        await characteristic.write(encode_message(response_message), response=True)
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
    aioble.register_services(ble_service)

    print(f"{IAM} starting to advertise")

    while True:
        async with await aioble.advertise(
            2000,
            name=ble_name,
            services=[ble_svc_uuid]) as connection:
            print(f"{IAM} connected to another device: {connection.device}")

            while connection.is_connected():
                await handle_write_request(characteristic)
            print(f"{IAM} disconnected")
            break

async def main():
    await run_peripheral_mode()

asyncio.run(main())
