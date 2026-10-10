# OPEN-258 設計・リスク評価 OPEN258_DESIGN_01

管理ID: FAMILY-X-TTS-ASR-ROOTCAUSE-01 FOLLOW-UP 委任_24 / 2026-10-11 / 到達点: **DESIGN_READY_FOR_REVIEW(Production未承認・未実装)**
制約遵守: 課金API呼び出し0(Azure/OpenAI/Gemini不使用)。ローカルfaster-whisper(無料)とローカル純粋関数(`classify_ja_asr_match`、Resolver LLM=OFFに固定)のみ使用。Production/Prompt/SSOT変更なし。
無料検証の生データ: `OPEN258_OFFLINE_EVIDENCE_01.json`(whisper転写・全47 segment群の再判定)。

## 0. 確定事実と結論
- 確定事実(ユーザー試聴): META A2 japanese_title、TTSは「出演」と正しく発音。Primary(gpt-4o-mini-transcribe)が3回とも「出現」と誤認識。
- 無料offline検証: 保存3 attemptをローカルfaster-whisper(tiny/small/medium、日本語、原稿非提示)で転写すると、attempt2・3は**3モデルとも「出演」**、「出現」と聞いたモデルは0。attempt1のみ3モデルとも「出面」(出演/出現のどちらでもない曖昧な音。試聴では出演)。独立ASRが「出演」と聞くことが無料で確認でき、Primary固有の誤認識という説明と整合(11節)。
- 結論: Primary NG直後に**Secondary ASR(Azure)を1回だけ独立確認として挟む案(以下SCG: Secondary Confirm Gate)**は、既存Cascadeの再利用で小規模に実装でき、既存ログ推定でも費用増は極小(履歴全体で約¥10)、再生成と時間を削減できる。最大リスクは「Secondaryが原稿寄りに丸めて誤PASS」で、PASS条件の厳格化・Phrase List不使用・証跡保存・試聴サンプル監査で管理する。

## 1. 既存資産の再利用と挿入点
| 再利用する既存資産 | 場所 |
|---|---|
| Azure Secondary呼び出し(連続認識、Phrase Listなし) | `er003_b1_p4_audio.get_full_text_via_azure_stt_continuous` L187、呼び出し例 `er007_ja_secondary_asr_01.py` Secondary#1ブロック |
| 判定 | `er007_ja_asr_validator_01.classify_ja_asr_match`(Secondary文字列にも同じ関数を適用。数字/否定保護 `protected.number_mismatches`/`negation_mismatches`、entity_like、読み比較をそのまま使える) |
| Human Review記録・queue重複防止 | `er007_ja_secondary_asr_01._log_human_review` |
| 複数エンジン一致の追跡パターン | 同ファイル `orthographic_ok_engines`(2エンジン判定)をSCGでも踏襲可 |
| 英語側と共通化可能な部分 | `er006_secondary_asr_01.evaluate_attempt_with_cascade_detail`(L459~)のAzure呼び出し・human review・独立ASR corroborationの形。特に英語は無料のローカルfaster-whisperを独立corroboration源として既に使用(`_connected_speech_equivalence_local_asr_text` L302、`er008_disfluency_qa_18.transcribe_verbatim`)。日本語でも同関数を`language="ja"`で流用可能(本検証で動作確認済み)。英語Tier3(er021)は日本語に存在せず共通化対象外 |
| 再利用**不可**(依頼文の`DEVIATION_FLAG_KEYS`) | `er003_v1_en_direct_vfl_01_generate.py` L452 / `er009_ledger_deviation_recalibration_02.py` L43 は**記事本文のFact Check逸脱フラグ**でありASR差分用ではない。ASR側の重大差分検出は`protected_check_ja`(数字・否定)+entity_like判定が既存機構 |

**挿入点(1か所)**: `er007_ja_secondary_asr_01.evaluate_attempt_ja_with_cascade_detail`(L104~)内 L128 の早期return
`if cls.should_pass or not cascade_enabled or not is_entity_like_mismatch_ja(cls): return result`
の直前に、`cls.classification == "TRUE_CONTENT_MISMATCH"`かつSCG適用条件を満たす場合だけAzure 1回を実行する新ブロックを追加。呼び出し元(`er003_v1_repro01_main_generate.py` L363)は`(verified, stop_retrying, cls)`のdrop-in戻り値のため無変更。Secondaryでも一致しなければ従来どおり`should_retry=True`のまま返す(=TTS再生成、挙動不変)。

