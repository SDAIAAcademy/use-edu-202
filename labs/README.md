# تقديم منهج البيانات والذكاء الاصطناعي في مختلف التخصصات: المختبرات

ثمانية مختبرات لمقرر أكاديمية سدايا **USE-EDU-202**. المختبرات صفحات إرشادية بالعربية: ما تخرج به، والملفات، وخطوات
بدقائقها وأوامر تُنسخ، وأسئلة تحقق، ومهمة إضافية ✱، وملاحظات للمدرّب. لا كود يكتبه المشارك.

كل المختبرات في جهة واحدة: **عمادة التطوير الأكاديمي في جامعة الدَّهناء**، جامعة افتراضية، ومساعدها «مِداد».
كل الأسماء واللوائح والخطط والأرقام مخترعة. الحقيقي الوحيد هو بنية المنهج الوطني في `files/curriculum_card.txt`،
وهي مكتوبة بكلمات الفريق وليست نصه.

## ما يحتاجه المشارك

- متصفح، والمساعد المرخص في جامعته أو حساب مجاني في مساعد عام. لا يُنزَّل أي نموذج على الجهاز.
- برنامج جداول يفتح ملفات CSV، أو ورقة وقلم.
- وثيقة المنهج، وتوصيف مقرره أو برنامجه بلا أسماء طلبة ولا درجات.

## سياسة الذكاء الاصطناعي

| المستوى | أين |
|---|---|
| دون ذكاء اصطناعي | المختبر 1.1 كله، والخطوة 2 من المختبر 2.3 |
| ذكاء اصطناعي مرشد | بطاقات التيسير في المختبرات 1.2 و1.3 و1.4، والخطوة 2 من المختبر 2.1 |
| ذكاء اصطناعي كامل، مع إفصاح | المختبران 1.5 و2.2 |
| المساعد موضوع الاختبار | الخطوات الأولى من المختبرات 1.2 و1.3 و1.4 |

## نقطة البداية والحل

كل مختبر يبدأ من ملفات جاهزة ولا يعتمد على مختبر آخر. المختبر 2.1 يستفيد من مصفوفة المختبر 1.5 ولا يشترطها.

| المختبر | الصفحة | المدة | يبدأ من | الحل المرجعي |
|---|---|---|---|---|
| 1.1 | `D1_1_alignment_summary.html` | 25 دقيقة | `files/curriculum_card.txt`، `files/alignment_summary.csv` | `solutions/alignment_summary_key.csv`، `solutions/alignment_paragraph.txt` |
| 1.2 | `D1_2_prediction.html` | 35 دقيقة | `files/attendance_table.txt`، `files/prediction_tests.txt`، `files/prediction_sheet.csv`، `files/midad_runs_prediction.txt` | `solutions/prediction_reference.csv`، `solutions/facilitation_card_prediction.txt` |
| 1.3 | `D1_3_red_team.html` | 35 دقيقة | `files/redteam_rules.txt`، `files/dahna_absence_bylaw.txt`، `files/redteam_probes.txt`، `files/redteam_log.csv`، `files/midad_runs_redteam.txt` | `solutions/redteam_log_reference.csv`، `solutions/facilitation_card_red_team.txt` |
| 1.4 | `D1_4_coverage.html` | 35 دقيقة | `files/coverage_prompt.txt`، `files/coverage_grid.csv`، `files/midad_runs_coverage.txt` | قياس `dahna_tools.py coverage`، `solutions/facilitation_card_coverage.txt` |
| 1.5 | `D1_5_alignment_matrix.html` | 45 دقيقة | `files/delivery_models.txt`، التوصيفات الثلاثة، `files/matrix_distributed.csv`، `files/matrix_template.csv` | فحص `dahna_tools.py matrix`، `solutions/matrix_embedded_reference.csv` |
| 2.1 | `D2_1_adapt_lab.html` | 60 دقيقة | `files/recommended_labs.txt`، `files/lab_card_template.txt`، `files/adaptation_checklist.txt`، `files/lab_card_flawed_business.txt` | `solutions/lab_card_reference_nursing.txt` |
| 2.2 | `D2_2_track_pack.html` | 45 دقيقة | `files/track_rules.txt`، `files/pack_template.txt`، `files/pack_health_model.txt`، `files/pack_business_draft.txt`، `files/mini/` | `solutions/pack_review_reference.txt` |
| 2.3 | `D2_3_calibration.html` | 50 دقيقة | `files/shared_rubric.txt`، `files/plans/`، `files/marks_sheet.csv` | `solutions/reference_marks.csv`، `solutions/moderation_rules_example.txt` |

للمشروع الختامي: `files/observation_rubric.txt`، `files/microteach_plan_template.txt`، `files/delivery_plan_checklist.txt`،
ومثال في `solutions/microteach_plan_example.txt`.

## للمدرّب: المفتاح والأدوات

- `solutions/answer_key.md`: كل ما زُرع في الملفات، وأين، وأي مختبر يكشفه، والأرقام المرجعية.
- `solutions/dahna_tools.py`: سبع أدوات فحص بسيطة ومقروءة. لا تغني واحدة منها عن قراءة عمل المشارك.
- `solutions/stand_in_midad.py`: نموذج بديل مكتوب، وليس نموذجًا لغويًّا. يكتب تشغيلات «مِداد» المسجلة من
  `solutions/midad_script.json` ليُنفَّذ كل مختبر ويُفحص حله دون اتصال ودون مفتاح.
- `solutions/run_all.py`: يشغّل كل ما سبق ويطبع PASS أو أول اختلاف.

الأدوات مكتوبة بمكتبة Python القياسية وحدها، وتُشغَّل بـ`uv` من جذر المستودع:

```
uv run labs/_tools/prepare_files.py
uv run labs/solutions/run_all.py
uv run labs/solutions/dahna_tools.py alignment labs/solutions/alignment_summary_key.csv
uv run labs/solutions/dahna_tools.py matrix labs/files/matrix_distributed.csv
uv run labs/solutions/dahna_tools.py card labs/files/lab_card_flawed_business.txt
uv run labs/solutions/dahna_tools.py pack labs/files/pack_business_draft.txt labs/files/mini_business_draft.csv
uv run labs/solutions/dahna_tools.py coverage labs/files/midad_runs_coverage.txt
uv run labs/solutions/dahna_tools.py marks labs/solutions/reference_marks.csv
uv run labs/solutions/dahna_tools.py room labs/solutions/room_marks_before.csv
```

الأول يعيد كتابة `files/` وملفات الحل المرجعية ببذرة ثابتة (202): البايتات نفسها في كل تشغيل.

## ما لم يُشغَّل على نموذج لغوي

الخطوات التي يُسأل فيها مساعد حي (المختبرات 1.2 و1.3 و1.4، وأوامر الصياغة في 1.5 و2.1 و2.2) لم تُشغَّل على
نموذج لغوي عند إعداد المقرر. التشغيلات المسجلة من النموذج البديل المكتوب، وزُرع فيها التفاوت والأخطاء عمدًا ليكون
للمختبر مرجع ثابت. سلوك المساعدات يختلف من نموذج لآخر ومن شهر لآخر: جرّب الأوامر الثلاثة على المساعد الذي ستستخدمه
القاعة قبل أول دفعة، وسجّل ما يختلف عن التسجيل. الاختلاف لا يُفسد المختبر: يُناقَش فيه.
