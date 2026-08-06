SetWorkingDir, C:\AHK\2nd-keyboard\support_files

#NoEnv
;Menu, Tray, Icon, shell32.dll, 283 ; this changes the tray icon to a little keyboard!
;#Warn All, MsgBox ; had to turn this off because it warns me of a bunch of global/local variable name stuff in the ACC library, which isn't even mine.
SendMode Input 
#SingleInstance force ;only one instance of this script may run at a time!
#MaxHotkeysPerInterval 2000
#WinActivateForce ;https://autohotkey.com/docs/commands/_WinActivateForce.htm
Menu, Tray, Icon, imageres.dll, 251 ;makes the icon into two blue window thingies. would prefer a PS icon if only i knew how to make custom icons.

;Menu, Tray, Icon, C:\My Icon.ico
;https://superuser.com/questions/1102307/change-the-picture-from-the-icon-tray



;-------------------------------------------------------------------------
; HELLO PEOPLES!
; IF YOU ARE NEW TO AUTOHOTKEY, YOU MUST AT LEAST TAKE THE FOLLOWING TUTORIAL:
; https://autohotkey.com/docs/Tutorial.htm
;
; You will need to know some basic scripting to custom tailor most
; of these scripts to your own machine, if you want to use them!
; VERY IMPORTANT NOTE:
; This file works in tandem with ALL_MULTIPLE_KEYBOARD_ASSIGNMENTS.ahk.
; All the functions from HERE are actually CALLED from keyboard shortcuts
; in THAT script. I had to do it this way because of the Stream Deck(s)...
; But you can put your key bindings and functions in the same script if
; you want.
;------------------------------------------------------------------------



PhotoshopExport(baseDir := "", format := "jpeg", forcePath := false)
{
;shout outs to Michael Bunzel for making this whole script for me! YEEAH BOIIIIIII
; baseDir: optional path to save the image if the document is unsaved or forcePath is true
; format: psd, png, jpeg or tif. more are available through the api but I'm lazy
; forcePath: force saving the file to baseDir
;;; #Warn All, MsgBox

	try {
		psApp := ComObjActive("Photoshop.Application")
	}
	catch e {
		MsgBox, % "Unable to connect to running Photoshop instance: " e.message
	}

	if(psApp.Documents.Count < 1)
		throw Exception("There is no open document")

	doc := psApp.activeDocument

	; figure out the directory where the file should be saved
	resultPath := ""
	if(forcePath)
	{
		resultPath := forcePath
	}
	else
	{
		try {
			; will throw an exception if unsaved
			resultPath := doc.path
		}
		catch e {
			if(baseDir != "")
				resultPath := baseDir
			else
				throw Exception("Document is unsaved and no baseDir was provided")
		}
	}
	
	; ensure the directory actually exists
	if(!InStr(FileExist(resultPath),  "D"))
		throw Exception("Unable to export to path " . resultPath)

	; parse the file name and change the extension
	newFileName := ""
	try {
		SplitPath, % doc.fullName, , , , currentBaseFileName
		newFileName := currentBaseFileName . "." . format
	} 
	catch e {
		; if unsaved, name the file ahkexport
		newFileName := "ahkexport." . format
	}

	exportFullPath := resultPath . "\" . newFileName

	formatId := -1
	if(format == "psd")
		formatId := 1
	if(format == "jpeg")
		formatId := 6
	else if(format == "png")
		formatId := 13
	else if(format == "tif")
		formatId := 17
	else
		throw Exception("Invalid file format: " . format)

	; see page 108 for numerous available options: https://www.adobe.com/content/dam/acom/en/devnet/photoshop/pdfs/photoshop-javascript-ref-2020.pdf
	options := ComObjCreate("Photoshop.ExportOptionsSaveForWeb")
	options.Quality := 90
	options.Format := formatId
	options.Optimized := ComObj(0xB, -1)

	try {
		; 2 stands for ExportType SAVEFORWEB
		; doc.export(exportFullPath , 2, options)
		doc.saveAs(2)
	}
	catch e {
		MsgBox, % "Error exporting the image: " e.message
	}
	
	ObjRelease(options)
	ObjRelease(psApp)
}
; end of PhotoshopExport()