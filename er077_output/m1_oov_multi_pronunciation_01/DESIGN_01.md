# DESIGN_01 M1 OOV 複数発音候補方式(ユーザー追加承認に基づく再設計)

管理ID: ASR-M1-OOV-MULTI-PRONUNCIATION-PRODUCTION-01 委任_01 / 到達上限Status: `WIRING_DESIGN_DRAFT`(Opus条件A待ち)/ 費用JPY0 / Production py無変更 / Ledger読取のみ
実装コード(offline評価): `er077_m1_oov_multi_pronunciation_01_eval.py`(unit test `..._test_01.py` 14件PASS)/ 数値・全件: `EVAL_01.md`・`eval_01.json`
上流: `er075_output/m1_f1_production_wiring_01/{OOV_SAFETY_01,M1_WIRING_DESIGN_01,F1_FIX_DESIGN_01}.md`(OF-163〜168反映事項を正とする。`docs/pm/OPUS_FINDINGS_LEDGER_01.md`は本worktreeに存在せず、委任文記載の要約を正とした)

## 0. 結論(先に)
1. **C1(CMU全異読)+C2(Ledger全発音)だけで Melos said 12件は 12/12(従来4/12)**。C3(規則G2P)は不要=STOP論点にならない。
2. 12件の一致は**全て `C2_ledger_alt`(confidence=low、Tier3が自動調査で書いた「音楽用語としての別読み」`/ˈmɛloʊs/`)**。Ledgerの「主発音」`/ˈmiː.lɑːs/` が一致した行は0件。つまりこの12/12は「システムが書いた低信頼の推測」に依存している(ユーザー承認下で許容されるが、報告で明示する)。
3. 674ペアでの新規PASS(M1起因)は13件(全てMelos、出典は同じLedgerエントリ1件)。F1反例19件は19/19期待どおり、合成24ケースは24/24期待どおり(本設計起因の想定外0)。「誤PASS候補として人手確認すべきもの」は8節。
4. 一般化の実力は**現Ledgerでは Melos 1語のみ**(CMU未収録かつIPA変換可の単一語は11語、うち候補が2つ以上あるのは4語)。他の固有名詞への効果はLedgerのエントリ増(=運用)に比例する。本設計は「Ledgerが候補を持てば使う」仕組みであり、辞書の完全性は目的化しない。

## 1. 候補集合(事前固定・ASR非依存)
| クラス | 出典 | 適用 | 採否 |
|---|---|---|---|
| C1 `C1_cmu_variant` | CMU(`pronouncing`)の全異読(`phones_for_word`) | CMU収録語。ただし固有名詞らしき語(`entity_like`)は既存M1の保守基準どおり**代表(先頭)発音のみ**(F2維持。全異読へ広げた感度分析=674ペアで追加PASS 0件) | 採用(既存挙動) |
| C2 `C2_ledger_expected` / `C2_ledger_alt` | Pronunciation Ledger の `expected_pronunciation_ipa` と `alternate_pronunciations` のIPA断片(confidence不問) | **CMU未収録語のみ**・単一トークンsurfaceのみ・`entity_type=ja_reading_katakana`は除外・「native/Swedish/Italian…」等の非英語ラベル直後の断片は除外・IPA→ARPAbet変換不能な断片は**候補不成立として記録** | 採用 |
| C3 規則G2P(綴りから推定) | 綴り→音素の規則推定 | — | **今回不採用**(Fable既定どおり。12/12に不要だったためSTOP論点にならない) |
| (禁止) | ASR転写側の綴りを近似して期待発音を作る(Trialの`oov_spelling_fallback`) | — | **不採用**(後付けに近い。`Cleos→Clio`を通す欠点が実証済み) |

