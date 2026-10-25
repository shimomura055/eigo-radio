# DESIGN_06(Trial-06: Part 2 選定の工程設計見直し = LLMは分類のみ、選定は決定論規則)

管理ID: FAMILY-Z-STUDY-TEXT-TRIAL-01 委任_11 / 日付: 2026-10-25 / Status: DEV/Trial専用。Production採用・配線は未承認。
根拠: `OPUS_REVIEW_04.md`(条件B)、`EVAL_05.md`/`analysis_05*.json`。実装: `run_trial_06.py`/`analyze_06.py`。基準: `PREREGISTERED_CRITERIA_06.md`(Step A'' 生成前commit)。

## 1. 変更の要点(Trial-05 Step A'との差)
| 項目 | Trial-05 | Trial-06 |
|---|---|---|
| LLMの役割 | 全文タグ付け + 文ごとの層A/B/C判定 + rank付け | **全文タグ付けのみ**(分類コード + 取り違えの対象/語句 + 逐語欄)。相対的な難しさ・重要度は答えさせない |
| 揺れの原因だった欄 | tier(A/B/C)・rank | **廃止**(呼出ごとに基準がずれ、全文が層Bで0件になる現象。OPUS_REVIEW_04 (a)) |
| 選ぶ主体 | コード(tier A + 基礎のみでない + 取り違え欄あり) | コード(**2段クラス**: 強INV/CLEFT/CMP・中FRONT/HEAVY/POSTMOD/SPEC/ELL/APPOS、OTHER除外) |
| 優先順位 | LLMのrank | **固定: INV>CLEFT>CMP>FRONT>HEAVY>POSTMOD>SPEC>ELL>APPOS** |
| 埋め草対策 | なし | **中クラスは`misread_target`∈列挙 かつ `misread_quote`が選定文に逐語で含まれる場合のみ適格**、同一クラス・同一段落は1件まで、適格0なら0件 |
| 基礎項目 | 一覧のみ(`basic_only`は18標本で一度もtrueにならず機能せず) | 一覧を拡張(使役/知覚+O+原形/分詞・keep/make/find+O+C基本形・会話断片/間投詞/一語返答・伝達部の同格/挿入を基礎へ)。SPEC・ELL・APPOSの定義を狭める |
| 費用ガード | 呼出開始時点の累計で判定 → 9並列で全callが開始し上限超過(9.11円/8円) | **予約方式**: spent + 実行中の最大見込み額 + 当該callの最大見込み額 <= 上限のときだけ開始。各callに`max_output_tokens=13000`で最大見込み額を保証 |
| `resolve_verbatim` | 引用符付きで返ると解決失敗 | 文頭・文末の引用符を除去してから再照合(`resolve6`) |
| 作品 | 4(猿の手=ホールドアウト) | 6(猿の手=開発用。告げ口心臓=新ホールドアウト。二十年後=平易な本文) |

## 2. Opus条件B指摘の反映対応表
| Opus指摘 | 反映箇所 |
|---|---|
| (b)1 分類を強/中の2段、OTHERは自動選定外 | `STRONG`/`MID`/`PRIORITY`、`base_ok`(OTHER除外) |
| (b)2 中クラスはmisread_target+misread_quote逐語 | `mid_cond`、Promptの`misread_target`欄(列挙)、`parse_stepa6`の`misread_quote_in_sentence` |
| (b)3 同じクラスの2件目は選ばない | `select_main`の`used_cls`(+同一段落`used_para`。Opusのリスク対処「段落単位の重複排除」) |
| (b)4 該当無しは0件 | `select_main`は適格0で`[]`。selftest(j3)で確認 |
| (b)5 rank/tier廃止、basic_only残す | schemaにtier/rank無し、`basic_only`はそのまま |
| (b)6 優先順位を事前登録で固定 | PREREGISTERED_CRITERIA_06 §1 |
| (c) SPEC/ELL/APPOS/INVの最終案 | Promptの分類定義・基礎項目へ反映 |
| (d) (B)n=3集計・2値化・推論量低減は不採用 | 本Trialでは実施しない |
| 必須修正1 費用ガード予約方式 | `Budget`クラス、`hard_cost_jpy`、selftest(30並列で上限不超過・単独不可は拒否・完了待ち) |
| 必須修正2 `resolve_verbatim`の引用符除去 | `strip_quotes`/`resolve6`、selftest |
| 必須修正3 Prompt・規則変更とselftest | `selftest()`(規則6系統+費用ガード4系統) |
| 必須修正4 Prompt例が全作品の本文外 | `leak_check()`(dry-run/selftestでassert。6作品全文と照合) |
| 比較規則はオフラインのみ | `select_cmp_orig`/`select_cmp_nosame`(追加費用0。合否に使わない) |
| `subject_span`/`main_verb`を記録欄に | schemaに追加(規則に使わない) |

## 3. 工程
Step A''(1 call/標本): 番号付き本文のみ入力(KPは渡さない) → JSON(`features[]`: para, sentence[逐語], feature_class, other_desc, misread_target, misread_quote, misread_ja, correct_structure_ja, subject_span, main_verb, basic_only, construct_ja, points_ja[最大2], context_ja / `no_feature_paras[]`)。
解析(コード): 文は`resolve6`で本文側の逐語文字列へ引き当て(解決不能は記録して除外)。前後1文・参考訳(Family X/既存KP文のみ)を自動付与。JSON不正は記録のみ(自動再試行なし)。
選定(コード): `select_main`(PREREGISTERED_CRITERIA_06 §1)。
Step B(Trial-04と同一Prompt。入力の選定文が変わるだけ): 選定文につき日本語訳・仕組み・(比較)・意味・ニュアンスの4点。学習者向け表記(`**見出し**`化)、開発者語禁止は04のまま。`OUTPUT_06_<work>_r1_USER.md`(学習者向けPart 2)と`_DEV.md`(選定記録・usage)を分離保存。
評価語を含みうる欄(misread_ja等)はDEV記録のみで、Step Bへは`reason_dev`として渡すがStep B Promptの`stepb_items`は使用しない(04と同じ)。

## 4. 既存機構との整合・Production境界
- Production側に英語学習テキスト解説は存在しない(DESIGN_04 §1)。本Trialは全てDEV専用で、Production code/Prompt/閾値/flagの変更0。`er003_*`/`er026_*`/`er062_*`等は読み取り(本文入力)のみ。
- 新Checker/Validator新設ではない(生成済みユーザー向け文を検査せず、選定段の分類と決定論規則のみ)。
- 責務分離: 点検・分類(LLM) / 選定(コード) / 執筆(Step B LLM)。LLMの確率的判断は「何の構文か」と「取り違える語句」の事実記述に限定し、「どの構文を教えるべきか」の価値判断は設計(固定優先順位)に移した。この価値判断は事前登録で固定し、VALIDATED報告時にユーザーへ開示する。
- 過剰適合防止: Promptの例は全て自作文(6作品全文との逐語照合をdry-run/selftestでassert)。ホールドアウトを新規に1作品追加し、平易な本文を必須で含める。
- Step Bは材料欄が揃う選定のみ呼ぶ。0件の作品はStep B call無し(固定文のみ)。

## 5. 想定コスト
Step A'' 1 callあたり約0.5〜0.7円(入力約3.5k token + 出力約5〜8k token、provider default reasoning)。6作品×3 = 約9〜13円。ガードで12.6円を超えない。Step B 6 call約1.2円。量産1セットあたり(1作品=Step A'' 1 + Step B 1): 約0.7〜0.9円(70円目標の約1.2%)。
