import aioble
import bluetooth
import uasyncio as asyncio

# Define UUIDs for the service and characteristic
_SERVICE_UUID = bluetooth.UUID(0x1848) 
_CHARACTERISTIC_UUID = bluetooth.UUID(0x2A6E)

async def send_data_task(connection, characteristic):
    while True:
        message = "Hello from Pico A!"
        await characteristic.write(message.encode(), response=True)
        print(f"Pico A sent: {message}")
        await asyncio.sleep(2)  # Wait for 2 seconds before sending the next message

async def receive_data_task(connection, characteristic):
    while True:
        try:
            data = await characteristic.notified()
            print(f"Pico A received: {data.decode()}")
        except asyncio.TimeoutError:
            print("Timeout waiting for data in Pico A.")
            break

async def run_pico_a():
    # Set up the Bluetooth service and characteristic
    service = aioble.Service(_SERVICE_UUID)
    characteristic = aioble.Characteristic(service, _CHARACTERISTIC_UUID, read=True, notify=True)

    # Start advertising
    aioble.advertise("PicoA", services=[service])
    print("Pico A is advertising...")

    async with aioble.gap_connect(service) as connection:
        print("Pico A connected to another device.")

        # Create tasks for sending and receiving data
        tasks = [
            asyncio.create_task(send_data_task(connection, characteristic)),
            asyncio.create_task(receive_data_task(connection, characteristic)),
        ]
        
        await asyncio.gather(*tasks)

async def main():
    await run_pico_a()

asyncio.run(main())