- **C2をCMU未収録語に限る理由**: Ledgerには「surface=`us` → IPA `/ʌnˈnoʊn/`」「`plus`→`kæsˈkeɪd`」のような誤エントリが実在する(Tier3の自動調査由来)。CMU収録語は辞書を信頼し、Ledgerの誤りが一般語の判定へ波及しないようにする。
- **IPA→ARPAbet**: 既存変換は無かったため決定論表を新設(`IPA_TABLE`)。UK `ɒ`→`AA`、`ɜː/ɝ/ɚ/ər`→`ER`、`oʊ/əʊ`→`OW`。Ledgerの綴り読み(`oh-TOH-nee`等のpronunciation_hint/非IPAのalternate)は**変換しない**(新たなG2Pになるため)。
- **事前固定の技術的担保**: `candidates_for(word, ledger)` の引数にASRは無い(unit testでsignature検査)。判定前に`fix_candidates(canonical)`で全トークンの候補集合+ハッシュを確定し、判定後に再計算して一致を確認、`candidates_fixed_before_asr=true`をauditへ。
- **上限**: 語あたり `CAP=6`(C1→C2 expected→C2 alt の順、同一音素列は統合し出典を`also_from`へ併記)。超過は切捨て+`overflow_dropped`を記録。現Ledgerの最大は4候補(melos)。Ledger全体37エントリ(low14/medium12/high11)、C2が使える語11。

## 2. 判定
各候補から`forms_from()`が、既存Pattern(厳密一致/A=語末S・Z1つ除去/B=-ed除去/C=-s付加)が受理側として期待する音素列を導く(`derived_phone_forms`と同じ規則を候補ごとに適用)。ASR側同音綴りがいずれかの候補のformに一致すれば、**既存M1と同じ流れ**(置換→Production既存判定=protected_check+entity gate+Pattern A/B/C+F1全差分点検→受理理由が純粋同音・Pattern A/B/C系のみ)へ進む。
- 差し替えるのは**`phoneme_ok`の『canonical側の音素集合』だけ**(O.phoneme_okの置換。他は無変更=既存機構再利用)。OOVで候補0なら`False`(従来のOOV fallback=綴り基準へは戻らない)。
- 受理理由: `M1_MULTI_CANDIDATE_ACCEPT`(PASS_WITH_WARNING)。audit: `original_asr / normalized_asr / subs(from,to,canonical_word,出典クラス,confidence,音素列,ledger_key,rule) / candidates(出典・confidence・音素列・overflow・unconvertible・excluded) / candidates_fixed_before_asr`。
- 候補全不成立→判定を変えない(既存のretry/fallback/HR上限そのまま)。
- **Secondary同意(fallback/forced-secondary)**: 両エンジンがM1で受理され、同一canonical語について**共通の候補音素列**で成立すること(`secondary_agree`)。12件では11/12(行11はOpenAI=`Mella`で不成立。他は両エンジン同一候補`M EH L OW S`で成立、または片方が元からEXACT/PASS)。

## 3. F1との整合(経路図)
```
Primary判定 -> should_pass? --YES--> PASS(M1は呼ばない)
   | NO
   v
_step_alternate_pass(CMU同音Case A) --PASS--> PASS
   | 未PASS かつ ASR_VALIDATION_UNCERTAIN かつ protected_check通過(数字/否定OK)
   v
M1: ASR差分トークン -> canonical語の候補集合(事前固定)とCMU音素照合 -> 置換文を作る
   v
置換文 -> Production既存判定(F1: 全差分点検。残差0のみACCEPT)
   |  残差あり(別の語・時制・数値・否定・欠落・余り) -> 不受理(UNCERTAIN維持)
   |  残差0かつ受理理由が純粋同音/Pattern A/B/C -> M1_MULTI_CANDIDATE_ACCEPT (PASS_WITH_WARNING + audit)
```
M1は**F1の残差点検の内側**で動き、entity残差の説明にのみ使われる。「M1成立+他の内容差分」は置換文のF1点検で必ず非PASS(合成: dogs/cats、not有無、5/6、slept/sleep、語句欠落すべて非PASS)。F1の承認済み是正(benign限定、`residual_kind`、Eq Layerの残差1件のみ評価)とは矛盾しない(M1はそれらより前段のUNCERTAINを入口にするだけ)。

