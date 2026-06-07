# Tools — `data` (10)

Inspect a dataset's distribution. Per-axis analyzers (`analyze_*_distribution`), pairwise correlation, coverage report, and cross-dataset comparison. Consumed by the data-analyzer subagent at session start to seed the plan.

## In this category

- [`analyze_camera_trajectory_distribution`](#analyze_camera_trajectory_distribution) — Trajectory diversity across train / target / collected / recent. Five axes: motion-kind categorical histogram + entropy, linear/angular speeds, mode (base vs arm), translation/rotation magnitude, and style (curvature/smoothness/dwell). For datasets without trajectory_type labels, motion_kind is heuristically classified from the pose log.
- [`analyze_depth_distribution`](#analyze_depth_distribution) — Depth distribution across train / target / collected / recent. Frame-level dims (mean/std, near/far fraction, valid ratio, gradient) plus object-level dims (per-object depth + 2D-at-depth size in meters) derived from the RAM++/SAM3 pipeline. The headline modality from the paper. Returns multi-metric comparisons + suggested rebalance actions.
- [`analyze_intrinsics_distribution`](#analyze_intrinsics_distribution) — Camera intrinsics distribution across train / target / collected / recent. Mostly degenerate for iPhone-only collections; useful when comparing across cameras (iPhone vs Kinect vs ARKit) where focal length and principal point differ meaningfully.
- [`analyze_language_distribution`](#analyze_language_distribution) — Language-instruction distribution across train / target / collected / recent. Lexical dims (length, token count, vocabulary) plus semantic dims (topic entropy, complexity). Returns has_instruction=0 for datasets lacking instructions — other dims gracefully skip those sources.
- [`analyze_object_distribution`](#analyze_object_distribution) — Object-level distribution analysis driven by RAM++ → SAM3. Compares train / target / collected / recent on dimensions like class diversity, per-frame detection count, bbox fill / aspect / position, and occlusion ratio. Returns stats per source, multi-metric comparisons (W1, KS, JS, Hellinger, hypothesis tests, effect sizes, bootstrap CI), suggested rebalance actions, and an optional KDE plot.
- [`compare_distributions`](#compare_distributions) — Pairwise distribution comparison: distance metrics, hypothesis tests, effect sizes, and bootstrap CI in one call. Accepts either explicit value arrays or cache identifiers of the form '<source>.<modality>.<dim>'. Use when the analyze_* tools' defaults don't cover what you need (custom metric subset, different bootstrap N, cross-modality comparisons).
- [`correlate_dimensions`](#correlate_dimensions) — Cross-dimensional correlation within ONE data source. Returns Pearson r + p, Spearman ρ + p, Kendall τ + p, and mutual information (non-linear-aware) for the two named dimensions. Optional 3rd 'control' dim adds partial Pearson to test whether the apparent correlation is mediated by a third variable. Use to probe spatial-reasoning laws like size-distance correlation within collected data.
- [`coverage_report`](#coverage_report) — Bin-by-bin gap analysis between two distributions. Headline output: top-K bins where source_b is UNDER-represented vs source_a — these are the bins the supervisor should target for additional collection. Also returns the full bin table (counts, densities, gap, relative gap) and top-K over-represented bins. Use this when 'target_vs_collected level=moderate' isn't enough — you need to know WHICH bins are off.
- [`describe_distribution`](#describe_distribution) — Single-distribution diagnostic. Returns moments (incl. skewness/kurtosis), quantiles, robust stats (median/MAD), shape tests (Hartigan dip for multimodality, Shapiro-Wilk for normality, Anderson-Darling), outlier counts via Tukey and MAD rules, and KDE peak detection. Use to understand WHAT a distribution looks like beyond mean/std.
- [`inspect_dataset`](#inspect_dataset) — Heuristic inspection of any dataset folder. Walks the tree, identifies which subdirectories likely hold RGB / depth / pose / intrinsics / language, and returns a layout schema with sample file paths the caller can spot-check. Use BEFORE the analyze_* tools when unsure what's in a folder.

---

## `analyze_camera_trajectory_distribution`

**Module:** [`modulated_system/tools/data_analysis/analyze_camera_trajectory_distribution.py`](https://github.com/Pengyu-Mo/tidyros_iphone/blob/main/modulated_system/tools/data_analysis/analyze_camera_trajectory_distribution.py#L58)  ·  **Python function:** `analyze_camera_trajectory_distribution`  ·  **Description source:** decorator `description=`

Trajectory diversity across train / target / collected / recent. Five axes: motion-kind categorical histogram + entropy, linear/angular speeds, mode (base vs arm), translation/rotation magnitude, and style (curvature/smoothness/dwell). For datasets without trajectory_type labels, motion_kind is heuristically classified from the pose log.

### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `train_dataset` | `string` | — | — | Path to train dataset root. |
| `target_dataset` | `string` | — | — | Path to target dataset root. |
| `dimensions` | `array` | — | — | Subset of fixed dims (default: all). |
| `drift_window` | `integer` | — | `20` | Last-N episodes for drift_recent. |
| `sample_fraction` | `number` | — | `0.1` | Fraction of train/target scenes to sample. |
| `sample_seed` | `integer` | — | `42` | RNG seed. |
| `refresh_cache` | `boolean` | — | `False` | Force recompute of cached per-episode summaries. |
| `include_plot` | `boolean` | — | `False` | Render PNG per dimension. |
| `include_bin_gaps` | `boolean` | — | `False` | Add per-bin gap report to each comparison. |
| `bin_n_bins` | `integer` | — | `20` | Number of histogram bins for bin_gaps (-1 → auto). |
| `bin_top_k` | `integer` | — | `5` | Top-K under/over-represented bins per pair. |
| `session_id` | `string` | — | — | Override session resolution. |

---

## `analyze_depth_distribution`

**Module:** [`modulated_system/tools/data_analysis/analyze_depth_distribution.py`](https://github.com/Pengyu-Mo/tidyros_iphone/blob/main/modulated_system/tools/data_analysis/analyze_depth_distribution.py#L42)  ·  **Python function:** `analyze_depth_distribution`  ·  **Description source:** decorator `description=`

Depth distribution across train / target / collected / recent. Frame-level dims (mean/std, near/far fraction, valid ratio, gradient) plus object-level dims (per-object depth + 2D-at-depth size in meters) derived from the RAM++/SAM3 pipeline. The headline modality from the paper. Returns multi-metric comparisons + suggested rebalance actions.

### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `train_dataset` | `string` | — | — | Path to train dataset root. |
| `target_dataset` | `string` | — | — | Path to target dataset root. |
| `dimensions` | `array` | — | — | Subset of frame + object dims. Default: all. Object dims require the object pipeline cache. |
| `class_filter` | `string` | — | — | Restrict object-level dims to ONE class label (e.g. 'mug'). Use to probe per-class depth behavior, the paper's `size_distance_correlation` story. |
| `drift_window` | `integer` | — | `20` | Last-N episodes for drift_recent. |
| `sample_fraction` | `number` | — | `0.1` | Fraction of train/target scenes to sample. |
| `sample_seed` | `integer` | — | `42` | RNG seed for reproducible sampling. |
| `depth_model` | `string` | — | `'gt'` | Depth source: 'gt' (ground-truth sensor) or one of 'unidepth' / 'depth_pro' / 'depth_anything_v2' for a learned monocular model. Use a learned model when comparing iPhone vs Kinect consistently. |
| `refresh_cache` | `boolean` | — | `False` | Force recompute of cached per-episode summaries. |
| `enable_objects` | `boolean` | — | `True` | Run RAM++/SAM3 to populate object-level dims. Disable to skip GPU work when you only need frame-level depth. |
| `include_plot` | `boolean` | — | `False` | Render KDE overlay PNG per dimension. |
| `include_bin_gaps` | `boolean` | — | `False` | Add per-bin gap report to each comparison (turns 'moderate W1' into 'depth [<1m] missing 28% density vs target'). |
| `bin_n_bins` | `integer` | — | `20` | Number of histogram bins for bin_gaps. Pass -1 for Freedman-Diaconis auto-binning (recommended for skewed dims like depth). |
| `bin_top_k` | `integer` | — | `5` | Top-K most under/over-represented bins per pair. |
| `session_id` | `string` | — | — | Override session resolution. |

---

## `analyze_intrinsics_distribution`

**Module:** [`modulated_system/tools/data_analysis/analyze_intrinsics_distribution.py`](https://github.com/Pengyu-Mo/tidyros_iphone/blob/main/modulated_system/tools/data_analysis/analyze_intrinsics_distribution.py#L28)  ·  **Python function:** `analyze_intrinsics_distribution`  ·  **Description source:** decorator `description=`

Camera intrinsics distribution across train / target / collected / recent. Mostly degenerate for iPhone-only collections; useful when comparing across cameras (iPhone vs Kinect vs ARKit) where focal length and principal point differ meaningfully.

### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `train_dataset` | `string` | — | — | Path to train dataset root. |
| `target_dataset` | `string` | — | — | Path to target dataset root. |
| `dimensions` | `array` | — | — | Subset of fixed dims (default: all). |
| `drift_window` | `integer` | — | `20` | Last-N for drift_recent. |
| `sample_fraction` | `number` | — | `0.1` | Fraction of train/target scenes to sample. |
| `sample_seed` | `integer` | — | `42` | RNG seed. |
| `refresh_cache` | `boolean` | — | `False` | Force recompute of cached per-episode summaries. |
| `include_plot` | `boolean` | — | `False` | Render PNG per dimension. |
| `include_bin_gaps` | `boolean` | — | `False` | Add per-bin gap report to each comparison. |
| `bin_n_bins` | `integer` | — | `20` | Histogram bins for bin_gaps (-1 → auto). |
| `bin_top_k` | `integer` | — | `5` | Top-K under/over-represented bins per pair. |
| `session_id` | `string` | — | — | Override session resolution. |

---

## `analyze_language_distribution`

**Module:** [`modulated_system/tools/data_analysis/analyze_language_distribution.py`](https://github.com/Pengyu-Mo/tidyros_iphone/blob/main/modulated_system/tools/data_analysis/analyze_language_distribution.py#L50)  ·  **Python function:** `analyze_language_distribution`  ·  **Description source:** decorator `description=`

Language-instruction distribution across train / target / collected / recent. Lexical dims (length, token count, vocabulary) plus semantic dims (topic entropy, complexity). Returns has_instruction=0 for datasets lacking instructions — other dims gracefully skip those sources.

### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `train_dataset` | `string` | — | — | Path to train dataset root. |
| `target_dataset` | `string` | — | — | Path to target dataset root. |
| `dimensions` | `array` | — | — | Subset of fixed dims (default: all). |
| `drift_window` | `integer` | — | `20` | Last-N for drift_recent. |
| `sample_fraction` | `number` | — | `0.1` | Fraction of train/target scenes to sample. |
| `sample_seed` | `integer` | — | `42` | RNG seed. |
| `refresh_cache` | `boolean` | — | `False` | Force recompute of cached per-episode summaries. |
| `include_plot` | `boolean` | — | `False` | Render PNG per dimension. |
| `include_bin_gaps` | `boolean` | — | `False` | Add per-bin gap report to each comparison. |
| `bin_n_bins` | `integer` | — | `20` | Histogram bins for bin_gaps (-1 → auto). |
| `bin_top_k` | `integer` | — | `5` | Top-K under/over-represented bins per pair. |
| `session_id` | `string` | — | — | Override session resolution. |

---

## `analyze_object_distribution`

**Module:** [`modulated_system/tools/data_analysis/analyze_object_distribution.py`](https://github.com/Pengyu-Mo/tidyros_iphone/blob/main/modulated_system/tools/data_analysis/analyze_object_distribution.py#L48)  ·  **Python function:** `analyze_object_distribution`  ·  **Description source:** decorator `description=`

Object-level distribution analysis driven by RAM++ → SAM3. Compares train / target / collected / recent on dimensions like class diversity, per-frame detection count, bbox fill / aspect / position, and occlusion ratio. Returns stats per source, multi-metric comparisons (W1, KS, JS, Hellinger, hypothesis tests, effect sizes, bootstrap CI), suggested rebalance actions, and an optional KDE plot.

### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `train_dataset` | `string` | — | — | Path to train dataset root. Skip pair if omitted. |
| `target_dataset` | `string` | — | — | Path to target dataset root. Skip pair if omitted. |
| `dimensions` | `array` | — | — | Subset of the fixed catalog to analyze. Default: all fixed dims. |
| `class_filter` | `string` | — | — | Restrict per-class dimensions to ONE class label (e.g. 'mug'). Other dims unaffected. |
| `drift_window` | `integer` | — | `20` | Last-N episodes used for drift_recent comparison. |
| `sample_fraction` | `number` | — | `0.1` | Fraction of train/target scenes to sample. Paper default: 0.1. |
| `sample_seed` | `integer` | — | `42` | RNG seed for reproducible sampling. |
| `refresh_cache` | `boolean` | — | `False` | True forces recompute of per-episode cached summaries. Slow; use only when you suspect cache staleness. |
| `include_plot` | `boolean` | — | `False` | Render base64 PNG KDE overlay per dimension. Heavy — only when needed. |
| `include_bin_gaps` | `boolean` | — | `False` | Add per-bin density gap report to each comparison: which histogram bins are over/under-represented vs target, plus top-K most-actionable bins. |
| `bin_n_bins` | `integer` | — | `20` | Number of histogram bins for bin_gaps. Pass -1 for Freedman-Diaconis auto-binning. |
| `bin_top_k` | `integer` | — | `5` | Top-K most under/over-represented bins to highlight. |
| `session_id` | `string` | — | — | Override session resolution. |

---

## `compare_distributions`

**Module:** [`modulated_system/tools/data_analysis/compare_distributions.py`](https://github.com/Pengyu-Mo/tidyros_iphone/blob/main/modulated_system/tools/data_analysis/compare_distributions.py#L42)  ·  **Python function:** `compare_distributions`  ·  **Description source:** decorator `description=`

Pairwise distribution comparison: distance metrics, hypothesis tests, effect sizes, and bootstrap CI in one call. Accepts either explicit value arrays or cache identifiers of the form '<source>.<modality>.<dim>'. Use when the analyze_* tools' defaults don't cover what you need (custom metric subset, different bootstrap N, cross-modality comparisons).

### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `values_a` | `array` | — | — | Explicit array A. Mutually exclusive with source_a. |
| `values_b` | `array` | — | — | Explicit array B. Mutually exclusive with source_b. |
| `source_a` | `string` | — | — | Cache identifier '<source>.<modality>.<dim>'. E.g. 'collected.depth.near_fraction'. |
| `source_b` | `string` | — | — | Same format as source_a. |
| `train_dataset` | `string` | — | — | Path to train dataset (needed if source_a/b uses 'train'). |
| `target_dataset` | `string` | — | — | Path to target dataset (needed for 'target' source). |
| `drift_window` | `integer` | — | `20` | Last-N for 'recent' source. |
| `categorical` | `boolean` | — | `False` | Treat inputs as categorical PMFs (each value is a label; counts aggregated). |
| `distance_metrics` | `array` | — | — | Subset of {w1, ks, js, tv, hellinger, kl, mmd_rbf, energy}. Default: all applicable. |
| `hypothesis_tests` | `array` | — | — | Subset of {ks_test, mannwhitney_u, anderson_darling_2sample, welch_t, chi2_test, permutation_test}. Skipped for categorical. |
| `effect_sizes` | `array` | — | — | Subset of {cohens_d, cliffs_delta, hedges_g}. Skipped for categorical. |
| `n_bootstrap` | `integer` | — | `1000` | Bootstrap CI resamples. 0 disables bootstrap. |
| `level_metric` | `string` | — | `'w1'` | Metric used for the 'level' bucketing. |
| `session_id` | `string` | — | — | Override session resolution. |

---

## `correlate_dimensions`

**Module:** [`modulated_system/tools/data_analysis/correlate_dimensions.py`](https://github.com/Pengyu-Mo/tidyros_iphone/blob/main/modulated_system/tools/data_analysis/correlate_dimensions.py#L27)  ·  **Python function:** `correlate_dimensions`  ·  **Description source:** decorator `description=`

Cross-dimensional correlation within ONE data source. Returns Pearson r + p, Spearman ρ + p, Kendall τ + p, and mutual information (non-linear-aware) for the two named dimensions. Optional 3rd 'control' dim adds partial Pearson to test whether the apparent correlation is mediated by a third variable. Use to probe spatial-reasoning laws like size-distance correlation within collected data.

### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `modality_a` | `string` | ✓ | — | Modality of dimension A (objects, depth, camera_trajectory, intrinsics, language). |
| `dim_a` | `string` | ✓ | — | Dimension name within modality_a. |
| `modality_b` | `string` | ✓ | — | Modality of dimension B. |
| `dim_b` | `string` | ✓ | — | Dimension name within modality_b. |
| `source` | `string` | — | `'collected'` | Which data source to operate on: collected, recent, train, target. |
| `control_modality` | `string` | — | — | If both control_modality and control_dim provided, also returns partial Pearson r(a, b ¦ c). |
| `control_dim` | `string` | — | — | Dimension name within control_modality. |
| `methods` | `array` | — | — | Subset of {pearson, spearman, kendall, mutual_info, partial_pearson}. Default: first 4. |
| `class_filter` | `string` | — | — | Restrict object-level dims to ONE class. |
| `train_dataset` | `string` | — | — | Path to train dataset (needed when source='train'). |
| `target_dataset` | `string` | — | — | Path to target dataset (needed when source='target'). |
| `drift_window` | `integer` | — | `20` | Last-N for source='recent'. |
| `session_id` | `string` | — | — | Override session resolution. |

---

## `coverage_report`

**Module:** [`modulated_system/tools/data_analysis/coverage_report.py`](https://github.com/Pengyu-Mo/tidyros_iphone/blob/main/modulated_system/tools/data_analysis/coverage_report.py#L37)  ·  **Python function:** `coverage_report`  ·  **Description source:** decorator `description=`

Bin-by-bin gap analysis between two distributions. Headline output: top-K bins where source_b is UNDER-represented vs source_a — these are the bins the supervisor should target for additional collection. Also returns the full bin table (counts, densities, gap, relative gap) and top-K over-represented bins. Use this when 'target_vs_collected level=moderate' isn't enough — you need to know WHICH bins are off.

### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `values_a` | `array` | — | — | Explicit array for source A (the reference, e.g. target). Mutually exclusive with source_a. |
| `values_b` | `array` | — | — | Explicit array for source B (what you're evaluating coverage of, e.g. collected). Mutually exclusive with source_b. |
| `source_a` | `string` | — | — | Cache identifier '<source>.<modality>.<dim>'. Convention: A is the reference (target/train), B is what you're checking (collected/recent). |
| `source_b` | `string` | — | — | Same format as source_a. |
| `train_dataset` | `string` | — | — | Path to train dataset (when a source uses 'train'). |
| `target_dataset` | `string` | — | — | Path to target dataset (when a source uses 'target'). |
| `drift_window` | `integer` | — | `20` | Last-N for 'recent' source. |
| `n_bins` | `integer` | — | `20` | Number of histogram bins. Pass -1 for Freedman-Diaconis auto-binning (better for skewed dims like depth). |
| `bin_edges` | `array` | — | — | Explicit bin edges (n+1 numbers). Overrides n_bins. Useful for known domain breaks like depth at [0, 0.5, 1.0, 1.5, 2.0, 3.0, 5.0, 10.0]. |
| `top_k` | `integer` | — | `5` | How many under/over-represented bins to highlight. |
| `categorical` | `boolean` | — | `False` | Treat inputs as categorical PMFs (each value is a label; counts aggregated). Default: auto-detect from input. |
| `session_id` | `string` | — | — | Override session resolution. |

---

## `describe_distribution`

**Module:** [`modulated_system/tools/data_analysis/describe_distribution.py`](https://github.com/Pengyu-Mo/tidyros_iphone/blob/main/modulated_system/tools/data_analysis/describe_distribution.py#L28)  ·  **Python function:** `describe_distribution`  ·  **Description source:** decorator `description=`

Single-distribution diagnostic. Returns moments (incl. skewness/kurtosis), quantiles, robust stats (median/MAD), shape tests (Hartigan dip for multimodality, Shapiro-Wilk for normality, Anderson-Darling), outlier counts via Tukey and MAD rules, and KDE peak detection. Use to understand WHAT a distribution looks like beyond mean/std.

### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `values` | `array` | — | — | Explicit value array. Mutually exclusive with source. |
| `source` | `string` | — | — | Cache identifier '<source>.<modality>.<dim>'. E.g. 'collected.depth.near_fraction'. |
| `summaries` | `array` | — | — | Subset of {moments, quantiles, shape_tests, outliers, modes}. Default: all. |
| `include_boxplot` | `boolean` | — | `False` | Include numeric box-plot stats. |
| `include_ecdf` | `boolean` | — | `False` | Include down-sampled ECDF (x + cdf arrays). |
| `include_kde` | `boolean` | — | `False` | Include KDE samples on a regular grid. |
| `train_dataset` | `string` | — | — | Path to train dataset (needed if source uses 'train'). |
| `target_dataset` | `string` | — | — | Path to target dataset (needed for 'target' source). |
| `drift_window` | `integer` | — | `20` | Last-N for 'recent' source. |
| `session_id` | `string` | — | — | Override session resolution. |

---

## `inspect_dataset`

**Module:** [`modulated_system/tools/data_analysis/inspect_dataset.py`](https://github.com/Pengyu-Mo/tidyros_iphone/blob/main/modulated_system/tools/data_analysis/inspect_dataset.py#L23)  ·  **Python function:** `inspect_dataset`  ·  **Description source:** decorator `description=`

Heuristic inspection of any dataset folder. Walks the tree, identifies which subdirectories likely hold RGB / depth / pose / intrinsics / language, and returns a layout schema with sample file paths the caller can spot-check. Use BEFORE the analyze_* tools when unsure what's in a folder.

### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `path` | `string` | ✓ | — | Absolute path to the dataset root directory. |
| `max_files` | `integer` | — | `20000` | Cap on files scanned. Higher = more accurate for huge datasets but slower. Default 20000. |
| `max_depth` | `integer` | — | `6` | Maximum directory traversal depth. |
| `sample_n` | `integer` | — | `3` | Per-modality sample file count to return in the response. Helps the supervisor spot-check by opening a few files. |

---