## 2. 適用条件(Secondaryを呼ぶ条件)
| 案 | 条件 | 履歴ログ推定(10節) | 評価 |
|---|---|---|---|
| V0 現行 | Secondary不実行 | - | 今回のMETA STOPPEDが再発 |
| **V1 全TRUE_CONTENT_MISMATCH先行(構造除外のみ)** | 数字/否定不一致なし・全体類似度>=0.4(TTS異常でない)・長さOK・指示文echo(prompt leak)でない | 適用32群/Azure44回($0.075)/Secondary代理が原稿一致=14群/再生成16回回避 | 救済最大。誤PASS管理が肝 |
| **V2 限定(replaceのみ・各側2文字以下)** | V1+opcodeがreplaceのみ・差分各側2文字以下 | 適用16群/18回($0.028)/救済3群/再生成4回回避 | 安全寄りだが、実際の誤認識(死図塔=湿度、買いせまい=倍線前、目をしく=目を引く)は3文字以上や挿入が多く救済漏れ大。**META事例(1文字)は拾える** |
| V3 同一誤り2 attempt以上の後のみ(OPEN-258候補A) | 同じASR誤りが2 attempt再現後にSecondary | 最低1回は無駄な再生成(今回で言えば約172s) | 費用最小だが時間削減は半減 |

推奨: **V1を基本、Production化はPhase分け**(13節)。V2は最初に導入する安全側ステップの候補。理由=誤PASSの管理はトリガ条件よりPASS条件側(3節)が本質で、トリガを絞ると救済がほぼ失われる。ユーザー方針「危険だからHuman Reviewで終わらせない」にも合致。
SCG非適用(構造除外): (a) 数字・否定の不一致(`number_mismatches`/`negation_mismatches`が非空)、(b) 全体類似度<0.4(TTS生成異常。例: 英語指示文を読み上げるprompt leak)、(c) `length_ok`=False、(d) A2 Reading Resolver/variant layerで既にPASSする差(従来経路が先)、(e) entity_like/phonetic_uncertain(既存Cascadeへ進むので現行のまま)。
注意: 履歴ログの「TRUE_CONTENT_MISMATCH」はOPEN-145配線(2026-09-12)前のものを含み、現行コードで再判定すると76件が48件に減る(例: towels comment_2の6回STOPPEDは現行コードではPHONETIC_MATCHで救済済み)。推定は現行コード基準。

## 3. Primary NG・Secondary OK時のPASS条件
- **要求水準(案)**: Secondary文字列を`classify_ja_asr_match(canonical, secondary_text)`にかけ、`EXACT_MATCH`/`NORMALIZED_MATCH`(句読点・全角半角正規化の範囲)の場合のみPASS。`PHONETIC_MATCH`(同読み別表記)、`ASR_VALIDATION_UNCERTAIN`、`READING_RESOLVED_MATCH`はPASSにしない(SCGはPrimaryが不一致と言った音声を覆す特別経路のため一段厳格に)。
- **Primary≠Secondary**: Secondaryが原稿一致かつPrimaryは不一致、すなわち2エンジンが食い違うことがSCG-PASSの定義。Secondaryも同じ誤りを返せば新情報なし=PASSにしない。
- **信頼度閾値**: 現行`get_full_text_via_azure_stt_continuous`は文字列のみで信頼度は取得していない。Phase1は閾値なし(文字列厳格一致で代替)。Phase2候補: 詳細出力(NBest confidence)取得による閾値(別実装、未検証)。
- **禁止**: SCGのAzure呼び出しにPhrase List(原稿由来の語彙ヒント)を渡さない。渡すとSecondaryが原稿へ寄って誤PASSする(英語の`get_full_text_via_azure_stt_with_phrase_list`と日本語Secondaryの重要な違い。日本語Secondaryは現状Phrase Listなし=この性質を維持)。
- 新final_status案: `SECONDARY_CONFIRMED_PRIMARY_FALSE_NG`。consumer調査(grep): 分類名のホワイトリストはなく、`ORTHOGRAPHIC_VARIANT_CONFIRMED`と同様に`er007_ja_secondary_asr_01.py`内でのみ生成される。attempt JSONの`audio_classification`/`cascade_steps`へ記録して証跡化。

