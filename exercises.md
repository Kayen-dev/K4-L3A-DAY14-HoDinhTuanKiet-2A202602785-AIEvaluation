# Day 14 — Exercises

## AI Evaluation & Benchmarking · Lab Worksheet

**Thời gian làm bài:** 14:15–17:00

**Domain:** OrbitTech Store Customer Support

Điền trực tiếp câu trả lời vào file này. Golden dataset 20 QA được viết một lần
duy nhất trong `golden_dataset.json`, không chép lại toàn bộ vào Markdown.

---

Từ 14:15–14:30, cài môi trường và chạy baseline tests theo `guide_lab.md`.

---

## Part 1 — Warm-up (14:30–14:45)

### Exercise 1.1 — RAGAS Metric Thresholds

Theo bài giảng:

- 0.8–1.0: Good — monitor, maintain.
- 0.6–0.8: Needs work — analyze failures, iterate.
- Dưới 0.6: Significant issues — investigate.

Với từng metric, xác định khi nào score thấp có thể chấp nhận và khi nào là
critical.

| Metric | Acceptable Low Score Scenario | Critical Low Score Scenario | Action Required |
|---|---|---|---|
| Faithfulness | A short refusal or limitation statement uses wording not present verbatim in the corpus but makes no unsupported policy claim. | The response invents a refund, warranty approval, product feature, or unsafe instruction. | Inspect answer claims against retrieved evidence; tighten grounding prompt and add a claim-level guardrail. |
| Answer Relevance | A correct answer includes a brief safety or escalation note in addition to the direct answer. | The response fails to address the customer's requested action or answers another policy question. | Improve intent detection and require the first sentence to answer the primary intent. |
| Context Recall | The question is intentionally out of scope and only the scope chunk is needed. | A multi-policy question misses a document containing a required condition, exception, date, or amount. | Improve query expansion, top-k, and chunking; add the missed case to the regression set. |
| Context Precision | Extra supporting chunks are retrieved after all relevant chunks and do not affect generation. | Noise outranks evidence and causes the model to use the wrong policy or version. | Add reranking and tune retrieval terms while monitoring recall. |
| Completeness | A concise answer omits optional background that the user did not request. | It omits a required fee, deadline, eligibility condition, safety action, or exception. | Add checklist-style generation instructions and multi-document retrieval. |

### Exercise 1.2 — Bias trong LLM-as-a-Judge

Ba bias thường gặp:

- Position bias: judge ưu tiên answer xuất hiện trước.
- Verbosity bias: judge ưu tiên answer dài hơn.
- Self-preference: judge ưu tiên output giống chính model đó.

**Câu 1: Thiết kế experiment phát hiện position bias với ít nhất hai conditions.**

> *Câu trả lời:*

Use the same question and two semantically equivalent candidate answers. In
condition A, show Answer 1 before Answer 2; in condition B, reverse their
positions while keeping the rubric, model, temperature, and prompt identical.
Repeat across the calibrated set with randomized labels. A systematic advantage
for whichever answer appears first indicates position bias.

**Câu 2: Làm thế nào giảm verbosity bias bằng rubric design?**

> *Câu trả lời:*

Score atomic requirements rather than length: factual correctness, coverage of
required policy conditions, directness, and safety. State explicitly that
repetition, generic preambles, and unsupported detail earn no credit and may
reduce relevance or faithfulness.

**Câu 3: Tại sao cần calibrate LLM judge với human labels?**

> *Câu trả lời:*

Human labels provide a trusted reference for measuring judge agreement and
detecting systematic leniency, severity, or preference for a model's own style.
Calibration also helps set score thresholds and resolve rubric wording that
different reviewers interpret inconsistently.

### Exercise 1.3 — Evaluation trong CI/CD

**Câu 1: Chọn threshold để block deployment.**

| Metric | Threshold | Lý do |
|---|---:|---|
| Faithfulness | 0.80 | Unsupported policy, privacy, or safety claims create the highest customer risk. |
| Answer Relevance | 0.70 | The answer must resolve the stated intent while allowing a short escalation note. |
| Completeness | 0.75 | Dates, fees, conditions, and exceptions are operationally important in support answers. |

