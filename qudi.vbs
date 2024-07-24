' Open Windows builtin, Wscript
Set WshShell = CreateObject("WScript.Shell")

' Run Qudi in silent mode (activate Python environment first)
WshShell.Run "cmd /K env\Scripts\activate & env\Scripts\qudi.exe", 0

' Hide script command line
Set WshShell = Nothing