## 4. 重大差分(数字・否定・固有名詞・主体入替・日付)の除外規則案
| 種別 | 検出 | 扱い |
|---|---|---|
| 数字差 | `protected.number_mismatches`(既存) | SCG対象外=現行どおり再生成 |
| 否定差 | `protected.negation_mismatches`(既存)。例: 縛られ**ず**→縛られ**る**は、whisper独立転写でも「縛られる」と確認でき、実際のTTS誤りの典型 | SCG対象外。Secondary側でも数字・否定一致を必須(`classify`がEXACT/NORMALIZEDのため自動的に満たす) |
| 固有名詞・略語 | `entity_like`(既存、カタカナ率50%以上・英大文字略語) | 既存Cascadeのまま(SCGは触れない) |
| 主体入替・助詞差(が/は/を/に等、単独ひらがなreplace) | 既存機構なし。新規ルール案: diff片側が単独の格助詞1文字 | Phase1はSCG対象外(例: 証拠**だ**と→証拠**が**と)。Phase2でSecondary一致を条件に解禁を検討 |
| 日付・数量(漢数字・年月日) | 数字検出は算用数字中心、漢数字は`normalize_kanji_counter_numerals_ja`が一部のみ | Phase1は差分文字列に漢数字(一〜十百千万)・年月日を含めばSCG対象外(新規の小ルール案) |
再利用可否: 数字・否定・固有名詞は**既存機構を再利用可**、助詞・日付は**新規の小ルール**(正規表現レベル)が必要。

## 5. Secondaryも誤認識する場合(同一誤聴)のリスクと検知
2種類を区別する。
1. **Secondaryが原稿寄りに丸めて誤PASS**(最重要): TTSが実際に誤読したのに、SecondaryのLM prior/補正で原稿どおりに書き起こす。
2. **PrimaryとSecondaryが同一誤聴**(Museの3系統一致、`MUSE_ASR_RCA_01.md`): SecondaryもNGとなり現行と同じ再生成へ進む=悪化しない。ただしSCGでは救えない(音韻衝突型はOPEN-257の領域)。

誤PASS側の検知・緩和策:
- Phrase List不使用、PASS条件を文字列厳格一致に限定(3節)。
- **第3の独立ASR(無料ローカルfaster-whisper)による2-of-3判定(Option)**: 本検証でwhisperは、真のTTS誤りと思われる例を概ね誤りのまま転写し(縛られる、名称/両手、体内どこ、肉術 等)、正しい発音(META attempt2/3)は正しく転写した。第3エンジンとして一定の判別力がある。Azure OKかつwhisper OKのときだけPASSとすれば誤PASS率は更に下がる(ただしProduction環境への導入・速度[small CPUで1音声数秒]は未検証)。
- 読み仮名比較・音素距離は、えん/げんのような1音差では「近いから許容」方向に働くため**PASS条件には採用しない**。差分spanの読み距離は監視用ログのみ。
- 証跡: Secondary文字列・Primary文字列・判定をattempt JSONへ記録、attempt音声は既存どおり`narration/attempts/`に全保存(`er011_human_review_lock_01.save_tts_attempt_audio`)。SCG-PASS音声を試聴ページ(既存形式)で提示し、サンプル試聴で誤PASS率を実測(Phase0/導入後監査)。

**無料offline検証の限界**: whisperも原稿を見ずに転写するためAzureの代理としては妥当だが、Azureの実際の書き起こしはAzure実行(約¥0.3、要ユーザー承認)でのみ確認できる。

