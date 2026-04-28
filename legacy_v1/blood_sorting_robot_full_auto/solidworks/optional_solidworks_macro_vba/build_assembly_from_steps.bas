Attribute VB_Name = "BuildAssemblyFromSteps"
' Optional macro skeleton for SolidWorks.
' It documents the intended workflow but may need path adjustments per SolidWorks version.

Sub main()
    Dim swApp As Object
    Set swApp = Application.SldWorks
    MsgBox "Open cad/assembly/blood_sorting_robot_assembly.step, then save as SLDASM. " & _
           "Use assembly_reference_coordinates.csv if rebuilding from individual STEP files."
End Sub