**Câu 2: Khi nào dùng offline evaluation, online evaluation và human review?**

> *Câu trả lời:*

Offline evaluation runs on every prompt, retriever, model, or code change before
deployment. Online evaluation monitors production traces, latency, escalation,
and user feedback after release. Human review is required for calibration,
borderline cases, safety/privacy failures, policy-version disputes, and sampled
production conversations.

---

## Part 2 — Core Coding (14:45–15:40)

Hoàn thiện các TODO bắt buộc trong `template.py`.

### Task 1 — Data Models

- `QAPair`: question, expected answer, gold context, metadata và retrieved contexts.
- `EvalResult`: answer-side scores, optional retrieval scores, pass/failure fields.
- `overall_score()`: trung bình Faithfulness, Relevance và Completeness.

### Task 2 — RAGASEvaluator

Answer-side:

- `evaluate_faithfulness(answer, context)`
- `evaluate_relevance(answer, question)`
- `evaluate_completeness(answer, expected)`

Retrieval-side:

- `evaluate_context_recall(contexts, expected)`
- `evaluate_context_precision(contexts, expected)`

Full pipeline:

- `run_full_eval(..., contexts=None)` luôn tính ba answer metrics.
- Nếu có `contexts`, tính và lưu thêm Context Recall và Context Precision.
- Retrieval scores không làm thay đổi `overall_score()` và pass rule gốc.

### Task 3 — LLMJudge

- `score_response(question, answer, rubric)`
- `detect_bias(scores_batch)`

### Task 4 — BenchmarkRunner

- `run(qa_pairs, agent_fn, evaluator)`
- `generate_report(results)`
- `run_regression(new_results, baseline_results)`
- `identify_failures(results, threshold)`

`BenchmarkRunner.run()` phải truyền `pair.retrieved_contexts` vào
`run_full_eval()`. Report phải có average của hai retrieval metrics.

### Task 5 — FailureAnalyzer

- `categorize_failures(failures)`
- `find_root_cause(failure)`
- `generate_improvement_suggestions(failures)`
- `generate_improvement_log(failures, suggestions)`

Kiểm tra:

```bash
pytest tests/ -v
```

`rerank_by_overlap()` là TODO bonus của Exercise 3.5. Test tương ứng được skip
nếu bạn chưa làm bonus.

---

## Part 3 — Golden Dataset & Real Benchmark (15:40–16:35)

### Exercise 3.1 — Build the Golden Dataset

Thiết kế và validate dataset theo Mục 5–6 trong `guide_lab.md`. Nội dung 20 QA
được điền trực tiếp trong `golden_dataset.json`; phần dưới chỉ ghi lại kết quả
và quyết định thiết kế, không chép lại toàn bộ QA.

**Kết quả dataset**

| Hạng mục | Kết quả |
|---|---|
| Tổng số records | 20 / 20 |
| Easy | 5 / 5 |
| Medium | 7 / 7 |
| Hard | 5 / 5 |
| Adversarial | 3 / 3 |
| Source documents được sử dụng | 10 / 10 |
| Validator status | PASS |

**Ba case đại diện cho quyết định thiết kế**

| ID | Difficulty | Source document(s) | Vì sao case phù hợp với difficulty/attack type? |
|---|---|---|---|
| E01 | Easy | 01_product_catalog.md | Một factual lookup trực tiếp về cổng, RAM, SSD và công suất sạc trong một đoạn duy nhất. |
| M04 | Medium | 08_accounts_privacy_and_security.md; 02_orders_and_payments.md | Cần kết hợp quy trình bảo mật tài khoản với giới hạn hủy/intercept khi đơn đã Packing. |
| H01 | Hard | 09_escalation_and_policy_updates.md | Cần suy luận policy version theo ngày đặt hàng, nhưng đếm cửa sổ từ ngày giao và không áp dụng OrbitPlus hồi tố. |

