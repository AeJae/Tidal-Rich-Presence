# Python-based rich presence for TIDAL.

Neither I nor this program are affiliated with either TIDAL or Discord in any way.

TIDAL, the wordmark and logo are registered trademarks of TIDAL Music AS.

## Set-Up

This project provides a simple and safe method of getting basic TIDAL rich presence on your profile, featuring the song name and artist.

1. Run the command `python -m pip install pypresence`, as this module is needed to interact with Discord.
2. If you wish to use the GUI variant, you will additionally need `python -m pip install PySimpleGUI` and `python -m pip install psgtray`
3. Download this project's [latest release](https://github.com/AeJae/Tidal-Rich-Presence/releases/latest) (.zip).
4. Head to the [Discord developer portal](https://discord.com/developers/docs/intro).
5. Select applications.
6. Sign in to Discord.
7. Click "New Application".
8. Under "General Information", name your application `TIDAL`.
9. Under "Rich Presence", add the two images contained in the downloaded zip, `hra` and `tidallogo`. Do __NOT__ change the file names.
10. Ensure the images have saved.
11. Head back to "General Information", and copy your "Application ID" into the `client_id` variable in `Tidal RPC.py`.

You're all set! Simply run `Tidal RPC.py`, and you should be able to see the rich presence in action.

This program requires that your TIDAL window remains open. It does not need to be in focus (apps can be on top of it), but it cannot be minimised or in your system tray.

## Running the CLI/GUI variants without any terminal windows
Create a simple .bat file running the CLI or GUI python code with

`@echo off`

`python "pathToFile\Tidal RPC GUI.py"`

Edit the AHK script and point it to your created .bat file.

Compile the AHK script into an executable file (use compression: NONE to avoid angry antivirus software).

<a href="https://imgbb.com/"><img src="https://i.ibb.co/xDJk8Vf/bilde.png" alt="bilde" border="0"></a>

Run the file! Optionally add it to startup by putting a shortcut to it in the startup folder, which you can access by using WindowsKey + R and entering `shell:startup`

Note: the CLI variant may start hidden in the system tray, and can be hidden/restored by doubleclicking the tray icon (looks like a C:> ).

## Media
Rich presence preview:

<img src="https://aejae.github.io/img/tidal-rp-media.png" alt="Project in Action">

GUI preview (set your own themes in PySimpleGUI)

<a href="https://imgbb.com/"><img src="https://i.ibb.co/yh4zM01/bilde.png" alt="GUI version" border="0"></a>

Notifications and minimize to tray preview:

<a href="https://imgbb.com/"><img src="https://i.ibb.co/WtX0zFP/bilde.png" alt="Notification and hide in system tray" border="0"></a>

## A Project by AJSF ([@AeJae](https://github.com/AeJae))
<a href="https://aejae.github.io/" target="_blank"><img src="https://aejae.github.io/img/logo.png" alt="Logo" width="70px"></a>
