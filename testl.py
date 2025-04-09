# test_lidar.py
import time
from rplidar import RPLidar, RPLidarException

# --- TRY BOTH BAUD RATES ---
#BAUD_RATE: int = 115200
BAUD_RATE: int = 256000
# ---------------------------

DEVICE_PATH: str = '/dev/ttyUSB0' # Or your specific path
TIMEOUT: int = 3 # Increased timeout slightly for initial connection

lidar = None
print(f"Attempting connection to {DEVICE_PATH} at {BAUD_RATE} baud...")

try:
    lidar = RPLidar(port=DEVICE_PATH, baudrate=BAUD_RATE, timeout=TIMEOUT)

    print("Connected! Getting device info...")
    info = lidar.get_info()
    print(f"  - Info: {info}")

    print("Getting device health...")
    health = lidar.get_health()
    print(f"  - Health: {health}")

    # Check health status explicitly
    if health[0] == 'Good':
         print("Device health is Good.")
    elif health[0] == 'Warning':
         print(f"Device health Warning: Code {health[1]}")
    elif health[0] == 'Error':
         print(f"Device health Error: Code {health[1]}")
         # Maybe stop here if health is bad
         # raise RPLidarException("Device reporting health error")

    # Optional: Try starting motor briefly if info/health worked
    # print("Starting motor...")
    # lidar.start_motor()
    # time.sleep(2)
    # print("Motor started. Attempting one scan iteration...")
    # # Try getting just one scan packet
    # for i, scan in enumerate(lidar.iter_scans(max_buf_meas=500)):
    #      print(f"Received scan {i} with {len(scan)} measurements.")
    #      break # Stop after the first scan
    # else:
    #      print("Could not get a single scan.")

    print("\nMinimal test successful!")

except RPLidarException as e:
    print(f"\n*** RPLidar Error: {e} ***")
except Exception as e:
    print(f"\n*** General Error: {e} ***")
finally:
    if lidar:
        print("Cleaning up: Stopping motor and disconnecting...")
        try:
            lidar.stop()
            lidar.stop_motor()
        except RPLidarException as e:
             print(f"Error during stop/disconnect: {e}") # Might happen if connection was bad
        finally:
             lidar.disconnect()
    print("Test finished.")
