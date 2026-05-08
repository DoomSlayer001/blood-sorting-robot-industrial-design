# Pick Place Task State Machine v1

The robot does not use a camera in this version. Pick tasks are generated from the internal tube occupancy input table.

| state | input | output | failure condition | next state |
|---|---|---|---|---|
| IDLE | system ready | wait for input table load | system not initialized | LOAD_INPUT_TABLE |
| LOAD_INPUT_TABLE | tube occupancy CSV/table | validated occupancy model | missing required fields | SELECT_NEXT_TUBE |
| SELECT_NEXT_TUBE | occupancy model, priorities | selected candidate tube | no available tubes | COMPLETE |
| CHECK_CATEGORY_AVAILABLE | selected tube category, output box state | route decision | category output full | WAIT_OUTPUT_BOX_SERVICE or SELECT_NEXT_TUBE |
| MOVE_TO_PICK | source slot pose | X/Y safe move command | collision envelope fail | HANDLE_EXCEPTION |
| DESCEND_TO_PICK | z_pick_mm | Z descend command | Z soft limit fail | HANDLE_EXCEPTION |
| GRIP_TUBE | gripper close command | tube grasped state | grip confirmation fail | HANDLE_EXCEPTION |
| LIFT_TUBE | safe Z height | tube lifted state | Z motion fail | HANDLE_EXCEPTION |
| MOVE_TO_PLACE | target slot pose | X/Y place command | collision envelope fail | HANDLE_EXCEPTION |
| DESCEND_TO_PLACE | target z_place_mm | Z descend command | Z soft limit fail | HANDLE_EXCEPTION |
| RELEASE_TUBE | gripper open command | tube released state | release confirmation fail | HANDLE_EXCEPTION |
| UPDATE_TABLE | completed task | source empty, target occupied | table write fail | SELECT_NEXT_TUBE |
| HANDLE_EXCEPTION | abnormal tube or task failure | manual review task if abnormal | normal tube blocked by full output category | UPDATE_TABLE or WAIT_OUTPUT_BOX_SERVICE |
| WAIT_OUTPUT_BOX_SERVICE | full output category | category paused | service timeout | SELECT_NEXT_TUBE |
| COMPLETE | no remaining active tasks | batch complete | none | IDLE |

Normal tubes are not sent to manual review merely because their output category is full. That category pauses while other categories continue.

