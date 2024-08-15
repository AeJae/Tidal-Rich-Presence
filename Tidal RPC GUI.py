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
import PySimpleGUI as sg
import threading
from psgtray import SystemTray

# Application ID (Enter yours here).
client_id = "0000000000000000000"
discord_alive = False
discord_connected = False
RPC = Presence(client_id)
tidal_paused = True
tidal_alive = False

# Returns a list of windows related to the passed process ID.
def get_windows_by_pid(pid):
    pid_windows = []

    def callback(hwnd, hwnds):
        _, found_pid = win32process.GetWindowThreadProcessId(hwnd)
        if win32gui.IsWindowVisible(hwnd) and pid == found_pid:
            hwnds.append(hwnd)
        return True

    win32gui.EnumWindows(callback, pid_windows)
    return pid_windows


def get_tidal_info():
    tidal_processes = []
    all_titles = []

    # Finds all processes related to TIDAL.
    for process in psutil.process_iter(attrs=['pid', 'name']):
        try:
            if "tidal" in process.info['name'].lower():
                tidal_processes.append(process.info['pid'])
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    # Finds GUI windows related to each PID, if they exist.
    for tidal_process_id in tidal_processes:
        windows = get_windows_by_pid(tidal_process_id)
        # If a PID has a GUI window, add its title to the titles list.
        for w in windows:
            window_text = win32gui.GetWindowText(w)
            if window_text:
                all_titles.append(window_text)

    # Process titles to extract song information.
    if all_titles:
        song_info = all_titles[0].split(" - ")
        if len(song_info) >= 2:
            return song_info[0], song_info[1]

    return None, None
    
# If Discord was closed, safety check to see if it's running again before attempting to reconnect. Otherwise it crashes with PipeClosed exception.
def processRunning(processName):
    #print("Debug: looking for process " + processName, end='\n')
    # Iterate over the all the running process
    for p in psutil.process_iter(['name']):
        try:
            # Check if process name contains the given name string.
            if processName.lower() in p.info['name'].lower():
                #print("Debug: " + processName + " found!", end='\n')
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    #print("Debug: " + processName + " NOT found!", end='\n')
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
            print("Invalid client ID. Please check the entered value in the code.")
            sleep(5)
            quit(1)
        except Exception:
            print("Discord not running, going to sleep for one minute.", end='\n')
            try:
                print("Hit Exit if you want to terminate the script.", end='\n')
                sleep(60)
                clear()
            except KeyboardInterrupt:
                quit(0)
        else: discord_connected = True
        
def waitForTidal():
    global tidal_alive
    while not tidal_alive:
        clear()
        print("Tidal not running, going to sleep for one minute.", end='\n')
        try:
            print("Hit Exit if you want to terminate the script.", end='\n')
            sleep(60)
            tidal_alive = processRunning("tidal")
        except KeyboardInterrupt:
            quit(0)
    clear()
    print("TIDAL is now running!", end='\n')

# Handles the updating of rich presence information while both TIDAL and Discord are found
def updateRPC():
    global RPC
    global details
    global tidal_alive
    tidal_alive = processRunning("tidal")
    if tidal_alive:
        RPC.update(
            state=f"by {details[1]}",
            details=details[0],
            large_image="tidallogo",
            large_text="TIDAL",
            small_image="hra",
            small_text="Streaming lossless in up to 24-bit 192kHz."
        )
        print("Rich presence successfully updated!", end='\n')
    else: print("Tidal process not found.", end='\n')
    
# Function to set the rich presence status to Paused when TIDAL is no longer playing or info can't be found
def pauseRPC():
    global RPC
    global tidal_alive
    global tidal_paused
    tidal_alive = processRunning("tidal")
    if tidal_alive:
        RPC.update(
            details="Paused",
            large_image="tidallogo",
            large_text="TIDAL"
        )
        print("Streaming paused or window closed...", end='\n')
        print("Rich presence set to Paused.", end='\n')
        tidal_paused = True
    else: print("Tidal process not found.", end='\n')
    
# Function to terminate the script, usually called from KeyboardInterrupt exception
def quit(code):
    print("Script terminated by user. Exiting.", end='\n')
    sleep(1)
    try:
        RPC.close()
        print("Successfully closed socket.", end='\n')
        sleep(1)
        tray.close()
        window.close()
        sys.exit(code)
    except Exception:
        sys.exit(code)