## 4. 適用点(委任_02の実装範囲。本委任は設計のみ)
| 経路 | 適用 | 備考 |
|---|---|---|
| Primary#1 / P2 / S1 / S2 | **適用** | 各stepの`should_pass`判定と`_step_alternate_pass`の後(OF-165)。cascade_eligible early returnより前 |
| forced-secondary(`er006_secondary_asr_01.py` L711付近、OF-163) | **適用** | Secondary同意条件は2節 |
| 減速後再検証(`er003_v1_n3_01_tts_generate.py` L146 rescue、L196は直接`classify_asr_match`、OF-164) | **L146 rescue経由のみ** | auditは`post_slowdown_cascade` |
| dialogue / point_headings_aoede | 適用(`segment_id`非依存) | |
| `cascade_enabled=False` | **不発**(OF-165) | |
| 言語 | `en-US`以外は不発 | `m1_enabled`既定True |
| **KP(論点)** | 下記 | |

### KP適用の両案(設計論点・Fable既定=KPにも適用、C1+C2のみ)
- 案K-A(Fable既定): KPにも適用。ユーザー指示「KPを含む関連英語ASR経路」と整合。F1全差分点検は共有関数のため自動適用。影響: KPのHR/regenが減る可能性(KP実データは本評価に0件=`kp_pairs_added=0`。効果は未測定)。リスク: 短句は1語の誤転写が全体に占める割合が大きく、誤PASS時の影響が相対的に大きい(候補はC1+C2のみ・同じaudit)。
- 案K-B: KPは`m1_enabled=False`(OF-164のKP呼出側`enable_non_latin_cascade=True`経路)。ユーザー指示の文面と不整合になる恐れ。
- **賛否**: 案K-Aに賛成。ただし委任_02で**KP実データの効果測定(read-only)**を先に行い、新規PASSがあれば全件を人手確認してから配線を確定する条件を推奨。

## 5. Ledgerとの関係
- **読取のみ**。低信頼→高信頼の書換なし(候補のconfidenceはそのままauditに出る。unit testで保持を検証)。評価前後でLedgerのmd5不変を確認済み(`eval_01.json`)。
- 書込側: `er006_secondary_asr_01.py` L227-248(Tier3自動調査→`pronun_ledger.upsert`、`entity_type=cascade_unresolved_entity`)。**運用で候補が増える経路はこれだけ**。Tier3の調査結果がそのまま次回以降のM1候補になる(自己強化の循環に注意)。
- 運用上限・監査(提案): (a)語あたりCAP=6(コード側)、(b)M1受理のauditに`ledger_key`と`updated_at`を残し、Ledger由来の受理を事後集計できるようにする、(c)Ledgerエントリが自動生成か人手確定かを区別する専用フィールドは無く、現状は`entity_type`/`resolution_method`で区別(`cascade_unresolved_entity`=自動)。専用フィールド追加は新規仕様のため**要判断(OPEN)**。
- Tier3が書く別読みが「ASR誤転写の実在語に偶然一致する別読み」を含む可能性(主発音が`MEE-lahs`なのに別読み`/ˈmɛloʊs/`が`Mello/Mellow`を通す)は残る。これはユーザー承認(複数の合理的候補の1つで可)の範囲内の挙動で、本設計では排除しない。排除するなら主発音のみ(=4/12に戻る)で、ユーザー承認と逆になる。

