from os import path
from sys import exit

import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np
from rplidar import RPLidar, RPLidarException # Import the exception type


BAUD_RATE: int = 256000
TIMEOUT: int = 3

MAC_DEVICE_PATH: str = '/dev/cu.usbserial-0001'
LINUX_DEVICE_PATH: str = '/dev/ttyUSB0'
# Automatically select path based on existence (optional improvement)
# DEVICE_PATH = MAC_DEVICE_PATH if path.exists(MAC_DEVICE_PATH) else LINUX_DEVICE_PATH
DEVICE_PATH: str = LINUX_DEVICE_PATH # Keep as is if you are sure about Linux

D_MAX: int = 5000 # Increased range slightly, adjust as needed (original D_MAX was 500)
I_MIN: int = 0
I_MAX: int = 50


 
 
def verify_device() -> bool:
	    if path.exists(DEVICE_PATH):
	        return True
	    else:
	        return False
	 

def update_plot(lidar_iter, line, ax, fig):
    """Handles getting data and updating the plot elements."""
    try:
        scan = next(lidar_iter)
        valid_measurements = [meas for meas in scan if meas[2] > 0]

        if not valid_measurements:
            return # Nothing to plot for this scan

        offsets = np.array([(np.radians(meas[1]), meas[2]) for meas in valid_measurements])
        intents = np.array([meas[0] for meas in valid_measurements])
        intents_clamped = np.clip(intents, I_MIN, I_MAX)

        line.set_offsets(offsets)
        line.set_array(intents_clamped)

        # Optional: Adjust plot limits dynamically if needed
        # current_rmax = ax.get_rmax()
        # max_dist = offsets[:, 1].max() if offsets.size > 0 else 0
        # if max_dist > current_rmax * 0.9: # Adjust if points get close to edge
        #    ax.set_rmax(max_dist * 1.1)

        # Redraw the canvas
        fig.canvas.draw_idle()
        # Process GUI events and pause briefly
        plt.pause(0.01) # Very important! Allows GUI to update and process signals

    except RPLidarException as e:
        print(f"RPLidar Exception caught during update: {e}")
        # Decide if you want to stop or continue
        # return False # Signal to stop the loop
        return True # Signal to continue trying
    except StopIteration:
        print("Lidar iterator stopped.")
        return False # Stop the loop
    except Exception as e:
        print(f"An unexpected error occurred in update_plot: {e}")
        return False # Stop the loop
    return True # Signal to continue

if __name__ == '__main__':

    if not verify_device():
        print(f'No device found at initial path or fallback: {DEVICE_PATH}')
        exit(1)

    print(f"Connecting to Lidar on: {DEVICE_PATH}")
    lidar = None
    keep_running = True

    try:
        lidar = RPLidar(port=DEVICE_PATH, baudrate=BAUD_RATE, timeout=TIMEOUT) # Use 115200 or 256000

        print("Starting motor...")
        lidar.start_motor()
        # time.sleep(2) # Optional spin-up time

        print("Setting up plot...")
        plt.ion() # Turn on interactive mode!
        fig = plt.figure(figsize=(8, 8))
        ax = plt.subplot(111, projection='polar')
        line = ax.scatter([0], [0], s=5, c=[(I_MIN + I_MAX) / 2], cmap=plt.cm.Greys_r, vmin=I_MIN, vmax=I_MAX, lw=0)
        ax.set_rmax(D_MAX)
        ax.set_theta_zero_location('N')
        ax.set_theta_direction(-1)
        ax.set_title('RPLidar Scan', va='bottom')
        ax.grid(True)
        fig.show() # Show the figure non-blockingly

        print("Starting scan loop...")
        iterator = lidar.iter_scans(max_buf_meas=5000, min_len=50)

        while keep_running:
             keep_running = update_plot(iterator, line, ax, fig)
             # Check if the figure window was closed
             if not plt.fignum_exists(fig.number):
                 print("Plot window closed.")
                 keep_running = False


    except KeyboardInterrupt:
        print('Stopping (Keyboard Interrupt caught).')
        # The finally block will handle cleanup
    except RPLidarException as e:
        print(f"RPLidar connection error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        plt.ioff() # Turn off interactive mode
        plt.close(fig) # Close the plot window explicitly
        if lidar is not None:
            print("Cleaning up Lidar connection...")
            lidar.stop()
            lidar.stop_motor()
            lidar.disconnect()
        print("Exiting.")
