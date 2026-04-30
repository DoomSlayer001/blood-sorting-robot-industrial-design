' Create Rough Assembly v1
' Purpose:
'   Insert components from component_placement_table_v1.csv into a SolidWorks assembly
'   for coordinate-based rough layout review.
'
' Important:
'   This macro is a fallback for running inside SolidWorks if Python COM automation
'   is unavailable or needs version-specific adjustment.
'   It does not add mates, does not select mounting faces, and does not select holes.
'
' Stage 4B-2 note:
'   Python COM direct insertion of STEP files failed on the current SolidWorks 2018
'   environment. The recommended workflow is to first convert STEP/STP files to
'   native SLDPRT/SLDASM files, then insert native files into the rough assembly.
'   The Python script writes:
'     03_cad\solidworks\conversion_reports\step_to_native_conversion_report.csv
'   If native_output_path values exist in that report, use those native files for
'   insertion. If conversion fails, manually open a STEP in SolidWorks, save it as
'   SLDPRT/SLDASM, then update the placement CSV or this macro to use that native
'   path.
'
' Recommended use:
'   1. Open SolidWorks.
'   2. Tools > Macro > New or Edit.
'   3. Paste or load this macro.
'   4. Update REPO_ROOT if the project folder moved.
'   5. Run Main.

Option Explicit

Const REPO_ROOT As String = "C:\Users\29868\Desktop\作业\医用机器人\blood-sorting-robot-industrial-design"
Const PLACEMENT_CSV As String = "\03_cad\solidworks\component_placement_table_v1.csv"
Const OUTPUT_ASM As String = "\03_cad\solidworks\assembly\blood_sorting_robot_rough_layout_v1.SLDASM"
Const CONVERSION_REPORT_CSV As String = "\03_cad\solidworks\conversion_reports\step_to_native_conversion_report.csv"

Sub Main()
    Dim swApp As Object
    Dim swModel As Object
    Dim swAssembly As Object
    Dim templatePath As String

    Set swApp = Application.SldWorks
    swApp.Visible = True

    templatePath = swApp.GetUserPreferenceStringValue(2)
    If Len(templatePath) = 0 Then
        MsgBox "No default assembly template configured. Set a SolidWorks assembly template first."
        Exit Sub
    End If

    Set swModel = swApp.NewDocument(templatePath, 0, 0, 0)
    If swModel Is Nothing Then
        MsgBox "Failed to create new assembly."
        Exit Sub
    End If
    Set swAssembly = swModel

    ' This fallback keeps the simple placement-table workflow. For the native
    ' conversion workflow, replace cadPath below with native_output_path values
    ' from CONVERSION_REPORT_CSV when they are available.
    InsertFromCsv swApp, swModel, swAssembly, REPO_ROOT & PLACEMENT_CSV

    swModel.ForceRebuild3 False
    swModel.SaveAs3 REPO_ROOT & OUTPUT_ASM, 0, 2
    MsgBox "Rough assembly macro completed. Review component orientations manually."
End Sub

Sub InsertFromCsv(swApp As Object, swModel As Object, swAssembly As Object, csvPath As String)
    Dim fso As Object
    Dim stream As Object
    Dim header As String
    Dim line As String
    Dim fields() As String
    Dim cadPath As String
    Dim compName As String
    Dim xMeters As Double, yMeters As Double, zMeters As Double
    Dim comp As Object

    Set fso = CreateObject("Scripting.FileSystemObject")
    If Not fso.FileExists(csvPath) Then
        MsgBox "CSV not found: " & csvPath
        Exit Sub
    End If

    Set stream = fso.OpenTextFile(csvPath, 1, False, -1)
    If Not stream.AtEndOfStream Then header = stream.ReadLine

    Do While Not stream.AtEndOfStream
        line = stream.ReadLine
        fields = ParseCsvLineBasic(line)

        ' Column order:
        ' 0 component_name, 1 part_id, 2 cad_file_path, 3 instance_name,
        ' 4 approx_x_mm, 5 approx_y_mm, 6 approx_z_mm,
        ' 7 rotation_x_deg, 8 rotation_y_deg, 9 rotation_z_deg, ...
        If UBound(fields) >= 14 Then
            cadPath = fields(2)
            compName = fields(3)

            If Len(cadPath) > 0 And UCase(cadPath) <> "TBD" And InStr(cadPath, "*") = 0 Then
                cadPath = REPO_ROOT & "\" & Replace(cadPath, "/", "\")
                If fso.FileExists(cadPath) Then
                    xMeters = CDbl(Val(fields(4))) / 1000#
                    yMeters = CDbl(Val(fields(5))) / 1000#
                    zMeters = CDbl(Val(fields(6))) / 1000#

                    Set comp = swAssembly.AddComponent5(cadPath, 0, "", False, "", xMeters, yMeters, zMeters)
                    If Not comp Is Nothing Then
                        On Error Resume Next
                        comp.Name2 = compName
                        swModel.ClearSelection2 True
                        comp.Select4 False, Nothing, False
                        swAssembly.FixComponent
                        On Error GoTo 0
                    End If
                End If
            End If
        End If
    Loop
    stream.Close
End Sub

Function ParseCsvLineBasic(line As String) As String()
    ' Basic CSV parser for the current placement table. It supports quoted commas
    ' but is intentionally compact; for difficult CSV cases use the Python script.
    Dim result() As String
    Dim current As String
    Dim i As Long
    Dim ch As String
    Dim inQuotes As Boolean
    Dim count As Long

    ReDim result(0)
    count = 0
    current = ""
    inQuotes = False

    For i = 1 To Len(line)
        ch = Mid(line, i, 1)
        If ch = """" Then
            inQuotes = Not inQuotes
        ElseIf ch = "," And Not inQuotes Then
            result(count) = current
            count = count + 1
            ReDim Preserve result(count)
            current = ""
        Else
            current = current & ch
        End If
    Next i
    result(count) = current
    ParseCsvLineBasic = result
End Function
