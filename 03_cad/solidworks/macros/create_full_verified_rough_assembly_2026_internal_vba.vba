' SolidWorks 2026 internal VBA macro skeleton for the full rough assembly.
'
' This macro uses the same insertion routine as the minimum verified macro.
' It is intended to be run only after the minimum 6-component macro succeeds.
' It still performs coordinate rough placement only: no complex mates, no hole
' selection, and no mounting-face inference.

Option Explicit

Const PROJECT_ROOT As String = "C:\Users\29868\Desktop\作业\医用机器人\blood-sorting-robot-industrial-design"
Const ASM_TEMPLATE As String = "C:\ProgramData\SOLIDWORKS\SOLIDWORKS 2026\templates\gb_assembly.asmdot"
Const OUTPUT_ASM As String = PROJECT_ROOT & "\03_cad\solidworks\assembly\full_verified_internal_macro_rough_layout_2026_v1.SLDASM"

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

    InsertOne swModel, assemblyTitle, "base_plate", PROJECT_ROOT & "\03_cad\solidworks\converted_native\parts\base_plate_1100x900x15.SLDPRT", 0#, 0#, -7.5
    InsertOne swModel, assemblyTitle, "left_y_axis_module", PROJECT_ROOT & "\03_cad\solidworks\converted_native\parts\MISUMI_MSA628_Y_axis_L750_double_shaft_B1_v1.SLDASM", -360#, 0#, 35#
    InsertOne swModel, assemblyTitle, "right_y_axis_module", PROJECT_ROOT & "\03_cad\solidworks\converted_native\parts\MISUMI_MSA628_Y_axis_L750_double_shaft_B1_v1.SLDASM", 360#, 0#, 35#
    InsertOne swModel, assemblyTitle, "x_axis_module_on_gantry", PROJECT_ROOT & "\03_cad\solidworks\converted_native\parts\MISUMI_MSA628_Y_axis_L750_double_shaft_B1_v1.SLDASM", 0#, 0#, 260#
    InsertOne swModel, assemblyTitle, "z_axis_module", PROJECT_ROOT & "\03_cad\solidworks\converted_native\parts\MISUMI_LS10_Z_axis_140stroke_T42_ball_screw_v1.SLDASM", 0#, 0#, 220#
    InsertOne swModel, assemblyTitle, "electric_parallel_gripper", PROJECT_ROOT & "\03_cad\solidworks\converted_native\assemblies\SMC_LEHF20_2finger_parallel_gripper_24stroke_v1.SLDASM", 0#, 0#, 120#
    InsertOne swModel, assemblyTitle, "input_mixed_tube_rack_4x6", PROJECT_ROOT & "\03_cad\solidworks\converted_native\parts\input_mixed_tube_rack_4x6.SLDASM", -250#, 250#, 17.5
    InsertOne swModel, assemblyTitle, "category_A_output_bin_2x3", PROJECT_ROOT & "\03_cad\solidworks\converted_native\parts\category_A_output_bin_2x3.SLDASM", 180#, -170#, 17.5
    InsertOne swModel, assemblyTitle, "category_B_output_bin_2x3", PROJECT_ROOT & "\03_cad\solidworks\converted_native\parts\category_A_output_bin_2x3.SLDASM", 320#, -170#, 17.5
    InsertOne swModel, assemblyTitle, "category_C_output_bin_2x3", PROJECT_ROOT & "\03_cad\solidworks\converted_native\parts\category_A_output_bin_2x3.SLDASM", 180#, -290#, 17.5
    InsertOne swModel, assemblyTitle, "category_D_output_bin_2x3", PROJECT_ROOT & "\03_cad\solidworks\converted_native\parts\category_A_output_bin_2x3.SLDASM", 320#, -290#, 17.5
    InsertOne swModel, assemblyTitle, "manual_review_bin_2x3", PROJECT_ROOT & "\03_cad\solidworks\converted_native\parts\category_A_output_bin_2x3.SLDASM", -250#, -300#, 17.5
    InsertOne swModel, assemblyTitle, "barcode_scanner", PROJECT_ROOT & "\03_cad\solidworks\converted_native\parts\Cognex_DataMan80_USB_fixed_barcode_reader_v1.SLDPRT", 80#, 160#, 80#
    InsertOne swModel, assemblyTitle, "photoelectric_sensor", PROJECT_ROOT & "\03_cad\solidworks\converted_native\parts\Panasonic_CX421J_diffuse_photoelectric_sensor_v1.SLDPRT", 20#, 80#, 60#
    InsertOne swModel, assemblyTitle, "cable_chain_xz", PROJECT_ROOT & "\03_cad\solidworks\converted_native\parts\MISUMI_MHPKS204_cable_carrier_R38_18links_v1.SLDASM", 120#, 0#, 240#
    InsertOne swModel, assemblyTitle, "emergency_stop_placeholder", PROJECT_ROOT & "\03_cad\standard_parts\placeholders\safety\emergency_stop_visual_placeholder_v1.sldprt", -500#, -420#, 35#
    ' control_box_placeholder has no confirmed native path in native_file_mapping.csv yet.
    Debug.Print "SKIP control_box_placeholder: native path still needs manual conversion or confirmation."
    skippedCount = skippedCount + 1
    InsertOne swModel, assemblyTitle, "y_axis_sync_mechanism", PROJECT_ROOT & "\03_cad\solidworks\converted_native\parts\y_axis_sync_shaft_placeholder.SLDPRT", 0#, -350#, 55#

    finalCount = ComponentCount(swModel)
    Debug.Print "Attempted count: " & attemptedCount
    Debug.Print "Inserted count: " & insertedCount
    Debug.Print "Failed count: " & failedCount
    Debug.Print "Skipped count: " & skippedCount
    Debug.Print "Final component count: " & finalCount

    If finalCount > 0 Then
        swModel.SaveAs3 OUTPUT_ASM, 0, 0
        Debug.Print "Saved full rough assembly: " & OUTPUT_ASM
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
        ApplyTranslation insertedComponent, xMm / 1000#, yMm / 1000#, zMm / 1000#
    End If

    afterCount = ComponentCount(swAssemblyModel)
    If afterCount > beforeCount Then
        insertedCount = insertedCount + 1
        Debug.Print "INSERTED " & componentName & ": count " & beforeCount & " -> " & afterCount
    Else
        failedCount = failedCount + 1
        Debug.Print "FAIL " & componentName & ": count did not increase; count " & beforeCount & " -> " & afterCount
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
