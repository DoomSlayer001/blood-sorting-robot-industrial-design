' Copy this module into a SolidWorks-created .swp macro. Do not run this .bas directly.
' SolidWorks 2026 internal VBA macro for Stage 4D corrected rough layout.
' This macro must be copied into or run from a SolidWorks-created .swp macro.
' It performs coordinate rough placement only: no complex mates, no hole
' selection, and no mounting-face inference.
'
' Source table: 03_cad/solidworks/component_placement_table_4d_corrected.csv
' Transform convention: coordinates in mm are converted to meters; rotations use
' Rz * Ry * Rx order.

Option Explicit

Const PROJECT_ROOT As String = "C:\Users\29868\Desktop\作业\医用机器人\blood-sorting-robot-industrial-design"
Const ASM_TEMPLATE As String = "C:\ProgramData\SOLIDWORKS\SOLIDWORKS 2026\templates\gb_assembly.asmdot"
Const OUTPUT_ASM As String = PROJECT_ROOT & "\03_cad\solidworks\assembly\rough_layout_4d_corrected_2026_v1.SLDASM"

Dim swApp As Object
Dim attemptedCount As Long
Dim insertedCount As Long
Dim failedCount As Long
Dim skippedCount As Long
Sub main()
    Dim swModel As Object
    Dim assemblyTitle As String
    Dim finalCount As Long

    Set swApp = Application.SldWorks
    attemptedCount = 0
    insertedCount = 0
    failedCount = 0
    skippedCount = 0

    Set swModel = swApp.NewDocument(ASM_TEMPLATE, 0, 0, 0)
    If swModel Is Nothing Then
        Debug.Print "ERROR: failed to create assembly from template: " & ASM_TEMPLATE
        Exit Sub
    End If
    assemblyTitle = swModel.GetTitle

    InsertOne swModel, assemblyTitle, "base_plate", "base_plate_1100x900x15_v1", PROJECT_ROOT & "\03_cad\solidworks\converted_native\parts\base_plate_1100x900x15.SLDPRT", 0#, 0#, -7.5#, 0#, 0#, 0#
    InsertOne swModel, assemblyTitle, "left_y_axis_module", "left_y_axis_module_v1", PROJECT_ROOT & "\03_cad\solidworks\converted_native\parts\MISUMI_MSA628_Y_axis_L750_double_shaft_B1_v1.SLDASM", -360#, 0#, 35#, 0#, 0#, 90#
    InsertOne swModel, assemblyTitle, "right_y_axis_module", "right_y_axis_module_v1", PROJECT_ROOT & "\03_cad\solidworks\converted_native\parts\MISUMI_MSA628_Y_axis_L750_double_shaft_B1_v1.SLDASM", 360#, 0#, 35#, 0#, 0#, 90#
    InsertOne swModel, assemblyTitle, "x_axis_module_on_gantry", "x_axis_module_on_gantry_v1", PROJECT_ROOT & "\03_cad\solidworks\converted_native\parts\MISUMI_MSA628_Y_axis_L750_double_shaft_B1_v1.SLDASM", 0#, 0#, 260#, 0#, 0#, 0#
    InsertOne swModel, assemblyTitle, "z_axis_module", "z_axis_module_v1", PROJECT_ROOT & "\03_cad\solidworks\converted_native\parts\MISUMI_LS10_Z_axis_140stroke_T42_ball_screw_v1.SLDASM", 0#, 0#, 220#, 0#, 90#, 0#
    InsertOne swModel, assemblyTitle, "electric_parallel_gripper", "electric_parallel_gripper_v1", PROJECT_ROOT & "\03_cad\solidworks\converted_native\assemblies\SMC_LEHF20_2finger_parallel_gripper_24stroke_v1.SLDASM", 0#, 0#, 120#, 0#, 0#, 0#
    InsertOne swModel, assemblyTitle, "input_mixed_tube_rack_4x6", "input_mixed_tube_rack_4x6_v1", PROJECT_ROOT & "\03_cad\solidworks\converted_native\parts\input_mixed_tube_rack_4x6.SLDASM", -250#, 250#, 17.5#, 0#, 0#, 0#
    InsertOne swModel, assemblyTitle, "category_A_output_bin_2x3", "category_A_output_bin_2x3_v1", PROJECT_ROOT & "\03_cad\solidworks\converted_native\parts\category_A_output_bin_2x3.SLDASM", 180#, -170#, 17.5#, 0#, 0#, 0#
    InsertOne swModel, assemblyTitle, "category_B_output_bin_2x3", "category_B_output_bin_2x3_v1", PROJECT_ROOT & "\03_cad\solidworks\converted_native\parts\category_A_output_bin_2x3.SLDASM", 320#, -170#, 17.5#, 0#, 0#, 0#
    InsertOne swModel, assemblyTitle, "category_C_output_bin_2x3", "category_C_output_bin_2x3_v1", PROJECT_ROOT & "\03_cad\solidworks\converted_native\parts\category_A_output_bin_2x3.SLDASM", 180#, -290#, 17.5#, 0#, 0#, 0#
    InsertOne swModel, assemblyTitle, "category_D_output_bin_2x3", "category_D_output_bin_2x3_v1", PROJECT_ROOT & "\03_cad\solidworks\converted_native\parts\category_A_output_bin_2x3.SLDASM", 320#, -290#, 17.5#, 0#, 0#, 0#
    InsertOne swModel, assemblyTitle, "manual_review_bin_2x3", "manual_review_bin_2x3_v1", PROJECT_ROOT & "\03_cad\solidworks\converted_native\parts\category_A_output_bin_2x3.SLDASM", -250#, -300#, 17.5#, 0#, 0#, 0#
    InsertOne swModel, assemblyTitle, "scan_station_reference", "scan_station_reference_v1", PROJECT_ROOT & "\03_cad\solidworks\converted_native\parts\scan_station_reference_block.SLDPRT", 80#, 80#, 40#, 0#, 0#, 0#
    InsertOne swModel, assemblyTitle, "barcode_scanner", "barcode_scanner_v1", PROJECT_ROOT & "\03_cad\solidworks\converted_native\parts\Cognex_DataMan80_USB_fixed_barcode_reader_v1.SLDPRT", 80#, 160#, 80#, 0#, 0#, 0#
    InsertOne swModel, assemblyTitle, "photoelectric_sensor", "photoelectric_sensor_v1", PROJECT_ROOT & "\03_cad\solidworks\converted_native\parts\Panasonic_CX421J_diffuse_photoelectric_sensor_v1.SLDPRT", 20#, 80#, 60#, 0#, 0#, 0#

    finalCount = ComponentCount(swModel)
    Debug.Print "Attempted count: " & attemptedCount
    Debug.Print "Inserted count: " & insertedCount
    Debug.Print "Failed count: " & failedCount
    Debug.Print "Skipped count: " & skippedCount
    Debug.Print "Final component count: " & finalCount

    If finalCount > 0 Then
        swModel.SaveAs3 OUTPUT_ASM, 0, 0
        Debug.Print "Saved 4D corrected rough assembly: " & OUTPUT_ASM
    Else
        Debug.Print "ERROR: final component count is zero; assembly was not a valid result."
    End If
