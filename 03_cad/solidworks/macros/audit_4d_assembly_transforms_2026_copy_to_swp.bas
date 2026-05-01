' Copy this module into a SolidWorks-created .swp macro. Do not run this .bas directly.
' SolidWorks 2026 internal VBA macro for Stage 4E transform and bounding box audit.
'
' Run inside SolidWorks 2026 from a SolidWorks-created .swp macro. This macro
' does not move components, does not save assembly changes, and does not modify
' the model. It only reads component transforms and bounding boxes.

Option Explicit

Const PROJECT_ROOT As String = "C:\Users\29868\Desktop\浣滀笟\鍖荤敤鏈哄櫒浜篭blood-sorting-robot-industrial-design"
Const ASM_PATH As String = PROJECT_ROOT & "\03_cad\solidworks\assembly\rough_layout_4d_corrected_2026_v1.SLDASM"
Const OUTPUT_CSV As String = PROJECT_ROOT & "\03_cad\solidworks\assembly\rough_layout_4d_component_transform_audit.csv"

Sub main()
    Dim swApp As Object
    Dim swModel As Object
    Dim swAssembly As Object
    Dim errors As Long
    Dim warnings As Long
    Dim comps As Variant
    Dim i As Long
    Dim fso As Object
    Dim outFile As Object

    Set swApp = Application.SldWorks
    Set fso = CreateObject("Scripting.FileSystemObject")

    If Not fso.FileExists(ASM_PATH) Then
        Debug.Print "ERROR: assembly not found: " & ASM_PATH
        Exit Sub
    End If

    Set swModel = swApp.ActiveDoc
    If swModel Is Nothing Or LCase(swModel.GetPathName) <> LCase(ASM_PATH) Then
        Set swModel = swApp.OpenDoc6(ASM_PATH, 2, 32, "", errors, warnings)
    End If
    If swModel Is Nothing Then
        Debug.Print "ERROR: failed to open assembly. errors=" & errors & " warnings=" & warnings
        Exit Sub
    End If

    Set swAssembly = swModel
    comps = swAssembly.GetComponents(False)

    Set outFile = fso.CreateTextFile(OUTPUT_CSV, True, True)
    outFile.WriteLine "component_name,referenced_file,is_suppressed,is_fixed,actual_x_m,actual_y_m,actual_z_m,actual_x_mm,actual_y_mm,actual_z_mm,bbox_min_x_mm,bbox_min_y_mm,bbox_min_z_mm,bbox_max_x_mm,bbox_max_y_mm,bbox_max_z_mm,bbox_size_x_mm,bbox_size_y_mm,bbox_size_z_mm,longest_bbox_axis,notes"

    If IsEmpty(comps) Then
        Debug.Print "No components found."
    Else
        For i = LBound(comps) To UBound(comps)
            WriteComponentAudit outFile, comps(i)
        Next i
    End If

    outFile.Close
    Debug.Print "4E transform audit CSV written: " & OUTPUT_CSV
    Debug.Print "No assembly changes were saved."
End Sub

Sub WriteComponentAudit(ByRef outFile As Object, ByRef comp As Object)
    Dim compName As String
    Dim refPath As String
    Dim isSuppressed As String
    Dim isFixed As String
    Dim tr As Object
    Dim data As Variant
    Dim xM As Variant, yM As Variant, zM As Variant
    Dim box As Variant
    Dim minX As Variant, minY As Variant, minZ As Variant
    Dim maxX As Variant, maxY As Variant, maxZ As Variant
    Dim sx As Variant, sy As Variant, sz As Variant
    Dim axis As String
    Dim notes As String

    notes = ""
    On Error Resume Next
    compName = comp.GetName2
    refPath = comp.GetPathName
    isSuppressed = CStr(comp.IsSuppressed)
    isFixed = CStr(comp.IsFixed)
    If Err.Number <> 0 Then
        notes = AppendNote(notes, "basic component property read error " & Err.Number)
        Err.Clear
    End If
    On Error GoTo 0

    xM = "": yM = "": zM = ""
    On Error Resume Next
    Set tr = comp.Transform2
    If tr Is Nothing Then
        notes = AppendNote(notes, "Transform2 unavailable")
    Else
        data = tr.ArrayData
        xM = CDbl(data(9))
        yM = CDbl(data(10))
        zM = CDbl(data(11))
    End If
    If Err.Number <> 0 Then
        notes = AppendNote(notes, "transform read error " & Err.Number)
        Err.Clear
    End If
    On Error GoTo 0

    minX = "": minY = "": minZ = ""
    maxX = "": maxY = "": maxZ = ""
    sx = "": sy = "": sz = ""
    axis = ""
    On Error Resume Next
    box = comp.GetBox(False, False)
    If IsEmpty(box) Then
        notes = AppendNote(notes, "bounding box unavailable")
    Else
        minX = CDbl(box(0)) * 1000#
        minY = CDbl(box(1)) * 1000#
        minZ = CDbl(box(2)) * 1000#
        maxX = CDbl(box(3)) * 1000#
        maxY = CDbl(box(4)) * 1000#
        maxZ = CDbl(box(5)) * 1000#
        sx = CDbl(maxX) - CDbl(minX)
        sy = CDbl(maxY) - CDbl(minY)
        sz = CDbl(maxZ) - CDbl(minZ)
        axis = LongestAxis(CDbl(sx), CDbl(sy), CDbl(sz))
    End If
    If Err.Number <> 0 Then
        notes = AppendNote(notes, "bounding box read error " & Err.Number)
        Err.Clear
    End If
    On Error GoTo 0

    outFile.WriteLine Csv(compName) & "," & Csv(refPath) & "," & Csv(isSuppressed) & "," & Csv(isFixed) & "," & _
        Csv(xM) & "," & Csv(yM) & "," & Csv(zM) & "," & Csv(MetersToMm(xM)) & "," & Csv(MetersToMm(yM)) & "," & Csv(MetersToMm(zM)) & "," & _
        Csv(minX) & "," & Csv(minY) & "," & Csv(minZ) & "," & Csv(maxX) & "," & Csv(maxY) & "," & Csv(maxZ) & "," & _
        Csv(sx) & "," & Csv(sy) & "," & Csv(sz) & "," & Csv(axis) & "," & Csv(notes)
End Sub

Function MetersToMm(ByVal value As Variant) As Variant
    If IsNumeric(value) Then
        MetersToMm = CDbl(value) * 1000#
    Else
        MetersToMm = ""
    End If
End Function

Function LongestAxis(ByVal sx As Double, ByVal sy As Double, ByVal sz As Double) As String
    If sx >= sy And sx >= sz Then
        LongestAxis = "X"
    ElseIf sy >= sx And sy >= sz Then
        LongestAxis = "Y"
    Else
        LongestAxis = "Z"
    End If
End Function

Function AppendNote(ByVal currentText As String, ByVal newText As String) As String
    If Len(currentText) = 0 Then
        AppendNote = newText
    Else
        AppendNote = currentText & "; " & newText
    End If
End Function

Function Csv(ByVal value As Variant) As String
    Dim text As String
    text = CStr(value)
    text = Replace(text, """", """""")
    Csv = """" & text & """"
End Function

