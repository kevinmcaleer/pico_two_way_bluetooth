import aioble
import bluetooth
import asyncio

# UUIDs for the service and characteristic
_SERVICE_UUID = bluetooth.UUID(0x181A)
_CHARACTERISTIC_UUID = bluetooth.UUID(0x2A6E)

# Device role configuration
IAM = "Peripheral"
MESSAGE = f"Hello back from {IAM}!"

message_count = 0

# Bluetooth parameters
ble_name = f"Pico_{IAM}"

def encode_message(message):
    return message.encode('utf-8')

def decode_message(message):
    return message.decode('utf-8')

async def handle_write_request(characteristic):
    global message_count
    try:
        # Try reading the data that the central wrote to the characteristic
        data = await characteristic.read()
        if data:
            received_message = decode_message(data)
            print(f"{IAM} received: {received_message}")
            
            # Prepare a response message
            response_message = f"{MESSAGE}, count: {message_count}"
            message_count += 1
            
            # Send the response back to the central
            await characteristic.write(encode_message(response_message))
            print(f"{IAM} sent response: {response_message}")
    except Exception as e:
        print(f"Error in handling write request: {e}")

async def run_peripheral_mode():
    # Create a BLE service and characteristic
    service = aioble.Service(_SERVICE_UUID)
    characteristic = aioble.Characteristic(
        service,
        _CHARACTERISTIC_UUID,
        read=True,
        write=True
    )

    # Start advertising the service
    print(f"{IAM} starting to advertise as {ble_name}")

    while True:
        try:
            async with await aioble.advertise(
                2000,  # Advertising interval in milliseconds
                name=ble_name,
                services=[_SERVICE_UUID]  # Pass the UUID, not the Service object itself
            ) as connection:
                print(f"{IAM} connected to another device: {connection.device}")

                # Loop to check for data being written to the characteristic
                while connection.is_connected():
                    await handle_write_request(characteristic)
                    await asyncio.sleep(0.5)  # Small sleep to prevent tight looping
                
                print(f"{IAM} disconnected")
        except Exception as e:
            print(f"Error during connection handling: {e}")
        finally:
            print("Restarting advertising after disconnection...")
            await asyncio.sleep(1)  # Delay before re-advertising

async def main():
    await run_peripheral_mode()

asyncio.run(main())
