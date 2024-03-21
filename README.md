# Python-based rich presence for TIDAL.

Neither I nor this program are affiliated with either TIDAL or Discord in any way.

TIDAL, the wordmark and logo are registered trademarks of TIDAL Music AS.

## Set-Up

This project provides a simple and safe method of getting basic TIDAL rich presence on your profile, featuring the song name and artist.

1. Run the command `python -m pip install pypresence`, as this module is needed to interact with Discord.
2. Download this project's [latest release](https://github.com/AeJae/Tidal-Rich-Presence/releases/latest) (.zip).
3. Head to the [Discord developer portal](https://discord.com/developers/docs/intro).
4. Select applications.
5. Sign in to Discord.
6. Click "New Application".
7. Under "General Information", name your application `TIDAL`.
8. Under "Rich Presence", add the two images contained in the downloaded zip, `hra` and `tidallogo`. Do __NOT__ change the file names.
9. Ensure the images have saved.
10. Head back to "General Information", and copy your "Application ID" into the `client_id` variable in `Tidal RPC.py`.

You're all set! Simply run `Tidal RPC.py`, and you should be able to see the rich presence in action.

This program requires that your TIDAL window remains open. It does not need to be in focus (apps can be on top of it), but it cannot be minimised or in your system tray.

## A Project by AJSF ([@AeJae](https://github.com/AeJae))
<a href="https://aejae.github.io/" target="_blank"><img src="https://aejae.github.io/img/logo.png" alt="Logo" width="70px"></a>
