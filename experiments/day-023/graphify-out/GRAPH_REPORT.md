# Graph Report - graphify-out  (2026-10-21)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 914 nodes · 1657 edges · 56 communities (29 shown, 27 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 100 edges (avg confidence: 0.85)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `5d8c306f`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Community 0
- Community 1
- Community 2
- Community 3
- Community 4
- Community 5
- Community 6
- Community 7
- Community 8
- Community 9
- Community 10
- Community 11
- Community 12
- Community 13
- Community 15
- Community 16
- Community 17
- Community 18
- Community 19
- Community 20
- Community 21
- Community 22
- Community 23
- Community 24
- Community 25
- Community 26
- Community 27
- Community 28
- Community 30
- Community 31
- Community 32
- Community 33
- Community 34
- Community 35
- Community 36
- Community 37
- Community 38
- Community 39
- Community 40
- Community 41
- Community 42
- Community 43
- Community 44
- Community 45
- Community 46
- Community 47
- Community 48
- Community 49
- Community 51
- Community 55

## God Nodes (most connected - your core abstractions)
1. `_` - 71 edges
2. `BaseMemory` - 20 edges
3. `Client` - 16 edges
4. `$e()` - 15 edges
5. `BinarySphericalQuantizer` - 14 edges
6. `v()` - 14 edges
7. `ProtocolError` - 13 edges
8. `B8_CTWM` - 13 edges
9. `AsyncClient` - 13 edges
10. `CitationVerifier` - 13 edges

## Surprising Connections (you probably didn't know these)
- `init_run()` --uses--> `B8_CTWM`  [INFERRED]
  experiments/day-006/run_prediction_loop.py → experiments/day-006/vendor/backends_ctwm.py
- `init_run()` --uses--> `B8_CTWM`  [INFERRED]
  experiments/day-006/run_prediction_loop_v2.py → experiments/day-006/vendor/backends_ctwm.py
- `ne()` --indirect_call--> `a`  [INFERRED]
  experiments/day-018/samples/bundle.js → experiments/day-018/samples/recovered-module.js
- `v()` --indirect_call--> `U()`  [INFERRED]
  experiments/day-018/samples/recovered-module.js → experiments/day-018/samples/bundle.js
- `$e()` --indirect_call--> `n`  [INFERRED]
  experiments/day-018/samples/bundle.js → experiments/day-018/samples/recovered-module.js

## Import Cycles
- None detected.

## Communities (56 total, 27 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.09
Nodes (21): _alpha(), _array(), check_homogeneity_of_variance(), check_linearity(), check_normality(), check_normality_per_group(), check_regression_diagnostics(), _clean() (+13 more)

### Community 1 - "Community 1"
Cohesion: 0.06
Nodes (9): classify(), run_rule_based(), auto_regressive_inference(), calc_time_stamps(), Kronos, KronosPredictor, KronosTokenizer, sample_from_logits() (+1 more)

### Community 2 - "Community 2"
Cohesion: 0.08
Nodes (31): Ae(), B(), Be(), c(), F(), fe(), Ge(), ht() (+23 more)

### Community 3 - "Community 3"
Cohesion: 0.07
Nodes (33): _, Ae(), Be(), Bt, ce(), createPseudo(), $e(), F() (+25 more)

### Community 4 - "Community 4"
Cohesion: 0.10
Nodes (31): build_action_menu(), cmd_answer(), cmd_init(), emit_next_prompt(), finalize(), init_run(), main(), make_prompt_text() (+23 more)

### Community 5 - "Community 5"
Cohesion: 0.05
Nodes (43): analysis_input, format, input_path, detected_formats, engine, audited_source_revision, executable, executed_source_revision (+35 more)

### Community 6 - "Community 6"
Cohesion: 0.07
Nodes (9): deduplicate_results(), filter_by_year(), format_search_results(), generate_search_summary(), main(), rank_results(), CitationVerifier, main() (+1 more)

### Community 7 - "Community 7"
Cohesion: 0.05
Nodes (43): analysis_input, format, input_path, detected_formats, engine, audited_source_revision, executable, executed_source_revision (+35 more)

### Community 8 - "Community 8"
Cohesion: 0.08
Nodes (7): main(), _normalize_review_text(), _parse_score(), _parse_verdict(), _resolve_api_key(), ReviewResult, ScientificSchematicGenerator

### Community 9 - "Community 9"
Cohesion: 0.14
Nodes (9): build_request(), check_orders(), check_prepare_state(), Client, Question, Score, score_question(), yes_no_question() (+1 more)

