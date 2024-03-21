# Python-based rich presence for TIDAL.

I and this project are NOT affiliated with either TIDAL or Discord.

TIDAL, the wordmark and logo are registered trademarks of TIDAL Music AS.

## Set-Up

This project provides a simple and safe method of getting basic TIDAL rich presence on your profile, featuring the song name and artist.

1. Download the latest release (.zip).
2. Head to the [Discord developer portal](https://discord.com/developers/docs/intro).
3. Select applications.
4. Sign in to Discord.
5. Click "New Application".
6. Under "General Information", name your application `TIDAL`.
7. Under "Rich Presence", add the two images contained in the downloaded zip, `hra` and `tidallogo`. Do __NOT__ change the file names.
8. Ensure the images have saved.
9. Head back to "General Information", and copy your "Application ID" into the `client_id` variable in `Tidal RPC.py`.
10. You're all set!

Simply run `Tidal RPC.py`, and you should be able to see the rich presence in action!

This program requires that your TIDAL window remains open. It does not need to be in focus (apps can be on top of it), but it cannot be minimised or in your system tray.

## A Project by AJSF ([@AeJae](https://github.com/AeJae))
<a href="https://aejae.github.io/" target="_blank"><img src="https://aejae.github.io/img/logo.png" alt="Logo" width="70px"></a>
