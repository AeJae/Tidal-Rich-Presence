#NoTrayIcon
#Persistent
#SingleInstance Force

global hBatFile

/* Setup Tray icon and add item that will handle
* double click events
*/
Menu Tray, Icon
Menu Tray, Icon, C:\windows\system32\cmd.exe
Menu Tray, Add, Show / Hide TIDAL_RPC, TrayClick
Menu Tray, Add, Close TIDAL_RPC, CloseItem
Menu Tray, Default, Show / Hide TIDAL_RPC

;// Run program or batch file hidden
DetectHiddenWindows On
;// Path to the .bat file running the Python script goes inside the ""
Run "C:\Users\UserX\Downloads\Tidal-Rich-Presence-1.3\RPC.bat",, Hide, PID
WinWait ahk_pid %PID%
hBatFile := WinExist()
DetectHiddenWindows Off
return

TrayClick:
OnTrayClick()
return

;// Show / hide program or batch file on double click
OnTrayClick() {
    if DllCall("IsWindowVisible", "Ptr", hBatFile) {
        WinHide ahk_id %hBatFile%

    } else {
        WinShow ahk_id %hBatFile%
        WinActivate ahk_id %hBatFile%
    }
}

CloseItem() {

       DetectHiddenWindows On
       WinWait ahk_class ConsoleWindowClass
       Process, Close, cmd.exe
       DetectHiddenWindows Off
       ExitApp

}
