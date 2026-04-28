# Vendor Download List v1

This list records where real industrial CAD should be obtained in Stage 2. No CAD has been downloaded in Stage 1. If a supplier website requires login, registration, captcha, model configuration, or manual format selection, the status must remain `manual_download_required`.

| Category | Supplier Candidates | CAD Source | Preferred Format | Likely Manual Action | Stage 2 Action |
|---|---|---|---|---|---|
| X/Y belt-driven linear modules | MISUMI, THK, HIWIN-equivalent actuator suppliers | https://us.misumi-ec.com/maker/misumi/mech/cad/ | STEP, Parasolid, SolidWorks | Login or configurator selection likely | Select stroke, carriage, motor mount, and download configured CAD |
| Z lead-screw lifting module | MISUMI, THK, HIWIN-equivalent actuator suppliers | MISUMI/THK actuator CAD pages | STEP, Parasolid, SolidWorks | Configurator and login likely | Select lead, stroke, carriage height, and motor orientation |
| Linear guides and sliders | THK, HIWIN, MISUMI | https://www.thk.com/opm/jp/en/linear/thklinearguide/ | STEP, Parasolid | Model and length configuration likely | Download exact rails/blocks or use integrated actuator CAD |
| Motors | Oriental Motor, Leadshine, Delta, MISUMI, 3D ContentCentral | https://www.3dcontentcentral.com/parts/browse/Motors-Stepper.aspx | STEP, SolidWorks | Manual model selection likely | Select by torque-speed curve and shaft dimensions |
| Timing belts and pulleys | MISUMI, Gates, McMaster-Carr | https://www.mcmaster.com/timing-belts/ | STEP for pulleys; belt path often modeled in assembly | Manual size selection | Freeze pitch, width, pulley teeth, bore, and belt length |
| Lead screw and nut | MISUMI, THK, McMaster-Carr | https://www.mcmaster.com/lead-screws/ | STEP, Parasolid | Manual lead and nut selection | Choose trapezoidal or ball screw and download nut/screw CAD |
| Couplings | MISUMI, McMaster-Carr, Ruland-equivalent | https://www.mcmaster.com/shaft-couplings/ | STEP | Bore selection required | Match motor and screw/pulley shaft diameters |
| Bearing blocks | MISUMI, McMaster-Carr, TraceParts | https://www.traceparts.com/en/search/bearing-block | STEP | Manual bore/support style selection | Select support style after shaft layout |
| Electric gripper | SMC, Festo | https://www.smc.com.cn/products/pickup/en-hk/electric_actuator/electric-grippers/ and https://ftp.festo.com/Public/PNEUMATIC/SOFTWARE_SERVICE/Documentation/2025/EN_US/EHPS_ENUS.PDF | STEP, SolidWorks | Supplier CAD portal or manual configuration likely | Select stroke/force class and download real CAD |
| Cable drag chain | igus, MISUMI, McMaster-Carr | https://www.igus.eu/info/echain-3d-cad | STEP, IGES | Chain configurator likely | Define cable bundle, bend radius, chain length |
| Limit switches | Omron, Panasonic, MISUMI, TraceParts | https://www.traceparts.com/en/search/limit-switch | STEP, SolidWorks | Manual switch choice | Select home/limit switch and target bracket interfaces |
| Photoelectric sensor | SICK, Keyence, Omron, TraceParts | https://www.traceparts.com/en/search/photoelectric-sensor | STEP, SolidWorks | Manual sensing mode choice | Select sensing distance and mounting angle |
| Barcode scanner | Keyence, SICK, Datalogic, TraceParts | Vendor CAD or TraceParts | STEP, SolidWorks | Manual model choice, vendor account possible | Define scan location and interface envelope |
| Emergency stop | Schneider, Siemens, IDEC, TraceParts | https://www.traceparts.com/en/search/rs-group-electrical-automation-cables-switches-push-button-switches-components-emergency-stop-push-buttons | STEP, SolidWorks | Manual contact block selection | Select rated E-stop and panel cutout |
| Control enclosure | Hammond, Rittal, McMaster-Carr, MISUMI | https://www.mcmaster.com/electrical-enclosures/ | STEP | Manual size choice | Estimate electronics volume and pick enclosure |
| Aluminum profiles and brackets | MISUMI, McMaster-Carr, Bosch Rexroth-equivalent | MISUMI CAD and https://www.mcmaster.com/t-slotted-framing-brackets/ | STEP | Manual profile family and length selection | Freeze slot standard and cut list |
| Fasteners | MISUMI, McMaster-Carr | https://www.mcmaster.com/socket-head-screws/ | STEP optional | Size selection after drawings | Build release fastener BOM after hole standards |
| Transparent PC guard hardware | McMaster-Carr, MISUMI, local sheet supplier | https://www.mcmaster.com/polycarbonate-sheets/ | STEP for hardware; drawings for panels | Panel thickness and hardware selection | Define guard panels, hinges, handles, latches |

## Download Rule

Stage 2 may place real supplier CAD under `03_cad/standard_parts/`. Until the actual file is obtained, the status remains `manual_download_required`, `not_started`, or `fallback_needed`; do not mark anything as `downloaded`.
