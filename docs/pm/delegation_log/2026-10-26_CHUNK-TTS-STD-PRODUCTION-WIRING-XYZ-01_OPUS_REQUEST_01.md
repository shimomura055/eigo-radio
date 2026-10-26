## 管理ID
CHUNK-TTS-STD-PRODUCTION-WIRING-XYZ-01 Opus独立技術レビュー(PM_GOVERNANCE 11-3 条件A: Standardの6%減速×段落境界Chunk分割+0.2秒ポーズの合成という新処理フロー。X/Y Std側は既定方針どおりの実装が先行済み[Fable許可条件内]、Z Std側は設計のみ。実装後レビューとして、必要なら修正をM/Rで示す)。read-only、JPY0。

## 性質/到達上限Status/禁止事項
レビューのみ。所見はFableが照合しPM判断する。ユーザー正式承認(2026-10-26、APPROVED_FOR_PRODUCTION): X=段落境界分割(B0.2)+0.2秒、Y=Xと同じ、Z=約70語を目安とした段落境界分割(B_r1)+0.2秒、いずれもStandard/Advanced。「Standardを除外することは認めない」「承認済みTrial B0.2/B_r1の規則を維持し、Standardにも正式適用する」「Standardの既存6%減速とChunk分割・0.2秒ポーズの合成を適切に設計する」「初回Production生成、retry、fallback、regeneration、resumeへ一貫して反映する」「X/Zで既に確認済みのAdvanced動作を回帰させない」。Yは「文境界分割や本文契約の変更を追加承認したものではない」。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)
E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: 読込効率=Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。修正範囲の線引き(PM_GOVERNANCE 11-8)=範囲外は受理面・閾値・方式の新設/拡大、範囲内は承認済み仕様・設計原則との矛盾(仕様文と実装の乖離・論理的に不整合な比較)の是正とそのRegression・検証。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要。
T-0: read-only(委任文保存・checkはFable側)。T-2: TTSなし。T-3: Capなし。

## レビュー依頼
正本=`C:\Users\tensh\eigo-radio\docs\research\CHUNK-TTS-STD-PRODUCTION-WIRING-XYZ-01\OPUS_REVIEW_REQUEST_01.md`(全文Read)。Fable重点:
1. **合成方式**: chunkごとに既存`generate_a2_segment_with_slowdown`(TTS→6%減速→減速後ASR再検証)→減速後に4800サンプル(0.2秒)無音を挿入→連結。連結後減速を採らない理由(ゼロ連続長4569≠4800、合成長検査不成立)は妥当か。Stdのmargin(各側0.16〜0.35秒)が6%伸びて可聴ポーズがAdvより境界あたり約0.02〜0.04秒長くなる点は「承認どおり0.2秒追加」の範囲内と言えるか(新基準・補正を入れない前提)。
2. **共有Gateの穴と補い方**: `_segment_missing_mandatory_a2_slowdown`(`er003_v1_n3_01_assemble.py`)がchunk idを対象外にし、chunk化した親が`slowdown_applied`/`_original.wav`を持たないため誤ブロックされる問題を、(a)親に「全chunk減速済みのときだけTrue」の集約値、(b)X組立前Gate/Y style gateへchunk単位の減速証跡検査追加、で補った設計。集約値が「親が減速済みと偽る」抜け道にならないか(前提=親wav=減速後chunkの整数サンプル生連結)。共有moduleを変えずに済ませた判断の是非。
3. **retry/fallback/regeneration/resumeの一貫性**: 通算TTS3回はchunk単位、同一本文・同一版で分割が変わる再計画はSTOP、減速証跡のないcacheは再利用しない、chunk失敗後も後続chunkは続行。抜け(例: 一部chunkのみ減速済みの中間状態でのresume、`--only-segments`でのchunk id指定、HR Lock後の親entry)はないか。
4. **Adv不変**: golden(実装前HEAD bb578265c、X Adv 2 run・Y Adv 2 run)の分割計画バイト一致+`CHUNK_PLANNER_VERSION`不変で十分か。音声生成側(減速なしAdv)の経路に変更が及んでいないかの確認方法。
5. **Z Std設計(DESIGN_01 §6)**: `er117.plan_z_clip`の`level != "b1b"`撤去、`er063:598`撤去、`verify_std_english_slowdown`の`_CLIP_ID_RE`→chunk id対応、`_z_chunk_parent_display`の集約、test書換えを同時に行う計画の妥当性。Zのセリフ経路(別案件で文脈TTS policyを実装済み・runtime evidence取得中)との干渉(narratorのchunk展開が文脈抽出adapterに影響しないか=FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01 DESIGN_02 M-6のadapter前提)。「約70語を目安」を「閾値100語超・k=ceil(語数/100)」と実装している既存解釈(`2026-10-25_FZ-TELL-TALE-HEART-CHUNK-FINAL-01_USER.md:6,13`)の再照合。
6. **Y**: 複数段落入力でのみ発火・実記事(1段落)は不発火=正常、文境界分割・本文契約変更なし、の設計が承認範囲に収まっているか。runtime evidenceとして「複数段落のdev入力1 segment(Std/Adv)」で原文要求(発火の検証と不発火の事実記録)を満たすか。
7. 試聴ページの「Standardは分割対象外」表示の是正を11-8「修正へ進む」で同一委任内に実施した判断の妥当性。

## 事前指定Read一覧
1. `docs/research/CHUNK-TTS-STD-PRODUCTION-WIRING-XYZ-01/{OPUS_REVIEW_REQUEST_01,DESIGN_01,FIX_01,BUDGET_PLAN_01}.md`(DESIGN_01/FIX_01全文)。
2. `er117_chunk_tts_production_01.py` :80-160、`er019_family_x_audio_production_runner_01.py` Grep `std_parent_slowdown_fields|_k|chunk|slowdown`→X Std経路、`er121_family_y_audio_01.py` Grep 同、`er003_v1_n3_01_assemble.py` :225-290, :395-545、`er003_v1_n3_01_tts_generate.py` :194-250, :331-432、`er063_family_z_audio_01.py` :585-610(読取のみ)。
3. 新規test 3ファイル(`er117_std_chunk_wiring_test_01.py`、`er019_x_std_chunk_test_01.py`、`er121_family_y_std_chunk_test_01.py`)のtest名一覧(Grep `def test_`)。
4. `docs/research/CHUNK-TTS-PRODUCTION-AUDIT-XYZ-01/RUNTIME_EVIDENCE_01.md`(既存発火実績)。

## 報告(出力形式)
論点1〜7ごとに「問題なし/要修正(修正案)/ユーザー判断要」+根拠(ファイル:行)。M(必須修正)/R(推奨)番号付き一覧(10件以内、X/Y側は実装済みのため「実装後の是正」として、Z側は「実装前に反映」として区別)。PRODUCTION_WIRED判定に必要なruntime evidenceの過不足(X Std 1記事3 part/Y Std・Adv複数段落dev入力/Z Std 1〜2 clip、で足りるか)。最終行に5行以内の要約。