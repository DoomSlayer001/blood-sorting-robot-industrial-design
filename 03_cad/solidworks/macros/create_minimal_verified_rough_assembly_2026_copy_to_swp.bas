' SolidWorks 2026 internal VBA macro module for copy/paste into a .swp macro.
' SolidWorks cannot directly run this .bas text file. Use Tools > Macro > New
' to create a .swp macro, open the VBA editor, then paste this module content
' into the generated macro module.
'
' Source preserved in:
' create_minimal_verified_rough_assembly_2026_internal_vba.vba
'
' This copy-to-swp module is intentionally plain text so it can be reviewed,
' copied, or imported into the SolidWorks VBA editor.
'
' SolidWorks 2026 internal VBA macro.
' Purpose: create a minimum verified rough assembly using the insertion flow
' proven by a user-recorded internal SolidWorks macro.
'
' Run inside SolidWorks 2026:
' Tools > Macro > Run > create_minimal_verified_rough_assembly_2026_internal_vba.vba
'
' This macro does not add complex mates, does not select holes, and does not
' infer mounting faces. Coordinates are converted from mm to meters.

Option Explicit

Const PROJECT_ROOT As String = "C:\Users\29868\Desktop\作业\医用机器人\blood-sorting-robot-industrial-design"
Const ASM_TEMPLATE As String = "C:\ProgramData\SOLIDWORKS\SOLIDWORKS 2026\templates\gb_assembly.asmdot"
Const OUTPUT_ASM As String = PROJECT_ROOT & "\03_cad\solidworks\assembly\minimal_verified_internal_macro_rough_layout_2026_v1.SLDASM"

Dim swApp As Object
Dim attemptedCount As Long
Dim insertedCount As Long
Dim failedCount As Long

Sub main()
    Dim swModel As Object
    Dim assemblyTitle As String
    Dim finalCount As Long

    Set swApp = Application.SldWorks
    attemptedCount = 0
    insertedCount = 0
    failedCount = 0

    Debug.Print "Creating minimum verified rough assembly with SolidWorks internal VBA."
    Set swModel = swApp.NewDocument(ASM_TEMPLATE, 0, 0, 0)
    If swModel Is Nothing Then
        Debug.Print "ERROR: failed to create assembly from template: " & ASM_TEMPLATE
        Exit Sub
    End If

    assemblyTitle = swModel.GetTitle

    InsertOne swModel, assemblyTitle, "base_plate", _
        PROJECT_ROOT & "\03_cad\solidworks\converted_native\parts\base_plate_1100x900x15.SLDPRT", _
        0#, 0#, -7.5

    InsertOne swModel, assemblyTitle, "input_mixed_tube_rack_4x6", _
        PROJECT_ROOT & "\03_cad\solidworks\converted_native\parts\input_mixed_tube_rack_4x6.SLDASM", _
        -250#, 250#, 17.5

    InsertOne swModel, assemblyTitle, "category_A_output_bin_2x3", _
        PROJECT_ROOT & "\03_cad\solidworks\converted_native\parts\category_A_output_bin_2x3.SLDASM", _
        180#, -170#, 17.5

    InsertOne swModel, assemblyTitle, "electric_parallel_gripper", _
        PROJECT_ROOT & "\03_cad\solidworks\converted_native\assemblies\SMC_LEHF20_2finger_parallel_gripper_24stroke_v1.SLDASM", _
        0#, 0#, 120#

    InsertOne swModel, assemblyTitle, "barcode_scanner", _
        PROJECT_ROOT & "\03_cad\solidworks\converted_native\parts\Cognex_DataMan80_USB_fixed_barcode_reader_v1.SLDPRT", _
        80#, 160#, 80#

    InsertOne swModel, assemblyTitle, "photoelectric_sensor", _
        PROJECT_ROOT & "\03_cad\solidworks\converted_native\parts\Panasonic_CX421J_diffuse_photoelectric_sensor_v1.SLDPRT", _
        20#, 80#, 60#

    finalCount = ComponentCount(swModel)
    Debug.Print "Attempted count: " & attemptedCount
    Debug.Print "Inserted count: " & insertedCount
    Debug.Print "Failed count: " & failedCount
    Debug.Print "Final component count: " & finalCount

    If finalCount > 0 Then
        swModel.SaveAs3 OUTPUT_ASM, 0, 0
        Debug.Print "Saved minimum rough assembly: " & OUTPUT_ASM
    Else
        Debug.Print "ERROR: final component count is zero; assembly was not a valid result."
    End If