def the_gui():
    menu = ['', ['Show Window', 'Hide Window', 'Exit']]
    tooltip = 'Tidal RPC'
    layout = [[sg.Text("TIDAL Rich Presence for Discord")], [sg.Multiline(size=(50, 7), key='-ML-', reroute_stdout=True, write_only=True, autoscroll=True, auto_refresh=True, reroute_cprint=True)],
    [sg.T('Double click icon to restore, or right click and choose Show Window!')],
    [sg.Button("Hide Window")],
    [sg.Button("Exit")]]
    window = sg.Window("TIDAL RPC", layout, finalize=True)
    app_icon = b'AAABAAEAICAAAAEAIACoEAAAFgAAACgAAAAgAAAAQAAAAAEAIAAAAAAAABAAAMIOAADCDgAAAAAAAAAAAAAAAAAA9mJWAPZiVg72YlZi9mJWv/ZiVvL2Ylb/9mJW8vZiVsH2YlZj9mJWDvZiVgDzYlUAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAPZiVgD2YlYc9mJWpPZiVvf2Ylb/9mJW//ZiVv/2Ylb/9mJW//ZiVvf2Ylal9WJWHPhjVwDbV00AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA9mJWEvZiVqr2YVX/9mBU//ZhVf/2YVX/9mFV//ZhVf/2YVX/9mBU//ZiVv/tXlOzQB0aQgQGBzwICAg8CAgIPAgICDwICAg8CAgIPAgICDwICAg8CAgIPAgICDwICAg8CAgIPAgICDwICAg7BwcHKwICAgpycnIAAAAAAAAAAAD2YlZ09mJW+fdqXv/5mJD/+qOc//dyZ//3dWv/93Jo//qknf/5mJD/92pe//VhVf1zMy7tDQ8P6hAQEOoQEBDqEBAQ6hAQEOoQEBDqEBAQ6hAQEOoQEBDqEBAQ6hAQEOoQEBDqEBAQ6hAQEOoQDxDbDQ0NcAAAAAcDAwQAAAAAAPZiVtH2YFT/+qSd///8/P/+7ez//eDe//7t7P/94d7//u3s///8/P/6rqj/+WJW/7dMQ/8aFBT/EhIS/xISEv8SEhL/EhIS/xISEv8SEhL/EhIS/xISEv8SEhL/EhIS/xISEv8SEhL/EhIS/xISEv8RERHWCgoKIA4NDQAAAAAA9mJW+vZgVP/7sKr///////zCvf/6o5z//vb1//qlnv/8wb3///////u4sv/4YVX/2FdN/ywcGv8SEhP/FBMT/xMTE/8TExP/FBMT/xMTE/8TExP/ExMT/xMTE/8TExP/ExMT/xMTE/8TExP/FBMT/xMTE+YNDQ0sERERAAAAAAD2Ylb89mBT//mZkf///v7//NPQ//u8t///+fn/+724//zTz////v7/+ZmR//hgVP/ZWE7/Lh0c/xMUFf8VFRX/FRQV/xUVFf8VFRX/FRQV/xUUFf8VFRX/FRQV/xUUFf8VFRX/FRUV/xUVFf8VFBX/FBQU5g4ODi0TExMAAAAAAPZiVtn2YVX/93No//3j4f////////////////////////////3j4f/3c2j/+WJW/79PRv8gGRn/FhYW/xcWFv8XFhb/FxYW/xcWFv8XFhb/FxYW/xcWFv8XFhb/FxYW/xcWFv8XFhb/FxYW/xcWFv8WFRXmEA8PLRUUFAAAAAAA9mJWg/ZiVvz2YVX/+ZOL//3Y1f/81NH/+8G8//zU0P/92Nb/+ZSL//ZhVf/3Ylb/fTk0/xYXF/8YFxj/FxYW/xYWFv8YFxj/GBcY/xgXGP8YFxj/GBcY/xgXGP8YFxj/GBcX/xgXF/8YFxj/GBcY/xcWF+YQEBAtFhUWAAAAAAD2YlYa9mJWu/ZiVv/2YVX/9mld//ZpXv/2YVX/9mle//ZpXf/2YVX/+mNX/75PRv8uHx//GRkZ/xgXF/84Nzf/ODc3/xgXF/8aGRn/GhkZ/xoZGf8aGRn/GhkZ/xoZGf8aGRn/GhkZ/xoZGf8aGRn/GRgY5hIRES0YFxcAAAAAAPZiVgD2YlYp82FVvvdiVv/5Ylb/92JW//diVv/3Ylb/+WNW//ZiVv+9UEb/PiYk/xkZGv8ZGBj/Pz4+/8K/wP/Cv8D/Pz4+/xkYGP8bGhr/Gxoa/xsaGv8bGhv/Gxoa/xsaGv8bGhr/Gxoa/xsaGv8bGRrmExISLRkYGAAAAAAAfzIsAGUyLgBqMSw4hD0368FRSP/hW1D/6l5S/+FbUP/CUUj/fTs2/y8hIf8bGxv/HBsb/0JBQf/DwMH/9PDx//Pw8P/DwMH/QkBB/xwbG/8dHBz/HRwc/x0cHP8dHBz/HRwc/x0cHP8dHBz/HRwc/xwbG+YUExMtGxoaAAAAAAAAAAAAGRoaABITFCwbHBzmKSAg/0AoJv9KKyn/Pygm/ykgIP8cHB3/HR0d/x4cHf8mJCT/rKmq//f09f/y7/D/8u/w//bz9P+rqan/JiQk/x4cHf8fHR3/Hx0d/x8dHf8fHR3/Hx0d/x8dHf8fHR3/Hhwc5hUUFC0cGxsAAAAAAAAAAAAdHBwAFhUVLR8eHuYfHh//Hh4e/x0eHv8eHh7/Hx4f/yAfH/8gHx//IB8f/yAeH/9ZV1f/2NXV//bz9P/28/P/19TV/1hXV/8gHh//IB8f/yAfH/8gHx//IB8f/yAfH/8gHx//IB8f/yAfH/8fHh7mFhUVLR0cHAAAAAAAAAAAAB8dHgAXFhYtIR8f5iIgIP8iICD/IiAg/yIgIP8iICD/IB4f/yAfH/8iICD/IiAg/x8eHv9ZV1f/2dbX/9jW1v9YVlf/Hx4e/yIgIP8iICD/IB8f/yAeH/8iICD/IiAg/yIgIP8hICD/IiAg/yEfH+YXFhYtHx0dAAAAAAAAAAAAIB4fABgXFy0iICHmIyEi/yMhIv8jISL/IyEi/yEfIP9APz//ODc3/yEfIP8jISL/IyEi/x8dHv9samr/bGpq/x8dHv8jISL/IyEi/yEfIP84Nzf/QD4+/yEfIP8jISL/IyEi/yMhIv8jISL/IiAh5hgXFy0gHh8AAAAAAAAAAAAiISEAGRgYLSQiIuYlIyP/JSMj/yUjI/8iICH/TEpK/87Nzf+7ubr/PDo6/yMhIf8iICH/QT9A/8C+vv+/vr7/QT8//yIgIf8iICH/PDo6/7q3uP/Mysv/S0lK/yIgIf8lIyP/JSMj/yUjI/8kIiLmGRgYLSIgIAAAAAAAAAAAACMhIgAaGRktJSMk5iYkJf8mJCX/JSMk/05MTf/Qz8///fz8//z7+/+7urr/Pjw8/0NBQf/DwcL//Pr6//z6+v/CwcH/Q0FB/z47PP+6uLn/+vj4//v5+f/OzMz/TkxM/yUjJP8mJCT/JiQk/yUjJOYaGRktIyEiAAAAAAAAAAAAJSMjABsaGi0nJSXmKCYm/yclJf80MjL/wcDA///////8+/v//Pv7//7+/v+tq6v/tbOz//7+/v/7+vr/+/n5//79/f+0s7P/rKqq//37/P/6+Pj/+fj4//78/P+/vb3/NDIy/yclJf8oJib/JyUl5hsaGi0lIiMAAAAAAAAAAAAnJCUAHBsbLSgmJ+YqJyj/KScn/yooKf90cnP/7Ovr////////////397e/2BfX/9pZ2j/5eTl//79/f/+/f3/5eTk/2lnZ/9gXl7/3tzc//38/P/9/Pz/6ujo/3Nxcf8rKCn/KScn/yonKP8oJibmHBsbLSYkJAAAAAAAAAAAACclJQAeHBwtKico5isoKf8rKCn/Kygp/yonKP90cnP/7u3t/+Hg4f9gXl7/KCYm/yknJ/9pZ2j/5+fn/+fm5/9pZ2j/KScn/ykmJv9fXV7/4N/f/+zr7P9zcXL/Kico/ysoKf8rKCn/Kygp/yonKOYdHBwtJyUmAAAAAAAAAAAAKSYnAB8dHS0sKSnmLSoq/y0qKv8tKir/LCoq/ywqKv9ta2v/X11e/ysoKP8tKir/LSoq/ysoKf9mZGT/ZmRk/ysoKf8sKir/LSoq/ysoKP9fXV3/bGpq/ywpKv8tKir/LSoq/y0qKv8tKir/LCkp5h8dHS0pJicAAAAAAAAAAAAqJygAIB0eLS0qK+YuKyz/Liss/y4rLP8uKyz/Liss/ywpKv8tKir/Liss/y4rLP8uKyz/Liss/y0pKv8sKSr/Liss/y4rLP8uKyz/Liss/y0qKv8sKSr/Liss/y4rLP8uKyz/Liss/y4rLP8tKivmIB4eLSonKAAAAAAAAAAAACwpKQAhHx8tLyws5jAtLf8wLS3/MC0t/zAtLf8wLS3/MC0t/zAtLf8wLS3/MC0t/zAtLf8wLS3/MC0t/zAtLf8wLS3/MC0t/zAtLf8wLS3/MC0t/zAtLf8wLS3/MC0t/zAtLf8wLS3/MC0t/y8sLOYhHx8tLCkpAAAAAAAAAAAALSorACIgIC0wLS7mMS4v/zEuL/8xLi//MS4v/zEuL/8xLi//MS4v/zEuL/8xLi//MS4v/zEuL/8xLi//MS4v/zEuL/8xLi//MS4v/zEuL/8xLi//MS4v/zEuL/8xLi//MS4v/zEuL/8xLi//MC0u5iIgIC0tKisAAAAAAAAAAAAvLCwAIyEhLTIvL+YzMDD/MzAw/zMwMP8zMDD/MzAw/zMwMP8zMDD/MzAw/zMwMP8zMDD/MzAw/zMwMP8zMDD/MzAw/zMwMP8zMDD/MzAw/zMwMP8zMDD/MzAw/zMwMP8zMDD/MzAw/zMwMP8yLy/mIyEhLS8sLAAAAAAAAAAAADAsLQAkISIsMzAx5TQxMv80MTL/NDEy/zQxMv80MTL/NDEy/zQxMv80MTL/NDEy/zUxMv81MTL/NTEy/zQxMv80MTL/NDEy/zQxMv80MTL/NDEy/zQxMv80MTL/NDEy/zQxMv80MTL/NTEy/zMwMeUkIiIsMC0tAAAAAAAAAAAAKygpACQhIRw0MTHSNjMz/zYyM/82MjP/NjIz/zYyM/82MjP/NjIz/zYzM/82MzP/NjIz/zYyM/82MjP/NjIz/zYyM/82MjP/NjIz/zYyM/82MjP/NjIz/zYyM/82MjP/NjIz/zYyM/82MzP/NDEx0iQhIhwrKSkAAAAAAAAAAAAYFhcAAAAAAjIvMGA3MzTRNzM04zczNOM3MzTjNzM04zczNOM3MzTjNzM04zczNOM3MzTjNzM04zczNOM3MzTjNzM04zczNOM3MzTjNzM04zczNOM3MzTjNzM04zczNOM3MzTjNzM04zczNNEzLzBfAAAAAhgXFwAAAAAAAAAAAAAAAAAjISIAIR8gAi4rKxcwLS0jMC0uJDAtLSQwLS4kMC0tJDAtLSQwLS4kMC0tJDAtLiQwLS4kMC0tJDAtLiQwLS0kMC0uJDAtLSQwLS4kMC0uJDAtLiQwLS0kMC0tJDAtLiQwLS4kLisrFyEeHwIkISEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAwB///4AP//8AAAAHAAAAAwAAAAMAAAADAAAAAwAAAAMAAAADAAAAA4AAAAPAAAADwAAAA8AAAAPAAAADwAAAA8AAAAPAAAADwAAAA8AAAAPAAAADwAAAA8AAAAPAAAADwAAAA8AAAAPAAAADwAAAA8AAAAPgAAAH//////////8='
    tray = SystemTray(menu, single_click_events=False, window=window, tooltip=tooltip, icon=app_icon)
    threading.Thread(target=TIDAL, args=(window,), daemon=True).start()
    sg.cprint_set_output_destination(window, '-ML-')
    window.hide()
    tray.show_icon() 
    tray.show_message('TIDAL RPC', 'TIDAL RPC hidden! Double click to show again.')
    # --------------------- EVENT LOOP ---------------------
    while True:
        # wait for up to 100 ms for a GUI event
        event, values = window.read()
        if event == tray.key:
            #sg.cprint(f'System Tray Event = ', values[event], c='white on red')
            event = values[event]       # use the System Tray's event as if was from the window
        if event == ('Exit'):
            break
        
        #sg.cprint(event, values)
        #tray.show_message(title=event, message=values)

        if event in ('Show Window', sg.EVENT_SYSTEM_TRAY_ICON_DOUBLE_CLICKED):
            window.un_hide()
            window.bring_to_front()
        elif event in ('Hide Window', sg.WIN_CLOSE_ATTEMPTED_EVENT):
            window.hide()
            tray.show_icon()        # if hiding window, better make sure the icon is visible
            tray.show_message('TIDAL RPC', 'TIDAL RPC hidden! Double click to show again.')
        elif event == 'Hide Icon':
            tray.hide_icon()
        elif event == 'Show Icon':
            tray.show_icon()
        # --------------- Loop through all messages coming in from threads ---------------
    # if user exits the window, then close the window and exit the GUI func
    quit(0)

