# Tool catalog

Every `@tool` registered under [`modulated_system/tools/`](https://github.com/Pengyu-Mo/tidyros_iphone/tree/main/modulated_system/tools). Generated from source by [`scripts/regenerate_tool_catalog.py`](https://github.com/saimlau/aeda_docs/blob/main/scripts/regenerate_tool_catalog.py) — re-run after upstream changes.

**73 tools** across **9 categories**. The category pages (see the nav) group them with prose context; this page is the flat alphabetical view.

| Tool | Category | Summary |
|---|---|---|
| [`activate_workspace`](collection.md#activate_workspace) | `collection` | _(no docstring)_ |
| [`analyze_camera_trajectory_distribution`](data.md#analyze_camera_trajectory_distribution) | `data` | _(no docstring)_ |
| [`analyze_depth_distribution`](data.md#analyze_depth_distribution) | `data` | _(no docstring)_ |
| [`analyze_intrinsics_distribution`](data.md#analyze_intrinsics_distribution) | `data` | _(no docstring)_ |
| [`analyze_language_distribution`](data.md#analyze_language_distribution) | `data` | _(no docstring)_ |
| [`analyze_object_distribution`](data.md#analyze_object_distribution) | `data` | _(no docstring)_ |
| [`analyze_recording`](meta.md#analyze_recording) | `meta` | _(no docstring)_ |
| [`append_memory`](meta.md#append_memory) | `meta` | _(no docstring)_ |
| [`check_reachability`](manipulator.md#check_reachability) | `manipulator` | _(no docstring)_ |
| [`check_stop_condition`](collection.md#check_stop_condition) | `collection` | _(no docstring)_ |
| [`check_target_in_frame`](perception.md#check_target_in_frame) | `perception` | Returns: |
| [`choose_collection_site`](navigation.md#choose_collection_site) | `navigation` | _(no docstring)_ |
| [`compare_distributions`](data.md#compare_distributions) | `data` | _(no docstring)_ |
| [`compute_params_for_base_pose`](trajectory.md#compute_params_for_base_pose) | `trajectory` | _(no docstring)_ |
| [`compute_parking_locations`](trajectory.md#compute_parking_locations) | `trajectory` | _(no docstring)_ |
| [`correlate_dimensions`](data.md#correlate_dimensions) | `data` | _(no docstring)_ |
| [`coverage_report`](data.md#coverage_report) | `data` | _(no docstring)_ |
| [`create_data_spec`](collection.md#create_data_spec) | `collection` | _(no docstring)_ |
| [`define_workspace`](collection.md#define_workspace) | `collection` | _(no docstring)_ |
| [`describe_distribution`](data.md#describe_distribution) | `data` | _(no docstring)_ |
| [`detect_target`](perception.md#detect_target) | `perception` | _(no docstring)_ |
| [`estimate_target_visibility`](perception.md#estimate_target_visibility) | `perception` | Returns a dict with confidence + diagnostic flags. |
| [`evaluate_episode`](collection.md#evaluate_episode) | `collection` | _(no docstring)_ |
| [`execute_trajectory`](trajectory.md#execute_trajectory) | `trajectory` | _(no docstring)_ |
| [`explore_frontier`](navigation.md#explore_frontier) | `navigation` | _(no docstring)_ |
| [`explore_unvisited`](navigation.md#explore_unvisited) | `navigation` | _(no docstring)_ |
| [`find_cluster_target`](perception.md#find_cluster_target) | `perception` | _(no docstring)_ |
| [`find_feasible_params`](trajectory.md#find_feasible_params) | `trajectory` | _(no docstring)_ |
| [`generate_view_trajectory`](trajectory.md#generate_view_trajectory) | `trajectory` | _(no docstring)_ |
| [`get_collection_status`](collection.md#get_collection_status) | `collection` | _(no docstring)_ |
| [`get_executor_state`](meta.md#get_executor_state) | `meta` | _(no docstring)_ |
| [`get_map_snapshot`](meta.md#get_map_snapshot) | `meta` | _(no docstring)_ |
| [`get_trajectory_history`](meta.md#get_trajectory_history) | `meta` | _(no docstring)_ |
| [`identify_objects_vision`](perception.md#identify_objects_vision) | `perception` | _(no docstring)_ |
| [`inject_primer_note`](meta.md#inject_primer_note) | `meta` | _(no docstring)_ |
| [`inspect_dataset`](data.md#inspect_dataset) | `data` | _(no docstring)_ |
| [`list_objects_in_view`](perception.md#list_objects_in_view) | `perception` | _(no docstring)_ |
| [`list_workspaces`](collection.md#list_workspaces) | `collection` | _(no docstring)_ |
| [`lock_base`](manipulator.md#lock_base) | `manipulator` | _(no docstring)_ |
| [`log_event`](collection.md#log_event) | `collection` | _(no docstring)_ |
| [`move_camera_relative`](manipulator.md#move_camera_relative) | `manipulator` | _(no docstring)_ |
| [`move_relative`](navigation.md#move_relative) | `navigation` | _(no docstring)_ |
| [`navigate_to`](navigation.md#navigate_to) | `navigation` | _(no docstring)_ |
| [`notify_supervisor`](meta.md#notify_supervisor) | `meta` | _(no docstring)_ |
| [`plan_arm_motion`](manipulator.md#plan_arm_motion) | `manipulator` | _(no docstring)_ |
| [`prepose_arm_for_view`](manipulator.md#prepose_arm_for_view) | `manipulator` | _(no docstring)_ |
| [`python_exec`](data_analysis.md#python_exec) | `data_analysis` | _(no docstring)_ |
| [`query_log`](meta.md#query_log) | `meta` | _(no docstring)_ |
| [`read_memory`](meta.md#read_memory) | `meta` | _(no docstring)_ |
| [`recover_arm`](manipulator.md#recover_arm) | `manipulator` | _(no docstring)_ |
| [`register_labeled_object`](collection.md#register_labeled_object) | `collection` | _(no docstring)_ |
| [`register_workspace`](collection.md#register_workspace) | `collection` | _(no docstring)_ |
| [`reposition`](navigation.md#reposition) | `navigation` | _(no docstring)_ |
| [`request_next_view`](navigation.md#request_next_view) | `navigation` | _(no docstring)_ |
| [`reset_arm_to_rest`](manipulator.md#reset_arm_to_rest) | `manipulator` | _(no docstring)_ |
| [`reset_collection_state`](collection.md#reset_collection_state) | `collection` | _(no docstring)_ |
| [`retime_trajectory`](manipulator.md#retime_trajectory) | `manipulator` | _(no docstring)_ |
| [`rotate_joint`](manipulator.md#rotate_joint) | `manipulator` | _(no docstring)_ |
| [`scan_room_for_tables`](perception.md#scan_room_for_tables) | `perception` | _(no docstring)_ |
| [`score_view_novelty`](perception.md#score_view_novelty) | `perception` | _(no docstring)_ |
| [`select_point_in_workspace`](collection.md#select_point_in_workspace) | `collection` | _(no docstring)_ |
| [`send_executor_command`](meta.md#send_executor_command) | `meta` | _(no docstring)_ |
| [`start_recording`](recording.md#start_recording) | `recording` | _(no docstring)_ |
| [`stop_recording`](recording.md#stop_recording) | `recording` | _(no docstring)_ |
| [`store_episode_summary`](collection.md#store_episode_summary) | `collection` | _(no docstring)_ |
| [`summarize_data_gaps`](collection.md#summarize_data_gaps) | `collection` | _(no docstring)_ |
| [`survey_scene_pose`](manipulator.md#survey_scene_pose) | `manipulator` | _(no docstring)_ |
| [`unlock_base`](manipulator.md#unlock_base) | `manipulator` | _(no docstring)_ |
| [`update_coverage_state`](collection.md#update_coverage_state) | `collection` | _(no docstring)_ |
| [`update_data_spec`](collection.md#update_data_spec) | `collection` | _(no docstring)_ |
| [`update_memory_index`](meta.md#update_memory_index) | `meta` | _(no docstring)_ |
| [`update_plan`](meta.md#update_plan) | `meta` | _(no docstring)_ |
| [`update_target_position`](collection.md#update_target_position) | `collection` | _(no docstring)_ |