### Community 10 - "Community 10"
Cohesion: 0.10
Nodes (9): DestructiveSummaryMemory, EmbargoedMemory, NonDestructiveMemory, score(), Record, run(), NonDestructiveMemory, Record (+1 more)

### Community 11 - "Community 11"
Cohesion: 0.08
Nodes (24): { createUniver, LocaleType }, main(), rawRows, { UniverSheetsNodeCorePreset }, author, dependencies, rxjs, @univerjs/preset-sheets-node-core (+16 more)

### Community 12 - "Community 12"
Cohesion: 0.13
Nodes (10): Busy, ConnectionFailed, error_for(), InvalidRequest, JeffError, NotReady, ServerError, TooManyOptions (+2 more)

### Community 13 - "Community 13"
Cohesion: 0.09
Nodes (15): _h(), _q(), { app, BrowserWindow, ipcMain }, path, { quote, debugSnapshot }, author, dependencies, electron (+7 more)

### Community 15 - "Community 15"
Cohesion: 0.15
Nodes (6): Call, Health, ModelInfo, parse_health(), parse_models(), Transport

### Community 17 - "Community 17"
Cohesion: 0.13
Nodes (3): aggregate_ngrams(), build_base_tokenizer(), main()

### Community 18 - "Community 18"
Cohesion: 0.27
Nodes (5): Answers, in_order(), number(), ProtocolError, WireAnswer

### Community 19 - "Community 19"
Cohesion: 0.26
Nodes (7): CapacityExceeded, decodes_valid_input_within_capacity(), odd_trailing_byte_is_ignored_like_c_version(), rejects_input_that_would_overflow_capacity(), rle_decode(), hex_decode(), main()

### Community 21 - "Community 21"
Cohesion: 0.25
Nodes (4): main(), build_subprocess_env(), main(), resolve_api_key()

### Community 22 - "Community 22"
Cohesion: 0.35
Nodes (11): ee(), L(), N(), c(), d(), ee(), L(), T() (+3 more)

### Community 24 - "Community 24"
Cohesion: 0.24
Nodes (3): hex_decode(), main(), rle_decode()

### Community 28 - "Community 28"
Cohesion: 0.31
Nodes (10): B(), fe(), h(), I(), J(), ne(), Q(), re() (+2 more)

### Community 31 - "Community 31"
Cohesion: 0.25
Nodes (3): Choice, choice_question(), option_pairs()

### Community 32 - "Community 32"
Cohesion: 0.31
Nodes (5): parse_response(), Request, Response, Usage, WireQuestion

### Community 36 - "Community 36"
Cohesion: 0.43
Nodes (3): check_dependencies(), generate_pdf(), main()

### Community 37 - "Community 37"
Cohesion: 0.36
Nodes (8): $e(), Ie(), m(), o(), l(), We(), a, l()

### Community 41 - "Community 41"
Cohesion: 0.43
Nodes (3): call_tool(), chat(), main()

### Community 42 - "Community 42"
Cohesion: 0.29
Nodes (6): description, devDependencies, wakaru, name, private, wakaru

### Community 47 - "Community 47"
Cohesion: 0.60
Nodes (3): gen_valid_case(), main(), run()

## Knowledge Gaps
- **4 isolated node(s):** `tt`, `rxjs`, `wakaru`, `rle_decode`
  These have ≤1 connection - possible missing edges. (Counts symbols only; 402 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **27 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `BinarySphericalQuantizer` connect `Community 16` to `Community 43`, `Community 30`?**
  _High betweenness centrality (0.024) - this node is a cross-community bridge._
- **Are the 5 inferred relationships involving `_` (e.g. with `o()` and `at()`) actually correct?**
  _`_` has 5 INFERRED edges - model-reasoned connections that need verification._
- **What connects `tt`, `rxjs`, `wakaru` to the rest of the system?**
  _4 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.08944793850454227 - nodes in this community are weakly interconnected._
- **Should `Community 1` be split into smaller, more focused modules?**
  _Cohesion score 0.06033182503770739 - nodes in this community are weakly interconnected._
- **Should `Community 2` be split into smaller, more focused modules?**
  _Cohesion score 0.08156028368794327 - nodes in this community are weakly interconnected._
- **Should `Community 3` be split into smaller, more focused modules?**
  _Cohesion score 0.06666666666666667 - nodes in this community are weakly interconnected._