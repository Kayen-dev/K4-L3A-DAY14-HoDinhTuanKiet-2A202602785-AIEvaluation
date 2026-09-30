# Day 14 — Reflection

## Evaluation Report & Failure Analysis

Dùng kết quả thật trong `artifacts/benchmark_results.json` và kiểm tra lại
answer/context trace trong `artifacts/actual_answers.json` trước khi kết luận.

---

## 1. Benchmark Results Summary

**Overall pass rate:** ____%

| Metric | Average | Min | Max | Nhận xét |
|---|---:|---:|---:|---|
| Context Recall | | | | |
| Context Precision | | | | |
| Faithfulness | | | | |
| Relevance | | | | |
| Completeness | | | | |
| Overall Score | | | | |

**Score interpretation**

- Metrics/cases ở mức Good (0.8–1.0): ____
- Metrics/cases ở mức Needs Work (0.6–0.8): ____
- Metrics/cases ở mức Significant Issues (<0.6): ____

**Failure type distribution**

| Failure Type | Count | Percentage |
|---|---:|---:|
| hallucination | | |
| irrelevant | | |
| incomplete | | |
| off_topic | | |
| refusal | | |

**Chẩn đoán tổng quan:** Vấn đề chính nằm ở retrieval, generation hay cả hai?
Dùng ít nhất hai metrics để bảo vệ kết luận.

> *Câu trả lời:*

---

## 2. Top 3 Worst Failures — 5 Whys

Phân loại failure trước khi đề xuất fix. Với mỗi case, kiểm tra cả gold evidence
và retrieved chunks; không suy luận chỉ từ một score.

### Failure 1

**ID và question:**

> *Điền:*

**Expected answer:**

> *Điền:*

**Actual answer:**

> *Điền:*

**Scores:** Context Recall: ____ | Context Precision: ____ | Faithfulness: ____ |
Relevance: ____ | Completeness: ____ | Overall: ____

**Evidence inspection:** Retriever lấy đúng/thiếu/thừa chunks nào?

> *Câu trả lời:*

| Level | Question | Answer |
|---|---|---|
| Symptom | Vấn đề quan sát được là gì? | |
| Why 1 | Tại sao symptom xảy ra? | |
| Why 2 | Tại sao nguyên nhân trên xảy ra? | |
| Why 3 | Tại sao vấn đề đó chưa được ngăn chặn? | |
| Why 4 | Tại sao cơ chế hiện tại chưa phát hiện hoặc xử lý được? | |
| Why 5 | Root cause có thể hành động được là gì? | |

**Root cause từ `find_root_cause()`:**

> *Paste output:*

**Bạn đồng ý hay không? Dẫn evidence từ trace:**

> *Câu trả lời:*

**Proposed fix cụ thể:**

> *Câu trả lời:*

### Failure 2

**ID và question:**

> *Điền:*

**Expected answer:**

> *Điền:*

**Actual answer:**

> *Điền:*

**Scores:** Context Recall: ____ | Context Precision: ____ | Faithfulness: ____ |
Relevance: ____ | Completeness: ____ | Overall: ____

**Evidence inspection:**

> *Câu trả lời:*

| Level | Question | Answer |
|---|---|---|
| Symptom | Vấn đề quan sát được là gì? | |
| Why 1 | Tại sao symptom xảy ra? | |
| Why 2 | Tại sao nguyên nhân trên xảy ra? | |
| Why 3 | Tại sao vấn đề đó chưa được ngăn chặn? | |
| Why 4 | Tại sao cơ chế hiện tại chưa phát hiện hoặc xử lý được? | |
| Why 5 | Root cause có thể hành động được là gì? | |

**Root cause và proposed fix:**

> *Câu trả lời:*

### Failure 3

**ID và question:**

> *Điền:*

**Expected answer:**

> *Điền:*

**Actual answer:**

> *Điền:*

**Scores:** Context Recall: ____ | Context Precision: ____ | Faithfulness: ____ |
Relevance: ____ | Completeness: ____ | Overall: ____

**Evidence inspection:**

> *Câu trả lời:*

| Level | Question | Answer |
|---|---|---|
| Symptom | Vấn đề quan sát được là gì? | |
| Why 1 | Tại sao symptom xảy ra? | |
| Why 2 | Tại sao nguyên nhân trên xảy ra? | |
| Why 3 | Tại sao vấn đề đó chưa được ngăn chặn? | |
| Why 4 | Tại sao cơ chế hiện tại chưa phát hiện hoặc xử lý được? | |
| Why 5 | Root cause có thể hành động được là gì? | |

**Root cause và proposed fix:**

> *Câu trả lời:*

---

## 3. Failure Clustering

Một root cause có thể tạo ra nhiều failures. Nhóm theo nguyên nhân có thể sửa,
không chỉ nhóm theo tên metric.

> Phần ID và priority sẽ được chốt từ benchmark thật. Trước benchmark, ba
> cluster dùng để phân loại là: (1) retriever bỏ sót evidence, (2) ranking đưa
> noise lên trước evidence, và (3) generator bỏ sót hoặc thêm claim không được
> context hỗ trợ.

| Cluster | Root Cause | Failure IDs | Priority |
|---|---|---|---|
| 1 | | | High/Medium/Low |
| 2 | | | |
| 3 | | | |

**Nếu chỉ được sửa một cluster, bạn chọn cluster nào và vì sao?**

> *Câu trả lời:*

---

## 4. Improvement Log

Paste output của `generate_improvement_log()`:

```text
[paste Markdown table here]
```

