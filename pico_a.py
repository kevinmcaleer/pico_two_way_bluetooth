import aioble
import bluetooth
import asyncio

# Define UUIDs for the service and characteristic
_SERVICE_UUID = bluetooth.UUID(0x1848)
_CHARACTERISTIC_UUID = bluetooth.UUID(0x2A6E)

# Bluetooth parameters
ble_name = "Pico A"  # You can dynamically change this if you want unique names
ble_svc_uuid = bluetooth.UUID(0x181A)
ble_characteristic_uuid = bluetooth.UUID(0x2A6E)
ble_appearance = 0x0300
ble_advertising_interval = 2000
ble_scan_length = 5000
ble_interval = 30000
ble_window = 30000

MESSAGE = "Hello from Pico!"

async def send_data_task(connection, characteristic):
    while True:
        message = MESSAGE
        print(f"sending {message}")
        await characteristic.write(message.encode())
        print(f"{ble_name} sent: {message}")
        await asyncio.sleep(2)  # Wait for 2 seconds before sending the next message

async def receive_data_task(connection, characteristic):
    while True:
        try:
            data = await characteristic.notified()
            print(f"{ble_name} received: {data.decode()}")
        except asyncio.TimeoutError:
            print("Timeout waiting for data in {ble_name}.")
            break

async def run_peripheral_mode():
    # Set up the Bluetooth service and characteristic
    ble_service = aioble.Service(ble_svc_uuid)
    characteristic = aioble.Characteristic(
        ble_service,
        ble_characteristic_uuid,
        read=True,
        notify=True
    )
    aioble.register_services(ble_service)

    print(f"{ble_name} starting to advertise")

    while True:
        async with await aioble.advertise(
            ble_advertising_interval,
            name=ble_name,
            services=[ble_svc_uuid],
            appearance=ble_appearance) as connection:
            print(f"{ble_name} connected to another device: {connection.device}")

            tasks = [
                asyncio.create_task(send_data_task(connection, characteristic)),
                asyncio.create_task(receive_data_task(connection, characteristic)),
            ]
            await asyncio.gather(*tasks)

async def ble_scan():
    print(f"Scanning for BLE Beacon named {ble_name}...")
    
    async with aioble.scan(5000, interval_us=30000, window_us=30000, active=True) as scanner:
        async for result in scanner:
            if result.name() == ble_name and ble_svc_uuid in result.services():
                print(f"found {result.name()} with service uuid {ble_svc_uuid}")
                return result
    return None

async def run_central_mode():
    # Start scanning for a device with the matching service UUID
    device = await ble_scan()
    
    if device is None:
        return
    print(f"device is: {device}, name is {device.name()}")

    try:
        print(f"Connecting to {device.name()}")
        connection = await device.device.connect()
        
    except asyncio.TimeoutError:
        print("Timeout during connection")
        return

    print(f"{ble_name} connected to {connection}")

    # Discover services
    service = await connection.service(ble_svc_uuid)
    if service:
        print(f"service: {service} {dir(service)}")
        characteristic = await service.characteristic(ble_characteristic_uuid)
     
        print(f"characteristic: {characteristic}")
        tasks = [
            asyncio.create_task(send_data_task(connection, characteristic)),
            asyncio.create_task(receive_data_task(connection, characteristic)),
        ]
        await asyncio.gather(*tasks)

        await connection.disconnected()
        print(f"{ble_name} disconnected from {result.name()}")

async def main():
    tasks = [
        asyncio.create_task(run_peripheral_mode()),
        asyncio.create_task(run_central_mode()),
    ]
    
    await asyncio.gather(*tasks)

asyncio.run(main())
