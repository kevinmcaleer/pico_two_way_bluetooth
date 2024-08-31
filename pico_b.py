import aioble
import bluetooth
import uasyncio as asyncio

# Define UUIDs for the service and characteristic
_SERVICE_UUID = bluetooth.UUID(0x1848) 
_CHARACTERISTIC_UUID = bluetooth.UUID(0x2A6E)

async def send_data_task(connection, characteristic):
    while True:
        message = "Hello from Pico B!"
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
    # Scan for 5 seconds to find the target device (Pico A)
    async with aioble.scan(5000, interval_us=30000, window_us=30000, active=True) as scanner:
        async for result in scanner:
            print(f"Found device: {result.name()}")
            if result.name() == "PicoA":
                print("Found PicoA, attempting to connect...")
                device = result.device
                break
        else:
            print("PicoA not found.")
            return

    try:
        # Connect to the device
        connection = await device.connect()
        async with connection:
            print("Connected to PicoA")

            # Find the service and characteristic on the receiver
            service = await connection.service(_SERVICE_UUID)
            characteristic = await service.characteristic(_CHARACTERISTIC_UUID)

            # Create tasks for sending and receiving data
            tasks = [
                asyncio.create_task(send_data_task(connection, characteristic)),
                asyncio.create_task(receive_data_task(connection, characteristic)),
            ]
            
            await asyncio.gather(*tasks)

    except Exception as e:
        print(f"Error during connection or communication: {e}")

async def main():
    await run_pico_b()

asyncio.run(main())
