' Recorded SolidWorks internal VBA insertion flow captured from the user's
' successful base_plate test.
'
' Note:
' The full raw exported macro text was not included in the chat context. This
' file preserves the key recorded calls exactly as supplied and wraps them in a
' readable reference macro. It is kept for analysis and traceability; use
' create_minimal_verified_rough_assembly_2026_internal_vba.vba for the runnable
' minimum assembly macro.
'
' Critical recorded insertion flow:
' - OpenDoc6(native_file, 1, 32, "", errors, warnings)
' - ActivateDoc3(AssemblyTitle, True, 0, errors)
' - Part.AddComponent5(native_file, 0, "", False, "", x_m, y_m, z_m)
' - swInsertedComponent.SetTransformAndSolve2(swTransform)
' - SaveAs3(output_sldasm, 0, 0)

Option Explicit

Sub main()
    Dim swApp As Object
    Dim swModel As Object
    Dim swAssembly As Object
    Dim swInsertedComponent As Object
    Dim swMathUtil As Object
    Dim swTransform As Object
    Dim errors As Long
    Dim warnings As Long
    Dim AssemblyTitle As String
    Dim native_file As String
    Dim output_sldasm As String
    Dim x_m As Double
    Dim y_m As Double
    Dim z_m As Double
    Dim transformData(15) As Double

    Set swApp = Application.SldWorks

    native_file = "C:\Users\29868\Desktop\作业\医用机器人\blood-sorting-robot-industrial-design\03_cad\solidworks\converted_native\parts\base_plate_1100x900x15.SLDPRT"
    output_sldasm = "C:\Users\29868\Desktop\作业\医用机器人\blood-sorting-robot-industrial-design\03_cad\solidworks\assembly\recorded_insert_baseplate_reference.SLDASM"

    Set swModel = swApp.NewDocument("C:\ProgramData\SOLIDWORKS\SOLIDWORKS 2026\templates\gb_assembly.asmdot", 0, 0, 0)
    If swModel Is Nothing Then
        Debug.Print "Failed to create assembly document."
        Exit Sub
    End If

    AssemblyTitle = swModel.GetTitle
    Set swAssembly = swModel

    ' Recorded pattern: open native CAD first, then activate the assembly again.
    Set swModel = swApp.OpenDoc6(native_file, 1, 32, "", errors, warnings)
    Debug.Print "OpenDoc6 errors=" & errors & " warnings=" & warnings
    swApp.ActivateDoc3 AssemblyTitle, True, 0, errors
    Set swModel = swApp.ActiveDoc
    Set swAssembly = swModel

    x_m = 0#
    y_m = 0#
    z_m = -0.0075

    Set swInsertedComponent = swAssembly.AddComponent5(native_file, 0, "", False, "", x_m, y_m, z_m)
    If swInsertedComponent Is Nothing Then
        Debug.Print "AddComponent5 returned Nothing."
        Exit Sub
    End If

    Set swMathUtil = swApp.GetMathUtility
    transformData(0) = 1#: transformData(1) = 0#: transformData(2) = 0#
    transformData(3) = 0#: transformData(4) = 1#: transformData(5) = 0#
    transformData(6) = 0#: transformData(7) = 0#: transformData(8) = 1#
    transformData(9) = x_m
    transformData(10) = y_m
    transformData(11) = z_m
    transformData(12) = 1#
    transformData(13) = 0#
    transformData(14) = 0#
    transformData(15) = 0#
    Set swTransform = swMathUtil.CreateTransform(transformData)
    swInsertedComponent.SetTransformAndSolve2 swTransform

    swModel.SaveAs3 output_sldasm, 0, 0
End Sub