def TIDAL(window):
    global tidal_paused
    global tidal_alive
    global discord_alive
    global discord_connected
    global RPC
    global details
    # Call the function to attempt to connect to Discord
    connectDiscord()
    # Update your status every 15 seconds (to stay within rate limits).
    while True:
        discord_alive = processRunning("discord")
        if not discord_alive:
            print("Discord process not found, closing socket and reconnecting in 15 seconds...", end='\n')
            RPC.close()
            discord_connected = False
            sleep(15)
            connectDiscord()
        tidal_alive = processRunning("tidal")
        if tidal_alive:
            try:
                #print("Debug: TIDAL is running!", end='\n')
                # Attempt to get info from TIDAL
                details = get_tidal_info()
                if details[0] and details[1]:
                    #print("Debug: TIDAL is playing, successfully retrieved track info...", end='\n')
                    tidal_paused = False
                else:
                    #print("Debug: Unable to get song information.", end='\n')
                    discord_alive = processRunning("discord")
                    if discord_alive and discord_connected:
                        pauseRPC()
                    elif discord_alive and not discord_connected:
                        discord_connected = False
                        clear()
                        print("Discord connection lost, attempting to reconnect.", end='\n')
                        connectDiscord()
                        print("Discord connection restored! Updating on the next cycle.", end='\n')
                    else:
                        print("Discord process not found or not connected.", end='\n')
                        tidal_paused = True
            # A catch all exception. The program should continue attempting to find the TIDAL window
            # and maintain its Discord connection under all circumstances.
            except Exception:
                print("Unable to get song information.", end='\n')
                discord_alive = processRunning("discord")
                if discord_alive and discord_connected:
                    pauseRPC()
                else:
                    print("Discord process not found or not connected.", end='\n')
                    tidal_paused = True
        else:
            #print("Debug: Tidal process not found.", end='\n')
            RPC.close()
            discord_connected = False
            tidal_paused = True
            waitForTidal()
            connectDiscord()
            print("Discord connection restored! Updating on the next cycle.", end='\n')
        if not tidal_paused:
            try:
                discord_alive = processRunning("discord")
                if discord_alive and discord_connected:
                    #print("Debug: Attempting to update Rich presence...", end='\n')
                    updateRPC()
                else:
                    discord_connected = False
                    clear()
                    print("Discord connection lost, attempting to reconnect.", end='\n')
                    connectDiscord()
                    print("Discord process now found! Updating on the next cycle.", end='\n')
            except Exception:
                discord_connected = False
                clear()
                print("Discord connection lost or Discord closed, attempting to reconnect.", end='\n')
                connectDiscord()
                print("Discord process now found! Updating on the next cycle.", end='\n')
        try:
            # MUST be no less than 15 seconds to remain within Discord rate limits.
            print("Sleeping for 15 seconds. Hit Exit if you want to terminate the script.", end='\n')
            sleep(15)
            clear()
            window['-ML-'].update('')
        # Terminate properly on user Exit
        except KeyboardInterrupt:
            quit(0)

if __name__ == '__main__':
    the_gui()
    quit(0)