## 6. Secondary NG / unavailable
- Secondary NG(原稿不一致): 現行どおりTTS再生成(`should_retry=True`)。attempt上限・fallback voice・STOPPEDは不変。
- Secondary unavailable(API障害・タイムアウト・quota・`text is None`): 「証拠なし」とし、PASSにも新規STOPにもしない=現行どおり再生成。`secondary_confirm_status="UNAVAILABLE"`を記録。1 attempt 1回まで、attempt上限3は不変。Azure quota/無料枠は未確認。
- 1 attemptにつきSecondary最大1回(既存Cascadeの#1/#2やPrimary#2は使わない=費用・遅延抑制。同一音声の再認識は誤認識が再現しやすいことが今回の3回同一誤り・Museで既知)。

## 7. 推奨フロー図

```
TTS attempt生成 -> Primary ASR(gpt-4o-mini-transcribe) -> classify_ja_asr_match
  |-- PASS系 ------------------------------------------------> 採用
  |-- ASR_VALIDATION_UNCERTAIN(entity_like/phonetic) --------> 既存Cascade(Primary#2/Azure#1/#2) -> PASS / Human Review  [不変]
  |-- TRUE_CONTENT_MISMATCH
        |-- 構造除外(数字/否定差, 類似度<0.4, length NG, 助詞/日付差[Phase1]) -> TTS再生成(従来)
        |-- SCG対象 -> Secondary ASR(Azure, Phrase Listなし, 1回)
              |-- Secondary=原稿(EXACT/NORMALIZED) [任意: whisperも一致] -> PASS (SECONDARY_CONFIRMED_PRIMARY_FALSE_NG、証跡記録・監査対象)
              |-- Secondary NG / Primaryと同じ誤り ------------> TTS再生成(従来、attempt上限3・fallbackそのまま)
              |-- Secondary unavailable ------------------------> TTS再生成(従来)
  上限(標準2+fallback1=3)到達 -> STOPPED / Human Review(従来)
```

## 8. retry / fallback / regeneration との整合
- cascade順序: 既存Cascade(entity_like系)の後ろに足すのではなく、TRUE_CONTENT_MISMATCH専用の**別分岐**。ASR_VALIDATION_UNCERTAIN経路は無変更。
- attempt上限(`PRODUCTION_MAX_TTS_ATTEMPTS=3`、`er011_human_review_lock_01.py` L80)・fallback voice(minimal)・Human Review lock・budget guard: 無変更。SCGはattemptを消費せず、PASSすれば再生成が不要になるだけ。
- Local Rewrite(`er020_*`、並行agentがOPEN-256で対応中): 呼ばれるのはSTOPPED後の回復であり、SCG前段で救済できればそもそも到達しない。SCGは`er020_*`と`OPEN256_*`に触れない。
- Human Review移行条件: 影響なし(SCGでPASSすればHuman Review・STOPPEDは減る方向のみ)。
- 安全装置の回避なし: foreign token gate・length check・Resolver・variant layerは従来順で先に適用。

## 9. 既存Open Itemとの重複・競合
| OPEN | 関係 |
|---|---|
| OPEN-06(ASR homophone ambiguity、同音異義語の機械判別未実装) | 近い問題領域。SCGは同音語リストでなく独立エンジンの二重確認で補う別アプローチ。重複なし、補完 |
| OPEN-145(JA表記ゆれ、variant layer) | **競合なし**。variant layer/Resolverで救済できる差が先に判定され、SCGはその後のTRUE_CONTENT_MISMATCH残りのみ。現行コード再判定で76→48件に既に減少 |
| OPEN-122(英語Connected Speech等価層) | 英語専用。無関係。独立ASR corroborationの思想のみ共通 |
| OPEN-186(英語ASR数値/表記等価性) | 英語専用。無関係 |
| OPEN-256(Local Rewrite prefix check過剰reject、`er020_*`) | 別層(STOPPED後の回復)。SCGは前段で干渉しない |
| OPEN-257(音韻衝突型固有名詞のTTS-ASR失敗、Muse) | **SCGでは救済できない領域**(同一誤聴)。導入後もOPEN-257の包括対策は別途必要。相互参照のみ |
| OPEN-258(本件) | 候補Aをより一般化した設計案(Phase分割) |

## 10. 影響試算(既存ログから無料、現行コードで再判定)
方法: `er*_output/**/attempts/*.json`のうち`language=ja` = **630 attempt / 468 segment群**。TRUE_CONTENT_MISMATCHを含む群は47、attempt 76件。原稿の代理=「後で合格したattemptのASR文字列」(原稿そのものではない近似。合格が無い群は代理なし)。現行`classify_ja_asr_match`(Resolver LLMはOFF固定=課金0)で再判定し、Secondary代理=ローカルfaster-whisper small(Azureではない)。同一内容の複製run(free_address 02/03/04、coffee l3_01と_ttsonly、rerun_02/04)を含むため、独立件数はやや少ない。
| 項目 | 件数 |
|---|---|
| TRUE_CONTENT_MISMATCH(旧ログ記録) | 76 attempt / 47群 |
| 同(現行コードで再判定、代理あり) | 48 attempt / 34群(残りは現行コードで救済済み、または代理なし14) |
| 同群で発生した再生成(追加attempt)数 | 54回 |
| STOPPED(最終不合格)群 | 9群: META japanese_title 1(今回、SCG対象)、towels comment_2 1(現行コードではOPEN-145で救済済み)、英語指示文echo(TTSモデルA/B Trial)3、pause tag人工テスト 4 |
| V1適用 / Azure呼び出し | 32群 / 44回 |
| V1でSecondary代理が原稿一致した群(=誤再生成回避の候補) | **14群** |
| V1で回避できた再生成 | **16回**(同群の再生成54回中) |
| V1で回避できたSTOPPED | 履歴の代理データ内では0件(METAの1件はユーザー試聴+whisperで「回避可能だった」と判断=代理データ外) |
| V2 | 適用16群/18回、救済3群、再生成4回回避 |
| Human Review | `er007_output/ja_asr_cascade_01/human_review_queue.jsonl` 8件(全てASR_VALIDATION_UNCERTAIN)。TRUE_CONTENT_MISMATCHは直接Human Reviewへ行かない(STOPPED経由)。SCGで増えることはない |
| `er011_output/attempt_history.jsonl` 日本語1,340件 | OK 990、STOPPED 348(うち321は`pool_test_theme`の0回試行lock記録=ASR無関係、TTSを試行した実STOPPEDは27件)。再生成が発生した呼び出しは62件 |

### 費用・時間比較(登録単価のみ、Azure実請求は未確認)
- Azure STT: $1.0/hour(`pricing_snapshot.json`登録単価)。V1の44回(音声実長から計算)=**約$0.075(約¥11、履歴全体)**、1回約$0.0017(6秒音声)=約¥0.26。V2は$0.028。
- 回避された再生成: Gemini TTS 1回約$0.00045 + Primary ASR約$0.0002 = 約$0.00065 x16回 = **約$0.010(約¥1.6)**。
- 費用収支: V1は履歴全体で約$0.065(約¥10)の純増。課金額としては無視可能。
- 時間: 再生成1回はBATCHで約120〜170秒(META実測172/123/122s)。V1で16回回避=約**32〜45分**短縮。Azure 44回の処理時間は未測定(数秒/回と推定、実測が必要)。**効果の本質は費用より所要時間とSTOPPED削減**。
- 限界: 「代理=whisper small」「原稿代理=後続合格ASR」の近似。V1の44呼び出しのうち、代理が原稿一致しなかった30回は「SCGが正しくスルー(=再生成のまま)」側、一致した14群はSCGがPASSさせる側であり、**14群のうち本当にTTSが正しかったかは試聴でのみ確定**(Phase0)。

## 11. 無料のoffline検証結果(META japanese_title 3 attempt、原稿「AIの電話に人間が出演。問題は「キャスト変更」のお知らせでした」)
ローカルfaster-whisper(CPU int8、language=ja、temperature=0、原稿プロンプトなし)。beam=1/5で結果は同系。
| attempt(OpenAIの認識) | tiny | small | medium |
|---|---|---|---|
| 1(出現) | 出面 | 出面 | 出面 |
| 2(出現) | 出演 | 出演 | 出演 |
| 3 fallback(出現) | 出演 | 出演 | 出演 |
所見: 「出現」と聞いたモデルは0。attempt2・3は3モデルとも「出演」(Primaryだけが誤認識)。attempt1は3モデル共通で「出面」=音が曖昧でASRに難しい音声の可能性(ユーザー試聴では出演)。「出面」は原稿「出演」とも誤認識「出現」とも異なるため、Azureでも不一致になる可能性があり、その場合attempt1は従来どおり再生成へ進む(attempt2で救済される見込み。現行の3回消費・STOPPEDではなく、最大2 attemptでPASSできる可能性)。Azureでの確認は**ユーザー承認後に約¥0.3(1 attempt)〜約¥0.8(3 attempt)**で可能(提案のみ、未実行)。

## 12. リスク一覧と緩和策
| リスク | 内容 | 緩和策 | 残余 |
|---|---|---|---|
| 誤PASS(Secondaryが原稿寄りに丸める) | TTS誤読を見逃し本番に出る | Phrase List不使用・EXACT/NORMALIZEDのみ・数字/否定/助詞/日付除外・証跡保存・SCG-PASS音声の試聴サンプル監査・任意で無料whisper 2-of-3 | 0にはならない。Phase0試聴で実測し許容率をユーザーが判断 |
| 同一誤聴(Muse型) | Primary/Secondary一致誤認識 | SCGでは救えないが現行と同じ再生成へ(悪化しない) | OPEN-257で別途 |
| 遅延 | Azure1回追加(数秒と推定、未測定) | 1 attempt 1回上限、TRUE_CONTENT_MISMATCHのときだけ | 再生成(120〜170s)より大幅に短い |
| 費用 | Azure $1/h | 履歴全体で約¥11、1回約¥0.26 | 無視可能(実請求は未確認) |
| 複雑化 | 新分岐・新final_status | 変更は1関数内の1ブロック、drop-in戻り値、既存Cascade不変、FEATURE_FLAGで既定OFF可、テスト追加 | 低 |
| API障害 | Azure unavailable | 現行動作へフォールバック、PASSにしない | なし |
| Azure quota未確認 | 無料枠/上限 | 実行前にAzureポータルで確認(提案) | 要確認 |

## 13. 実装規模の見積(Production実装はしない)
- 変更ファイル(最小): `er007_ja_secondary_asr_01.py`(SCGブロック約40〜60行、FEATURE_FLAGで既定OFF可能)、`er007_ja_asr_validator_01.py`(助詞/日付の除外判定ヘルパー、任意)。
- test: `er007_ja_secondary_asr_01_test.py`にmock Azure(Primary=出現・Secondary=出演でPASS、Secondary=出現でretry、数字/否定差は呼ばれない、unavailableで従来動作、flag OFFで完全同一)。既存`er007_ja_asr_validator_01_test.py`は無変更で回帰確認。
- runtime evidence: Phase0=保存済みMETA音声でAzure Secondary実行(約¥0.8、ユーザー承認後)+回避候補14件のユーザー試聴(誤PASS率実測)。Phase1=実装後、Productionの`evaluate_attempt_ja_with_cascade`を保存wavで通すE2E(TTS再生成なし)。
- 規模感: 実装+test半日未満、検証と試聴確認で半日程度。Opus独立技術レビューGate: 条件A(新しい処理フロー設計)に該当するため、Production採用提案前にOpus独立レビューが必要な見込み(`docs/pm/PM_GOVERNANCE.md` 11-3、Fable判断)。

## 14. 残るユーザー判断事項(USER_DECISION_REQUIRED)
1. SCG方針の可否(V1全TCM対象 / V2限定 / V3同一誤り後)と、Phase分け(Phase0=Azure検証+試聴 → Phase1実装 → 本番ON)。
2. 誤PASSの許容水準(Phase0試聴で14件中何件までを許容するか)と、第3エンジン(無料whisper 2-of-3)の採否。
3. Azure検証の実行承認(約¥0.3〜0.8)。
4. 助詞差・日付差をPhase1で除外するか(推奨=除外)。
5. 新final_status名と、SCG-PASS音声の継続的な試聴監査運用の採否。