**Điểm khó nhất khi xây dựng expected answer hoặc evidence là gì?**

> *Câu trả lời:*

Khó nhất là viết expected answer vừa đầy đủ các điều kiện, ngoại lệ, mốc thời
gian và số tiền, vừa không thêm suy luận ngoài corpus. Các câu hard phải kết hợp
nhiều đoạn nhưng vẫn giữ từng claim truy vết được về evidence nguyên văn.

**Xác nhận:**

- [x] Mọi claim trong expected answer đều có evidence hỗ trợ.
- [x] Không có questions trùng ý và không dùng kiến thức ngoài corpus.
- [x] `python validate_golden_dataset.py` báo `PASS`.

### Exercise 3.2 — Benchmark Run

Chạy:

```bash
python domain_assistant.py
python evaluate_answers.py
```

Copy bảng terminal vào đây hoặc điền từ `artifacts/benchmark_results.json`.

| ID | Question (short) | Ctx Recall | Ctx Precision | Faithfulness | Relevance | Completeness | Overall | Passed? | Failure Type |
|---|---|---:|---:|---:|---:|---:|---:|---|---|
| E01 | | | | | | | | | |
| E02 | | | | | | | | | |
| E03 | | | | | | | | | |
| E04 | | | | | | | | | |
| E05 | | | | | | | | | |
| M01 | | | | | | | | | |
| M02 | | | | | | | | | |
| M03 | | | | | | | | | |
| M04 | | | | | | | | | |
| M05 | | | | | | | | | |
| M06 | | | | | | | | | |
| M07 | | | | | | | | | |
| H01 | | | | | | | | | |
| H02 | | | | | | | | | |
| H03 | | | | | | | | | |
| H04 | | | | | | | | | |
| H05 | | | | | | | | | |
| A01 | | | | | | | | | |
| A02 | | | | | | | | | |
| A03 | | | | | | | | | |

**Aggregate Report**

- Overall pass rate: ____%
- Avg Context Recall: ____
- Avg Context Precision: ____
- Avg Faithfulness: ____
- Avg Relevance: ____
- Avg Completeness: ____
- Failure type distribution: ____

**Ba cases có Overall Score thấp nhất**

1. ID: ____ | Score: ____ | Failure type: ____
2. ID: ____ | Score: ____ | Failure type: ____
3. ID: ____ | Score: ____ | Failure type: ____

**Nhận xét ngắn:** Metric nào yếu nhất? Kết quả gợi ý vấn đề nằm ở retrieval
hay generation?

> *Câu trả lời:*

### Exercise 3.3 — LLM-as-a-Judge Rubric Design

Thiết kế rubric domain-specific cho OrbitTech Customer Support. Mỗi mức phải
đủ cụ thể để hai người chấm độc lập có thể hiểu giống nhau.

Chọn 3–5 dimensions:

- [x] Correctness
- [x] Completeness
- [x] Relevance
- [x] Evidence/citation
- [x] Actionability
- [x] Safety/privacy
- [x] Tone/clarity
- [ ] Dimension khác: __________

| Score | Tiêu chí domain-specific | Ví dụ response |
|---:|---|---|
| 5 | Correct and fully grounded; answers every requested part; preserves all applicable dates, amounts, conditions, exceptions, and safety/privacy limits; gives a clear next step without claiming actions the assistant cannot perform. | “Because the order is Packing, cancellation is not guaranteed. Support may request interception, but success is not guaranteed and the fee is non-refundable.” |
| 4 | Correct and grounded with one minor non-critical omission; direct, safe, and actionable; no invented policy. | Correctly explains the 14-day opened return and 10% fee but omits refund timing that was not central to the question. |
| 3 | Mostly correct but misses one material condition or exception, or includes harmless irrelevant detail; still safe and useful. | Gives the correct return window but omits that a verified defect removes the restocking fee. |
| 2 | Contains a significant policy error, unsupported promise, or misses several required steps; only partially useful, but does not create an immediate severe safety/privacy risk. | Says Packing orders can always be cancelled, although the policy says cancellation is not guaranteed. |
| 1 | Wrong, irrelevant, fabricated, unsafe, privacy-violating, or follows prompt injection; fails the customer's core need. | Requests an OTP, reveals private data, advises continued use of a swollen device, or invents a guaranteed refund. |

