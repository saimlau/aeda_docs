# Tool catalog

Every `@tool` registered under [`modulated_system/tools/`](https://github.com/Pengyu-Mo/tidyros_iphone/tree/main/modulated_system/tools). Generated from source by [`scripts/regenerate_tool_catalog.py`](https://github.com/saimlau/aeda_docs/blob/main/scripts/regenerate_tool_catalog.py) — re-run after upstream changes.

**73 tools** across **9 categories**. The category pages (see the nav) group them with prose context; this page is the flat alphabetical view.

| Tool | Category | Summary |
|---|---|---|
| [`activate_workspace`](collection.md#activate-workspace) | `collection` | _(no docstring)_ |
| [`analyze_camera_trajectory_distribution`](data.md#analyze-camera-trajectory-distribution) | `data` | _(no docstring)_ |
| [`analyze_depth_distribution`](data.md#analyze-depth-distribution) | `data` | _(no docstring)_ |
| [`analyze_intrinsics_distribution`](data.md#analyze-intrinsics-distribution) | `data` | _(no docstring)_ |
| [`analyze_language_distribution`](data.md#analyze-language-distribution) | `data` | _(no docstring)_ |
| [`analyze_object_distribution`](data.md#analyze-object-distribution) | `data` | _(no docstring)_ |
| [`analyze_recording`](meta.md#analyze-recording) | `meta` | _(no docstring)_ |
| [`append_memory`](meta.md#append-memory) | `meta` | _(no docstring)_ |
| [`check_reachability`](manipulator.md#check-reachability) | `manipulator` | _(no docstring)_ |
| [`check_stop_condition`](collection.md#check-stop-condition) | `collection` | _(no docstring)_ |
| [`check_target_in_frame`](perception.md#check-target-in-frame) | `perception` | Returns: |
| [`choose_collection_site`](navigation.md#choose-collection-site) | `navigation` | _(no docstring)_ |
| [`compare_distributions`](data.md#compare-distributions) | `data` | _(no docstring)_ |
| [`compute_params_for_base_pose`](trajectory.md#compute-params-for-base-pose) | `trajectory` | _(no docstring)_ |
| [`compute_parking_locations`](trajectory.md#compute-parking-locations) | `trajectory` | _(no docstring)_ |
| [`correlate_dimensions`](data.md#correlate-dimensions) | `data` | _(no docstring)_ |
| [`coverage_report`](data.md#coverage-report) | `data` | _(no docstring)_ |
| [`create_data_spec`](collection.md#create-data-spec) | `collection` | _(no docstring)_ |
| [`define_workspace`](collection.md#define-workspace) | `collection` | _(no docstring)_ |
| [`describe_distribution`](data.md#describe-distribution) | `data` | _(no docstring)_ |
| [`detect_target`](perception.md#detect-target) | `perception` | _(no docstring)_ |
| [`estimate_target_visibility`](perception.md#estimate-target-visibility) | `perception` | Returns a dict with confidence + diagnostic flags. |
| [`evaluate_episode`](collection.md#evaluate-episode) | `collection` | _(no docstring)_ |
| [`execute_trajectory`](trajectory.md#execute-trajectory) | `trajectory` | _(no docstring)_ |
| [`explore_frontier`](navigation.md#explore-frontier) | `navigation` | _(no docstring)_ |
| [`explore_unvisited`](navigation.md#explore-unvisited) | `navigation` | _(no docstring)_ |
| [`find_cluster_target`](perception.md#find-cluster-target) | `perception` | _(no docstring)_ |
| [`find_feasible_params`](trajectory.md#find-feasible-params) | `trajectory` | _(no docstring)_ |
| [`generate_view_trajectory`](trajectory.md#generate-view-trajectory) | `trajectory` | _(no docstring)_ |
| [`get_collection_status`](collection.md#get-collection-status) | `collection` | _(no docstring)_ |
| [`get_executor_state`](meta.md#get-executor-state) | `meta` | _(no docstring)_ |
| [`get_map_snapshot`](meta.md#get-map-snapshot) | `meta` | _(no docstring)_ |
| [`get_trajectory_history`](meta.md#get-trajectory-history) | `meta` | _(no docstring)_ |
| [`identify_objects_vision`](perception.md#identify-objects-vision) | `perception` | _(no docstring)_ |
| [`inject_primer_note`](meta.md#inject-primer-note) | `meta` | _(no docstring)_ |
| [`inspect_dataset`](data.md#inspect-dataset) | `data` | _(no docstring)_ |
| [`list_objects_in_view`](perception.md#list-objects-in-view) | `perception` | _(no docstring)_ |
| [`list_workspaces`](collection.md#list-workspaces) | `collection` | _(no docstring)_ |
| [`lock_base`](manipulator.md#lock-base) | `manipulator` | _(no docstring)_ |
| [`log_event`](collection.md#log-event) | `collection` | _(no docstring)_ |
| [`move_camera_relative`](manipulator.md#move-camera-relative) | `manipulator` | _(no docstring)_ |
| [`move_relative`](navigation.md#move-relative) | `navigation` | _(no docstring)_ |
| [`navigate_to`](navigation.md#navigate-to) | `navigation` | _(no docstring)_ |
| [`notify_supervisor`](meta.md#notify-supervisor) | `meta` | _(no docstring)_ |
| [`plan_arm_motion`](manipulator.md#plan-arm-motion) | `manipulator` | _(no docstring)_ |
| [`prepose_arm_for_view`](manipulator.md#prepose-arm-for-view) | `manipulator` | _(no docstring)_ |
| [`python_exec`](data_analysis.md#python-exec) | `data_analysis` | _(no docstring)_ |
| [`query_log`](meta.md#query-log) | `meta` | _(no docstring)_ |
| [`read_memory`](meta.md#read-memory) | `meta` | _(no docstring)_ |
| [`recover_arm`](manipulator.md#recover-arm) | `manipulator` | _(no docstring)_ |
| [`register_labeled_object`](collection.md#register-labeled-object) | `collection` | _(no docstring)_ |
| [`register_workspace`](collection.md#register-workspace) | `collection` | _(no docstring)_ |
| [`reposition`](navigation.md#reposition) | `navigation` | _(no docstring)_ |
| [`request_next_view`](navigation.md#request-next-view) | `navigation` | _(no docstring)_ |
| [`reset_arm_to_rest`](manipulator.md#reset-arm-to-rest) | `manipulator` | _(no docstring)_ |
| [`reset_collection_state`](collection.md#reset-collection-state) | `collection` | _(no docstring)_ |
| [`retime_trajectory`](manipulator.md#retime-trajectory) | `manipulator` | _(no docstring)_ |
| [`rotate_joint`](manipulator.md#rotate-joint) | `manipulator` | _(no docstring)_ |
| [`scan_room_for_tables`](perception.md#scan-room-for-tables) | `perception` | _(no docstring)_ |
| [`score_view_novelty`](perception.md#score-view-novelty) | `perception` | _(no docstring)_ |
| [`select_point_in_workspace`](collection.md#select-point-in-workspace) | `collection` | _(no docstring)_ |
| [`send_executor_command`](meta.md#send-executor-command) | `meta` | _(no docstring)_ |
| [`start_recording`](recording.md#start-recording) | `recording` | _(no docstring)_ |
| [`stop_recording`](recording.md#stop-recording) | `recording` | _(no docstring)_ |
| [`store_episode_summary`](collection.md#store-episode-summary) | `collection` | _(no docstring)_ |
| [`summarize_data_gaps`](collection.md#summarize-data-gaps) | `collection` | _(no docstring)_ |
| [`survey_scene_pose`](manipulator.md#survey-scene-pose) | `manipulator` | _(no docstring)_ |
| [`unlock_base`](manipulator.md#unlock-base) | `manipulator` | _(no docstring)_ |
| [`update_coverage_state`](collection.md#update-coverage-state) | `collection` | _(no docstring)_ |
| [`update_data_spec`](collection.md#update-data-spec) | `collection` | _(no docstring)_ |
| [`update_memory_index`](meta.md#update-memory-index) | `meta` | _(no docstring)_ |
| [`update_plan`](meta.md#update-plan) | `meta` | _(no docstring)_ |
| [`update_target_position`](collection.md#update-target-position) | `collection` | _(no docstring)_ |
