#   Tidal-Rich-Presence, Discord rich presence for TIDAL.
#   Copyright (C) 2024  Arun Fletcher
#
#   Neither I nor this program are affiliated with TIDAL in any way.
#   The TIDAL wordmark and logo are registered trademarks of TIDAL Music AS.
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.

from pypresence import Presence, InvalidID
from os import system, name
from time import sleep
import sys
import psutil
import win32gui
import win32process

# Application ID (Enter yours here).
client_id = "0000000000000000000"
discord_alive = False
discord_connected = False
RPC = Presence(client_id)
tidal_paused = False

# Returns a list of windows related to the passed process ID.
def get_windows_by_pid(pid):
    pid_windows = []

    def callback(hwnd, hwnds):
        if win32gui.IsWindowVisible(hwnd) and pid == win32process.GetWindowThreadProcessId(hwnd)[1]:
            hwnds.append(hwnd)
        return True
    win32gui.EnumWindows(callback, pid_windows)
    return pid_windows


def get_tidal_info():
    tidal_processes = []
    all_titles = []

    # Finds all processes related to TIDAL.
    for processID in psutil.pids():
        p = psutil.Process(processID)
        if "tidal" in p.name().lower():
            tidal_processes.append(processID)

    # Finds GUI windows related to each PID, if they exist.
    for tidal_process_id in tidal_processes:
        windows = get_windows_by_pid(tidal_process_id)
        # If a PID has a GUI window, add its title to the titles list.
        if windows:
            for w in windows:
                all_titles.append(win32gui.GetWindowText(w))

    song_info = all_titles[0].split(" - ")
    return song_info[0], song_info[1]
    
# If Discord was closed, safety check to see if it's running again before attempting to reconnect. Otherwise it crashes with PipeClosed exception.
def discordRunning():
    processName = "discord"
    # Iterate over the all the running process
    for p in psutil.process_iter():
        try:
            # Check if process name contains the given name string.
            if processName.lower() in p.name().lower():
                print("Discord found!", end='\n')
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    print("Discord NOT found!", end='\n')
    return False;

# OS independent clear screen function.
def clear():
 
    # for windows
    if name == 'nt':
        _ = system('cls')
 
    # for mac and linux(here, os.name is 'posix')
    else:
        _ = system('clear')

# Checks if Discord is running and connects to the rich presence application, otherwise goes to sleep for 60 seconds and retries.
def connectDiscord():
    global discord_connected
    global RPC
    while not discord_connected:
        try:
            RPC.connect()
        # Notify the user if their entered client ID is invalid.
        except InvalidID:
            print("Invalid client ID. Please check the entered value.")
            sleep(5)
            sys.exit(1)
        except Exception:
            print("Discord not running, going to sleep for one minute.", end='\n')
            try:
                print("Hit CTRL-C if you want to terminate the script.", end='\n')
                sleep(60)
                clear()
            except KeyboardInterrupt:
                quit()
        else: discord_connected = True

# Handles the updating of rich presence information while both TIDAL and Discord are found
def updateRPC():
    global RPC
    global details
    RPC.update(
        state=f"by {details[1]}",
        details=details[0],
        large_image="tidallogo",
        large_text="TIDAL",
        small_image="hra",
        small_text="Streaming lossless in up to 24-bit 192kHz."
    )
    print("Rich presence updated...", end='\n')
    
# Function to set the rich presence status to Paused when TIDAL is no longer playing or info can't be found
def pauseRPC():
    global RPC
    RPC.update(
        details="Paused",
        large_image="tidallogo",
        large_text="TIDAL"
    )
    clear()
    print("Streaming paused or window closed...", end='\n')
    print("Rich presence set to Paused.", end='\n')

# Function to terminate the script, usually called from KeyboardInterrupt exception
def quit():
    print("Script terminated by user. Exiting.")
    sys.exit(0)

# Call the function to attempt to connect to Discord
connectDiscord()
# Update your status every 15 seconds (to stay within rate limits).
while True:
    try:
        # Attempt to get info from TIDAL
        details = get_tidal_info()
        print("TIDAL is playing, attempting to update Rich presence...", end='\n')
        tidal_paused = False
    # A catch all exception. The program should continue attempting to find the TIDAL window
    # and maintain its Discord connection under all circumstances.
    except Exception:
        discord_alive = discordRunning()
        if discord_alive:
            pauseRPC()
            tidal_paused = True
        else: print("Discord process no longer found.", end='\n')
    if not tidal_paused:
        try:
            updateRPC()
        except Exception:
            discord_connected = False
            clear()
            print("Discord connection lost or Discord closed, attempting to reconnect.", end='\n')
            connectDiscord()
            print("Discord process now found!", end='\n')
    try:
        # MUST be no less than 15 seconds to remain within Discord rate limits.
        print("Sleeping for 15 seconds. Hit CTRL-C if you want to terminate the script.", end='\n')
        sleep(15)
        clear()
    # Terminate properly on user CTRL-C
    except KeyboardInterrupt:
        discord_alive = discordRunning()
        if discord_alive:
            try:
                print("Attempting to close RPC socket.", end='\n')
                RPC.close()
                quit()
            except Exception:
                quit()
        else: quit()