**Ba edge cases khó chấm**

| Edge Case | Tại sao khó chấm? | Rubric xử lý thế nào? |
|---|---|---|
| Correct policy but overly long answer | Verbosity can look like completeness even when it adds no value. | Score only atomic required claims; repetition earns no credit and irrelevant text reduces relevance. |
| Concise safety refusal | Low lexical overlap can understate quality even though refusal is correct. | Award full credit when the scope/safety action and a supported alternative are present. |
| Correct general rule but wrong policy version | Most wording may be accurate while the date-dependent result is wrong. | A wrong triggering date/version is a material correctness error and caps the score at 2. |

**Bias controls:** Rubric hoặc evaluation protocol của bạn giảm position bias,
verbosity bias và self-preference bằng cách nào?

> *Câu trả lời:*

Candidate order and labels are randomized and swapped on a second pass to
control position bias. The rubric scores atomic claims and explicitly gives no
credit for length or repetition to reduce verbosity bias. Judge prompts avoid
revealing the generator identity, use a model-independent reference answer, and
are calibrated against human labels to reduce self-preference. High-risk
disagreements receive human review.

### Exercise 3.4 — Framework Comparison (Bonus +5)

Chỉ làm sau khi hoàn thành 3.1–3.3. Chọn hai framework trong RAGAS, DeepEval
và TruLens; chạy hoặc thiết kế một so sánh có cùng input dataset.

| Tiêu chí | Framework 1: RAGAS | Framework 2: DeepEval |
|---|---|---|
| Setup complexity | Cần chuyển dataset sang input/response/reference/retrieved-context format, cấu hình evaluator LLM và embeddings tùy metric. Phù hợp experiment notebook hoặc evaluation pipeline chuyên cho RAG. | Tạo `LLMTestCase`, gắn metrics và threshold; CLI `deepeval test run` tích hợp theo cách gần pytest. Cấu hình judge model vẫn cần thiết. |
| Metrics available | Mạnh ở RAG: context precision/recall, faithfulness, response relevance và custom metrics; dataset/experiment được tách rõ. | Có answer relevancy, faithfulness, contextual recall/precision, hallucination, G-Eval, conversational và agent/trajectory metrics; mỗi metric trả score và reasoning. |
| CI/CD integration | Có thể chạy script evaluation, lưu experiment và tự viết quality gate từ output; linh hoạt nhưng cần glue code cho pipeline hiện tại. | Có `assert_test()`, per-metric threshold và CLI dành cho CI; failure có thể làm fail build trực tiếp. |
| Kết quả trên cùng dataset | Chưa chạy do chưa có gateway key/kết nối; sẽ dùng đúng 20 actual answers và cùng judge model để so sánh công bằng. | Chưa chạy do chưa có gateway key/kết nối; sẽ dùng cùng input, output, contexts, reference và threshold. |
| Insight rút ra | Lựa chọn tự nhiên nếu trọng tâm là chẩn đoán từng tầng của RAG và experiment analysis. | Thuận tiện hơn khi muốn biến eval thành unit/regression tests và mở rộng sang conversation/agent traces. |

- Scores có nhất quán không?
- Framework nào strict hơn và vì sao?
- Hai framework có tìm ra cùng failure cases không?

> *Phân tích:*