End Sub

Sub InsertOne(ByRef swAssemblyModel As Object, ByVal assemblyTitle As String, ByVal componentName As String, ByVal nativePath As String, ByVal xMm As Double, ByVal yMm As Double, ByVal zMm As Double)
    Dim fso As Object
    Dim openedDoc As Object
    Dim insertedComponent As Object
    Dim errors As Long
    Dim warnings As Long
    Dim beforeCount As Long
    Dim afterCount As Long
    Dim xM As Double
    Dim yM As Double
    Dim zM As Double
    Dim docType As Long

    attemptedCount = attemptedCount + 1
    Set fso = CreateObject("Scripting.FileSystemObject")
    If Not fso.FileExists(nativePath) Then
        Debug.Print "FAIL " & componentName & ": file not found: " & nativePath
        failedCount = failedCount + 1
        Exit Sub
    End If

    docType = NativeDocType(nativePath)
    Set openedDoc = swApp.OpenDoc6(nativePath, docType, 32, "", errors, warnings)
    Debug.Print "OpenDoc6 " & componentName & ": errors=" & errors & " warnings=" & warnings
    swApp.ActivateDoc3 assemblyTitle, True, 0, errors
    Set swAssemblyModel = swApp.ActiveDoc

    beforeCount = ComponentCount(swAssemblyModel)
    xM = xMm / 1000#
    yM = yMm / 1000#
    zM = zMm / 1000#

    Set insertedComponent = swAssemblyModel.AddComponent5(nativePath, 0, "", False, "", xM, yM, zM)
    If Not insertedComponent Is Nothing Then
        ApplyTranslation insertedComponent, xM, yM, zM
    Else
        Debug.Print "WARN " & componentName & ": AddComponent5 returned Nothing."
    End If

    afterCount = ComponentCount(swAssemblyModel)
    If afterCount > beforeCount Then
        insertedCount = insertedCount + 1
        Debug.Print "INSERTED " & componentName & ": count " & beforeCount & " -> " & afterCount
    Else
        failedCount = failedCount + 1
        Debug.Print "FAIL " & componentName & ": component count did not increase; count " & beforeCount & " -> " & afterCount
    End If

    On Error Resume Next
    If Not openedDoc Is Nothing Then swApp.CloseDoc openedDoc.GetTitle
    swApp.ActivateDoc3 assemblyTitle, True, 0, errors
    On Error GoTo 0
End Sub

Sub ApplyTranslation(ByRef swComponent As Object, ByVal xM As Double, ByVal yM As Double, ByVal zM As Double)
    Dim swMathUtil As Object
    Dim swTransform As Object
    Dim transformData(15) As Double

    transformData(0) = 1#: transformData(1) = 0#: transformData(2) = 0#
    transformData(3) = 0#: transformData(4) = 1#: transformData(5) = 0#
    transformData(6) = 0#: transformData(7) = 0#: transformData(8) = 1#
    transformData(9) = xM
    transformData(10) = yM
    transformData(11) = zM
    transformData(12) = 1#
    transformData(13) = 0#
    transformData(14) = 0#
    transformData(15) = 0#

    Set swMathUtil = swApp.GetMathUtility
    Set swTransform = swMathUtil.CreateTransform(transformData)
    swComponent.SetTransformAndSolve2 swTransform
End Sub

Function ComponentCount(ByRef swAssemblyModel As Object) As Long
    Dim comps As Variant
    On Error Resume Next
    comps = swAssemblyModel.GetComponents(False)
    If IsEmpty(comps) Then
        ComponentCount = 0
    Else
        ComponentCount = UBound(comps) - LBound(comps) + 1
    End If
    If Err.Number <> 0 Then
        Err.Clear
        ComponentCount = 0
    End If
    On Error GoTo 0
End Function

Function NativeDocType(ByVal filePath As String) As Long
    Dim lowerPath As String
    lowerPath = LCase(filePath)
    If Right(lowerPath, 7) = ".sldasm" Then
        NativeDocType = 2
    Else
        NativeDocType = 1
    End If
End Function
