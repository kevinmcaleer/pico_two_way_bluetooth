import aioble
import bluetooth
import struct
import asyncio

# Define UUIDs for the service and characteristic
_SERVICE_UUID = bluetooth.UUID(0x1848)
_CHARACTERISTIC_UUID = bluetooth.UUID(0x2A6E)

ble_name = "Pico B"
ble_svc_uuid = bluetooth.UUID(0x181A)
ble_characteristic_uuid = bluetooth.UUID(0x2A6E)
ble_appearance = 0x0300
ble_advertising_interval = 2000

MESSAGE = "Hello from Pico B!"

async def send_data_task(connection, characteristic):
    while True:
        message = MESSAGE
        await characteristic.write(message.encode(), response=True)
        print(f"Pico B sent: {message}")
        await asyncio.sleep(2)  # Wait for 2 seconds before sending the next message

async def receive_data_task(connection, characteristic):
    while True:
        try:
            data = await characteristic.notified()
            print(f"Pico B received: {data.decode()}")
        except asyncio.TimeoutError:
            print("Timeout waiting for data in Pico B.")
            break

async def run_pico_b():
    # Set up the Bluetooth service and characteristic
    ble_service = aioble.Service(ble_svc_uuid)
    characteristic = aioble.Characteristic(
        ble_service,
        ble_characteristic_uuid,
        read=True,
        notify=True)
    aioble.register_services(ble_service)
    # Start advertising

    while True:
        async with await aioble.advertise(
            ble_advertising_interval,
            name=ble_name,
            services=[ble_svc_uuid],
            appearance=ble_appearance) as connection:
            print("Pico A connected to another device: {connection.device}")

            await connection.disconnected()
       
        # Create tasks for sending and receiving data
        tasks = [
            asyncio.create_task(send_data_task(connection, characteristic)),
            asyncio.create_task(receive_data_task(connection, characteristic)),
        ]
        
        await asyncio.gather(*tasks)

asyncio.run(run_pico_b())


