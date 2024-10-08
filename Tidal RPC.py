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
disc_found = False
RPC = Presence(client_id)


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


def clear():
    # for windows
    if name == 'nt':
        _ = system('cls')
    # for mac and linux (here, os.name is 'posix')
    else:
        _ = system('clear')


while not disc_found:
    try:
        RPC.connect()
    # Notify the user if their entered client ID is invalid.
    except InvalidID:
        print("Invalid client ID. Please check the entered value.")
        sleep(5)
        sys.exit(1)
    # A catch-all exception. The program should always continue attempting to connect to Discord.
    except Exception:
        print("Discord not running, going to sleep for one minute.", end='\n')
        try:
            print("Hit CTRL-C if you want to terminate the script.", end='\n')
            sleep(60)
            clear()
        except KeyboardInterrupt:
            print("Script terminated by user. Exiting.")
            sys.exit(0)
    # If there is no exception here, the discord connection has been successfully made.
    else:
        disc_found = True
    
# Update your status every 15 seconds (to stay within rate limits).
while True:
    try:
        details = get_tidal_info()
        RPC.update(
            state=f"by {details[1]}",
            details=details[0],
            large_image="tidallogo",
            large_text="TIDAL",
            small_image="hra",
            small_text="Streaming lossless in up to 24-bit 192kHz."
        )
        clear()
        print("Rich presence active...", end='\n')
    # A catch-all exception. The program should continue attempting to find the TIDAL window
    # and maintain its Discord connection under all circumstances.
    except Exception:
        RPC.update(
            details="Paused",
            large_image="tidallogo",
            large_text="TIDAL"
        )
        clear()
        print("Streaming paused or window closed...", end='\n')
    try:
        # MUST be no less than 15 seconds to remain within Discord rate limits.
        print("Hit CTRL-C if you want to terminate the script.", end='\n')
        sleep(15)
    # Close RPC connection properly on user CTRL-C
    except KeyboardInterrupt:
        RPC.close()
        clear()
        print("Script terminated by user. Exiting.")
        sys.exit(0)