Improvement log cần được sinh từ đúng ba failures thấp nhất sau benchmark;
không điền dữ liệu giả trước khi có `benchmark_results.json`.

**Ba improvement suggestions ưu tiên**

1. ____
2. ____
3. ____

Với mỗi suggestion, nêu metric dự kiến thay đổi và cách đo lại.

| Suggestion | Target metric | Verification method |
|---|---|---|
| | | |
| | | |
| | | |

---

## 5. Regression Testing Strategy

**Câu 1: Khi nào chạy `run_regression()` trong production workflow?**

> *Câu trả lời:*

Chạy trên pull request có thay đổi prompt, model, retriever, chunking, corpus
hoặc evaluation code; chạy lại trước release; và chạy định kỳ trên một snapshot
production đã ẩn dữ liệu nhạy cảm. Baseline phải được version cùng model,
prompt, corpus và dataset để so sánh có ý nghĩa.

**Câu 2: Threshold drop 0.05 có phù hợp OrbitTech Customer Support không? Vì sao?**

> *Câu trả lời:*

Ngưỡng giảm hơn 0.05 phù hợp làm quality gate tổng quát của lab vì đủ lớn để
tránh chặn bởi dao động nhỏ. Tuy nhiên production nên dùng ngưỡng chặt hơn hoặc
zero-tolerance cho safety/privacy và hallucination policy nghiêm trọng, đồng
thời dùng nhiều lần chạy hoặc confidence interval trước khi kết luận regression
do model không hoàn toàn deterministic.

**Câu 3: Metric/failure nào phải block deployment, metric nào chỉ alert?**

> *Câu trả lời:*

Block deployment khi Faithfulness dưới 0.80, khi bất kỳ case safety/privacy
hoặc prompt-injection nào thất bại, hoặc khi một answer metric trung bình giảm
hơn 0.05 so với baseline. Relevance/Completeness giảm nhỏ nhưng chưa vượt
ngưỡng có thể alert để điều tra; Context Precision thấp có thể alert nếu Recall
và answer quality vẫn đạt, nhưng Context Recall thấp trên case bắt buộc phải
block vì evidence cần thiết đã bị bỏ sót.

**Câu 4: Điền evaluation stages vào flow.**

```text
Code/prompt/retrieval change → [Unit + dataset validation] → [Offline benchmark + regression gate] → [Human review for high-risk failures] → Deploy
```

> *Giải thích:*

Unit tests bảo vệ công thức và wiring; validator bảo vệ schema/provenance.
Benchmark đo chất lượng end-to-end so với baseline. Human review xử lý các case
safety, privacy, policy-version và các bất đồng mà word-overlap không đánh giá
được tin cậy. Sau deploy, online monitoring tiếp tục phát hiện drift.

---

## 6. Continuous Improvement Loop

```text
Evaluate → Analyze → Improve → Augment benchmark → Repeat
```

| Priority | Action | Metric dự kiến cải thiện | Expected impact |
|---:|---|---|---|
| 1 | Bổ sung query expansion/intent routing cho case có evidence không xuất hiện trong top-k. | Context Recall | Tăng khả năng lấy đủ policy, điều kiện và ngoại lệ cần cho câu trả lời. |
| 2 | Rerank candidate chunks bằng semantic/cross-encoder và kiểm tra thứ tự bằng regression set. | Context Precision, Faithfulness | Đưa evidence lên trước noise, giảm khả năng generator bám vào policy sai. |
| 3 | Thêm checklist generation cho dates, amounts, conditions, exceptions và scope limitations. | Completeness, Faithfulness | Giảm bỏ sót claim bắt buộc và ngăn lời hứa không được policy hỗ trợ. |

**Hai hoặc ba failure cases nào cần thêm vào benchmark ở vòng tiếp theo?**

> *Câu trả lời:*

Ưu tiên bổ sung các case production có Context Recall thấp, case đúng general
rule nhưng sai policy version theo ngày, và case adversarial mà câu trả lời an
toàn bị heuristic lexical chấm thấp. ID cụ thể sẽ lấy từ ba failures thấp nhất
sau benchmark để tránh chọn theo giả định.

---

## 7. Final Reflection

**Điều gì trong kết quả benchmark trái với dự đoán ban đầu của bạn?**

> *Câu trả lời:*

Chưa thể kết luận trước benchmark thật. Kết quả retrieval-only ban đầu cho thấy
một điểm đáng chú ý: lexical reranking tăng Context Precision trung bình trên
mẫu 5 case nhưng làm M01 giảm 0.050, chứng minh reranking theo overlap không
đảm bảo cải thiện từng case. Phần này sẽ được cập nhật bằng answer metrics sau
khi gateway sinh đủ 20 actual answers.

**Word-overlap heuristics trong lab có giới hạn gì? Nếu đưa hệ thống vào
production, bạn sẽ thay hoặc bổ sung metric nào?**

> *Câu trả lời:*

Word overlap không hiểu paraphrase, phủ định, quan hệ logic, đúng/sai của số và
ngày, hay việc một câu tuy dùng đúng từ nhưng diễn giải sai chính sách. Nó cũng
có thể phạt một refusal ngắn nhưng an toàn và thưởng câu copy context mà không
giải quyết intent. Trong production, tôi sẽ bổ sung claim-level entailment cho
faithfulness, semantic answer relevance, LLM-as-a-Judge đã calibrate với human
labels, deterministic checks cho dates/fees/policy versions, safety/privacy
tests, cùng business metrics như escalation accuracy và resolution rate.