End Sub

Sub InsertOne(ByRef swAssemblyModel As Object, ByVal assemblyTitle As String, ByVal componentName As String, ByVal instanceName As String, ByVal nativePath As String, ByVal xMm As Double, ByVal yMm As Double, ByVal zMm As Double, ByVal rxDeg As Double, ByVal ryDeg As Double, ByVal rzDeg As Double)
    Dim fso As Object
    Dim openedDoc As Object
    Dim insertedComponent As Object
    Dim errors As Long
    Dim warnings As Long
    Dim beforeCount As Long
    Dim afterCount As Long

    attemptedCount = attemptedCount + 1
    Set fso = CreateObject("Scripting.FileSystemObject")
    If Not fso.FileExists(nativePath) Then
        Debug.Print "FAIL " & componentName & ": file not found: " & nativePath
        failedCount = failedCount + 1
        Exit Sub
    End If

    Set openedDoc = swApp.OpenDoc6(nativePath, NativeDocType(nativePath), 32, "", errors, warnings)
    Debug.Print "OpenDoc6 " & componentName & ": errors=" & errors & " warnings=" & warnings
    swApp.ActivateDoc3 assemblyTitle, True, 0, errors
    Set swAssemblyModel = swApp.ActiveDoc

    beforeCount = ComponentCount(swAssemblyModel)
    Set insertedComponent = swAssemblyModel.AddComponent5(nativePath, 0, "", False, "", xMm / 1000#, yMm / 1000#, zMm / 1000#)
    If Not insertedComponent Is Nothing Then
        On Error Resume Next
        insertedComponent.Name2 = instanceName
        On Error GoTo 0
        insertedComponent.SetTransformAndSolve2 MakeTransform(xMm, yMm, zMm, rxDeg, ryDeg, rzDeg)
    Else
        Debug.Print "WARN " & componentName & ": AddComponent5 returned Nothing."
    End If

    afterCount = ComponentCount(swAssemblyModel)
    If afterCount > beforeCount Then
        insertedCount = insertedCount + 1
        Debug.Print "INSERTED " & componentName & " as " & instanceName & ": count " & beforeCount & " -> " & afterCount
    Else
        failedCount = failedCount + 1
        Debug.Print "FAIL " & componentName & ": count did not increase; count " & beforeCount & " -> " & afterCount
    End If

    On Error Resume Next
    If Not openedDoc Is Nothing Then swApp.CloseDoc openedDoc.GetTitle
    swApp.ActivateDoc3 assemblyTitle, True, 0, errors
    On Error GoTo 0
End Sub

Function MakeTransform(ByVal xMm As Double, ByVal yMm As Double, ByVal zMm As Double, ByVal rxDeg As Double, ByVal ryDeg As Double, ByVal rzDeg As Double) As Object
    Dim swMathUtil As Object
    Dim transformData(15) As Double
    Dim rx As Double, ry As Double, rz As Double
    Dim cx As Double, sx As Double, cy As Double, sy As Double, cz As Double, sz As Double
    Dim pi As Double

    pi = 4# * Atn(1#)
    rx = rxDeg * pi / 180#
    ry = ryDeg * pi / 180#
    rz = rzDeg * pi / 180#
    cx = Cos(rx): sx = Sin(rx)
    cy = Cos(ry): sy = Sin(ry)
    cz = Cos(rz): sz = Sin(rz)

    ' Rotation order: Rz * Ry * Rx.
    transformData(0) = cz * cy
    transformData(1) = cz * sy * sx - sz * cx
    transformData(2) = cz * sy * cx + sz * sx
    transformData(3) = sz * cy
    transformData(4) = sz * sy * sx + cz * cx
    transformData(5) = sz * sy * cx - cz * sx
    transformData(6) = -sy
    transformData(7) = cy * sx
    transformData(8) = cy * cx

    transformData(9) = xMm / 1000#
    transformData(10) = yMm / 1000#
    transformData(11) = zMm / 1000#
    transformData(12) = 1#
    transformData(13) = 0#
    transformData(14) = 0#
    transformData(15) = 0#

    Set swMathUtil = swApp.GetMathUtility
    Set MakeTransform = swMathUtil.CreateTransform(transformData)
End Function

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
