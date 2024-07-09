' Open Windows builtin, Wscript
Set WshShell = CreateObject("WScript.Shell")

' Run bat file
WshShell.Run chr(34) & "env\Scripts\qudi.exe" & Chr(34), 0

' Hide script command line
Set WshShell = Nothing