## 6. 誤PASS / 誤NGのバランス(§6、1000本あたり1〜2本目標)
- **誤PASSが増える経路**: ASRが別の実在語へ誤転写し、その語の音素がLedger候補(低信頼含む)に一致する場合(例: TTSが実際には`MEE-lahs`と読んだのにASRが`Mellow`と書く)。実際にそう読まれたかは今回の12音声で独立確認されていない。
- **抑制**: (1)F1全差分点検(置換文に別の内容差分があれば非PASS) (2)Secondary同意(fallback/forced-secondaryは共通候補で両エンジン一致) (3)Ledger参照はCMU未収録語のみ・上限6・事前固定 (4)受理理由を純粋同音/Pattern A/B/Cに限定し常にPASS_WITH_WARNING+audit (5)`HOMOPHONE_EQUIVALENT`経由の固有名詞受理は根拠にしない(F2維持)。
- **誤NG(不要HR)の減少見込み**: 12件のうちBeforeで非PASS(=HR/regen対象)だった8件(行1,2,5,6,8,9,10,11)が全てPASSに(行11はSecondary同意を要する場面では不成立=11/12)。674ペアでは13件が新規PASS(Melos同型のHR/regenを回避)。
- 未確認の安全性を『確率が低いはず』でPASS扱いしない: 674ペア・合成のみで、**実音声での誤PASS率は未測定**。委任_02のruntime evidenceで実機確認する前提で、Status到達は`WIRING_DESIGN_DRAFT`止まり。

## 7. 設計論点とFable既定への賛否
| # | 論点 | Fable既定 | 本設計の評価 |
|---|---|---|---|
| 1 | C3(規則G2P)採否 | 不採用 | **賛成**。12/12に不要。C3はOOV語の発音を機械的に作るため後付けとの境界が曖昧になる |
| 2 | KP適用 | 適用(C1+C2) | 賛成(4節。先に実データ効果測定を推奨) |
| 3 | Ledger運用上限 | 読取のみ・CAP | 賛成+auditに`ledger_key`。自動生成/人手確定の区別フィールドは要判断 |
| 4 | forced-secondary | 適用(同一候補同意) | 賛成。Melos 12件で11/12 |
| 5 | 既存M1の実装上の制約(新発見) | — | 既存`m1_candidates`を再利用するため、置換先の綴りは『ASR語とCMU音素が同一かつPattern期待綴り(`melo`)であるCMU収録語』に限られる。語幹がCMU未収録の語、またはASR側がCMU未収録の綴りの場合は不成立(取りこぼし側であり誤PASSではない。EVAL合成T1c)。直接音素置換(ASR語の音素がformに一致→Pattern期待綴りへ置換)へ広げる選択肢はあるが**新規処理の追加**であり本委任では未実装。委任_02前にFable/Opusが要否を判断 |
| 6 | C1全異読をentity_likeへ広げるか | 代表のみ維持 | 感度分析で674ペア追加0件。拡張の実益なし→維持 |
| 7 | 既存Pattern A(綴り基準、OPEN-330)との関係 | — | `Brontes→Bronte`型はM1と無関係に既存Pattern Aが受理(EVAL合成の参考行)。本設計は触れない |
| 8 | design_judge EXACTショートカット | — | 674ペア集計で、offlineハーネスの`EXACT`(トークン等価で`$`/`%`等が落ちる)が4件をPASS扱いする。M1ではなくProductionも非PASSのため集計から除外(`harness_EXACT_artifact_not_m1`)。委任_02の実装は`classify_asr_match`直結で行いこの影響を受けない |

## 8. 誤PASS候補(人手確認用)
EVAL_01.mdの674ペア新規PASS13件を全件列挙。全て`Melos`↔`Mello/Mellow`型(Melos said/says/sighed、`The guards went still when Mello spoke`、`At the wedding, mellow smiled…`)。`mellow`は別の実在語(形容詞)でもあるため、「ASRが別実在語へ誤転写した」と「TTSがMello/Mellowと発音した」を転写だけでは区別できない。ここは本設計で**排除できない残余リスク**であり、ユーザー承認(複数の合理的候補の1つで可)に依拠する。実音声での確認はruntime evidence(委任_02)で行う。