Đây là thiết kế so sánh trước khi chạy, không phải số liệu benchmark giả. Hai
framework phải nhận cùng 20 records, cùng actual answers/retrieved contexts,
cùng judge model và temperature, rồi so sánh rank correlation và giao của top
failures thay vì đòi score tuyệt đối giống nhau. DeepEval có thể strict hơn nếu
threshold và judge rubric của metric native yêu cầu giải thích theo từng test;
RAGAS có thể khác do prompt, decomposition và aggregation riêng. Chỉ được kết
luận framework nào strict hơn sau khi chạy thật. Tài liệu tham khảo:
[RAGAS datasets/experiments](https://docs.ragas.io/en/stable/concepts/datasets/)
và [DeepEval CI/CD](https://deepeval.com/docs/evaluation-unit-testing-in-ci-cd).

### Exercise 3.5 — Retrieval Reranking (Bonus +5)

Mục tiêu: kiểm tra việc đổi thứ tự chunks có tăng Context Precision mà không
thay đổi Context Recall hay không.

1. Chọn ít nhất 5 cases từ `artifacts/actual_answers.json`.
2. Tính Context Recall và Context Precision trước rerank.
3. Implement `rerank_by_overlap()` hoặc một reranker khác.
4. Rerank cùng tập chunks, không thêm hoặc xóa chunk.
5. Tính lại hai metrics và giải thích kết quả.

**Pre-key retrieval-only dry run:** Vì `actual_answers.json` chưa thể sinh khi
gateway chưa kết nối, bảng dưới dùng đúng BM25 retriever, top-k=5, questions và
expected answers của golden dataset. Sau khi có key, cần chạy lại trên trace
trong artifact để xác nhận. Reranker dùng lexical overlap với question và không
thêm/xóa chunk.

| ID | Recall before | Recall after | Precision before | Precision after | Delta Precision |
|---|---:|---:|---:|---:|---:|
| E01 | 0.867 | 0.867 | 0.867 | 0.917 | +0.050 |
| E03 | 0.741 | 0.741 | 0.639 | 0.917 | +0.278 |
| E05 | 0.960 | 0.960 | 0.950 | 1.000 | +0.050 |
| M01 | 0.531 | 0.531 | 0.917 | 0.867 | -0.050 |
| H04 | 0.667 | 0.667 | 0.806 | 0.917 | +0.111 |
| **Avg** | **0.753** | **0.753** | **0.836** | **0.923** | **+0.088** |

**Tại sao Recall dự kiến không đổi?**

> *Câu trả lời:*

Context Recall đo coverage trên union của toàn bộ retrieved chunks. Reranking
chỉ đổi thứ tự của cùng một tập chunks nên union token không đổi; vì vậy recall
before và after phải bằng nhau. Context Precision là rank-aware nên thay đổi
khi chunk relevant được đẩy lên hoặc xuống.

**Khi nào reranking không đủ và cần sửa retriever/query/chunking?**

> *Câu trả lời:*

Reranking không đủ khi evidence cần thiết không nằm trong top-k ban đầu, như
recall rất thấp ở A01 hoặc M01. Khi đó cần sửa query expansion/intent routing,
BM25 vocabulary, chunk boundaries, metadata filters hoặc tăng candidate pool
trước rerank. Kết quả M01 cũng cho thấy lexical overlap với question có thể đẩy
chunk hữu ích cho expected answer xuống dưới; production nên cân nhắc
cross-encoder/semantic reranker và regression-test cả recall lẫn precision.

---

## Part 4 — Reflection (16:35–16:50)

Hoàn thành `reflection.md` bằng kết quả thật từ Exercise 3.2.

---

## Completion Checklist

Hoàn thành kiểm tra cuối trong khoảng 16:50–17:00.

- [x] Tất cả required tests pass.
- [x] `golden_dataset.json` validate thành công.
- [x] Exercise 3.1 hoàn thành trong file JSON và bảng kết quả phía trên.
- [ ] Exercise 3.2 có năm metrics, aggregate report và ba cases thấp nhất.
- [x] Exercise 3.3 có rubric 1–5 và bias controls.
- [ ] `reflection.md` có ba failure analyses và regression strategy.
- [x] Đã copy `template.py` thành `solution/solution.py`.
- [x] Exercise 3.4 đã thiết kế; Exercise 3.5 đã có pre-key dry run và cần xác nhận lại từ artifact.
