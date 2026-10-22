# INVESTIGATION_01: 固有名詞発音の新方針(PNAP)現状調査(委任_01、API 0・JPY0・Production無変更)

管理ID: PROPER-NOUN-PRONUNCIATION-ALARM-POLICY-PRODUCTION-01 委任_01 / 到達Status: `APPROVED_FOR_PRODUCTION_DESIGN_PENDING_OPUS`。ユーザー原文: `docs/pm/delegation_log/2026-10-22_PROPER-NOUN-PRONUNCIATION-ALARM-POLICY-PRODUCTION-01_USER.md`。
調査対象は全てread-only。数値は保存済みデータ(`er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl`ほか)の再判定(API 0)。

## 0. 結論(要点)
1. **X・Zは音声判定・HR投入・HR Lockの下流を共有している**(同一の`er006_secondary_asr_01.evaluate_attempt_with_cascade_detail`、同一のleaf関数群、同一の`er011_human_review_lock_01`)。アラーム受理の挿入点は**1か所**(adapterの統一judge直後)でX・Zの全英語ナレーションroleを覆える。
2. HRは「最終slotのNG」だけが投入条件(`er006_secondary_asr_01.py:1176`)。つまり**最終slotまで再試行TTSを回してからHR**する現行フローになっており、固有名詞不一致で最大3回のTTS+ASR+Azureを消費している。アラーム受理を最初のNG時点で行えば、この再試行費用も節約できる。
3. **TTSへの発音供給は2系統が既にある**: (a)静的綴り置換 `tts_safe_name_pronunciation_en`(`{"Reicher":"Riker"}`、`er003_v1_n3_01_tts_generate.py:990-999`)、(b)Ledgerの`pronunciation_hint`をstyle指示へ注入(`er006_pronunciation_tts_injection_01.py:56-77`)。X・Zの現行経路では(a)は**ナレーション本文(narrator/dialogue)だけ**に掛かり、comment/preview/topic_intro等には掛かっていない。(b)は`enable_pronunciation_resolver=True`の限られた経路(Z narrator[b1b]/charon_en、X b1b本文)のみ。
4. **Ledger側の欠落**: `upsert()`は`human_approved`・`tts_respelling`を保存しない(`er006_pronunciation_ledger_01.py:140-196`、任意キーは`evidence_tier/source_page_check_v1/evidence`のみ)。実Ledger38件はいずれも`human_approved`・`evidence_tier`未保存(2026-10-22 Ledger直読)。**現状のLedgerからA/B階層を判定して自動供給できるentryは0件**。Khaiteのhintは`KAYT`(非語)で機械的にはrespellingにならない。
5. 一般リスナーに公開されるページは`pages_dir`(`index.html`/`standard.html`/`advanced.html`+mp3)。既存の`PASS_WITH_WARNING`事後試聴リストは**このindex.htmlの補助節に出ている**(`er063_family_z_audio_01.py:1719-1730,1765-1769`、Xは`er019_family_x_audio_production_runner_01.py:2253-2255`)。アラームを同じ場所に出すと公開側に露出するため、**audit/配下の別ファイルに限定**する設計が必要。
6. 自動受理境界の校正(保存HR queueの実質88イベント、API 0): 保存イベントの51%(45/88)、distinct segment 45のうち22が全件受理・2が一部受理・21が不受理。不受理の内訳は語の脱落/見出し語(9)、Secondary転写なし(9)、Secondary側が隣接語まで別語(16)、Primary側に非固有名詞差・数値差(5)ほか。**M1配線後(2026-10-14以降)の実質12イベントのうち受理は1**(残りはMelos「Mellow Strength」型・数値/見出し等)。

## 1. 経路図(file:line付き)

### 1-1. 共有部(X・Z共通)
```
[TTS入力整形]  X: n3_tts.tts_safe_news_en(text)  er019:962(B1B本文) er019:1361(A2本文) / tts_safe_en系 er019:910,927,1314(topic_intro/comment等)
               Z: _norm_for_tts(spec)  er063:760-768 (narrator/dialogue=tts_safe_news_en, topic_intro/preview/comment=tts_safe_en, kp_en=tts_safe_kp_en)
               tts_safe_news_en = name_pronunciation(Reicher->Riker) ∘ number_words ∘ paragraphs ∘ tts_safe_en   er003_v1_n3_01_tts_generate.py:994-999
      │  この整形後textが「TTS入力」かつ「ASR比較のcanonical_text」(Reicher方式の根拠。置換後textで比較される)
      ▼
[leaf生成関数]  review_lock.guarded_generate("en")(er011:673-701) が check_before_generation(er011:299) / record_outcome(er011:357)で包む
      │  news_tail_fix.generate_news_narration_wide_margin(er003_v1_sing01_news_tail_fix.py:209) / voice01.generate_charon_english(er003_v1_sing01_voice01_generate.py:246)
      │  / crosslevel.generate_english_segment_with_fallback(er003_v1_crosslevel_audio_02_common.py:378) / repro01.generate_narration_snippet_verified_strict(er003_v1_repro01_main_generate.py:362)
      │  / n3_tts.generate_a2_segment_with_slowdown (6%減速後の再検証 _post_slowdown_unified_judge er003_v1_n3_01_tts_generate.py:122-170)
      ▼
[ASR]  Primary=OpenAI ASR(routing.transcribe) → evaluate_attempt_with_cascade(er006_secondary_asr_01.py:578) → evaluate_attempt_with_cascade_detail(:816)
      │  Primary P-chain: val.evaluate_attempt(Tier1[5role]+baseline+contraction+B1 CS) → CS Equivalence層(:~920, A2/B1本文) → Tier3(:959)
      │                   → 非ラテンKP層(:~1010) → CMU Case A/homophone(:1050-1060) → M1(:1062-1070)
      │  統一judge(er078_asr_unified_judge_01.unified_judge, 呼出 er006:1124): Primary PASS→最終ANDゲート / Primary NG→P1値・否定差(NG_PROTECTED)→P2除外表(NG_EXCLUDED)
      │                   →P3 Azure Secondary 1回(Phrase List付き; 障害=NG_SECONDARY_UNAVAILABLE[技術STOP]; 許容集合PASS=PASS_WITH_WARNING[SECONDARY_CONFIRMED]; 不許容=NG_BOTH)
      ▼
[判定の確定]  er006:1146 result["verified"]=bool(jr.verified)
      │   NG時: 最終slotかつ技術STOPでなければ human_review_required=True(:1176)、entity_like mismatchなら pronunciation_lookups(Stage 1: :1177-1197 → _resolve_unresolved_entity_for_review :439)
      │   evaluate_attempt_with_cascade(:628-636) が human_review_required なら _log_human_review(:476) → er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl
      ▼
[leaf: verified/NG]  verified=True → status "OK" + asr_judgement(監査record)を返す(news_tail :251-290)。NG → 次slot再試行(attempt上限は build_attempt_ctx(er078_asr_unified_attempt_ctx_01.py)のtotal_slots)
      │   最終NG → status STOPPED を返す
      ▼
[HR Lock] record_outcome: status=="OK" → RESOLVED / それ以外 → HUMAN_REVIEW_REQUIRED(er011:357-440)。次回起動の check_before_generation(:299) が HUMAN_REVIEW_REQUIRED を 0 API で停止(:341-343)。
          解除=approve_regenerate / record_human_approval(人のみ)
      ▼
[run層]  X: er019:990-1016(B1B) / :1388-1402(A2) が tts_generation_results.json を保存→ pww_registry.write_listening_list_safe(out_dir)(:1008 / :1397)
         Z: er063:1165-1175 が results 保存→ write_listening_list_safe(level_dir)(:1172-1175)
         status!=OK のclip: X=Audio Validation Gate/Assembly前の関所(er019:785-830, _assert_shared_narration_ok)、Z=FamilyZ…_TTS_CLIPS_NOT_OK(er026:1631)で停止
      ▼
[試聴ページ/完成物]  Z: pages_dir/index.html(+standard.html/advanced.html) の補助節に PASS_WITH_WARNING listing(er063:1719-1769)
                     X: 試聴ページ(er019:2253-2262 pww_sections_html)。 GitHub Pages `user_test/*` は実質公開(PM_GOVERNANCE参照)
```

### 1-2. 再利用・resume(アラーム状態を失わないために必須の経路)
| 経路 | 現行挙動 | file:line | アラーム状態への含意 |
|---|---|---|---|
| X同一out_dir前回run再利用 | `_generate_or_reuse`がstatus==OK+canonical一致で再利用。再利用音声は`asr_judgement`→`asr_judgement_inherited`へ移す | er019:614-675 | 再利用時もalarm recordが`asr_judgement_inherited`に残る→run層deriveで拾える(新規対応不要。ただし下の再判定ガードに注意) |
| 再利用前の値ガード | `_reuse_guard_blocks`→`er078_reuse_value_guard_01.guard_entry`が保存転写を現行統一judgeで再判定。値/否定差のみ再利用ブロック(それ以外のNGは再利用を止めない) | er019:622-628, er078_reuse_value_guard_01.py:32-71 | アラーム受理entryは再判定でNG_BOTH(`secondary_not_accepted`)になるがprotected理由でないため**ブロックされない**。ただし次行 |
| X継承再判定(validation inheritance) | `rejudge_with_current_judge`: 元`asr_judgement.state`が`PASS`/`PASS_WITH_WARNING`のときのみ元WARNINGを継承。それ以外は現行judgeの結果でokを決める | er019_family_x_validation_inheritance_01.py:231-236,296-335 | `PASS_WITH_PRONUNCIATION_ALARM`はこの許容集合に無い→再判定NG→継承失敗(再生成)の恐れ。**配線で許容集合へ追加が必要(IMPLEMENTATION_DESIGN §5-5)** |
| Master Audio Store再利用 | `asr_judgement`をmanifestに保存し、再利用時`asr_judgement_inherited`に復元 | er006_master_audio_store_01.py:190-193,225-226 | alarm recordがmanifestに残る(`asr_judgement`丸ごと保存のため新規対応不要)。共有narration(shell)に固有名詞は無いので実質影響小 |
| Z resume | checkpoint/results再読込(`RUN_STATE_FILES`)、同一clip再実行は`--only-clips` | er063:563-640,1063; er026:1624-1632 | 同上。results内の`asr_judgement`が残るため、run層deriveは冪等に再生成できる |
| HR Lock | status!=OKで`HUMAN_REVIEW_REQUIRED`。status==OKなら`RESOLVED` | er011:341-343,396-410 | アラーム受理はleafにとって**status OK**なので、HR Lock・HR queue・`approve_regenerate`を一切経由しない(承認操作不要の要件を満たす) |

### 1-3. 判定器の区分(受理条件の根拠)
- `val.classify_asr_match`の`ASR_VALIDATION_UNCERTAIN`: `er006_preprod_hardening_01_validation.py:1172-1195`。`entity_like`は**canonical側の内容語がすべて「原文で大文字始まりの語」(+loanword+Ledger[既定OFF=`LEDGER_ENTITY_FLAGS_ENABLED_FOR_CLASSIFICATION`])**であること(同:726-736, 1098-1110)。ASR側の語数・語種は問わない(Melos→"Mellow Strength"も`entity_like=True`になり得る)。
- 数値/否定差は`protected_check`で`TRUE_CONTENT_MISMATCH`(:1117-1130)。非固有名詞の内容語差は`TRUE_CONTENT_MISMATCH`(:1143-1183)。`tts_failure_threshold`未満は`TTS_FAILURE`(:1132)。
- `is_entity_like_mismatch`(`er006_secondary_asr_01.py:307-315`)は「UNCERTAIN∧全diffがentity_like」。**文頭の大文字語(Retail等)も`capitalized_flags`に入る**(`_STOPWORDS`の語のみ除外、val:468-492)→一般語を固有名詞扱いして許容してしまうリスクがあるため、受理側で追加検査を課す(DESIGN §2-3)。
- 語の追加のみのdiff(canonical側が空)は`entity_like=False`(`bool(canon_content)`、val:734)=従来どおり`TRUE_CONTENT_MISMATCH`。語の脱落(ASR側が空、canonical側が固有名詞)は`entity_like=True`になり得る→**受理側で「語の脱落=音声欠落との区別不能」として不受理**にする(CONFLICTS (e))。

### 1-4. 旧ルール・重複の洗い出し(Dangling Reference候補)
| 旧ルール/参照 | 所在 | 新方針での扱い案 |
|---|---|---|
| 固有名詞のみ不一致でのHR投入(最終slot→human_review_queue) | er006:1176-1197 | **対象範囲内の固有名詞のみ不一致は発動しない**(受理で`verified=True`に変わるため構造上到達しない)。範囲外(KP/見出し/一般語等)の経路は無変更で残る |
| Stage 1のHRパッケージ表示(`pronunciation_lookups`: 階層・出典・否定記録) | er006:1177-1197, er097 `hr_display` | 受理経路ではHR packageを作らず、**同じ調査結果を`pronunciation_basis`としてアラームrecordへ載せる**(用途変更・重複排除。調査自体=`_resolve_unresolved_entity_for_review`は維持) |
| `ASR_VALIDATION_UNCERTAIN`→`stop_retrying`(entity-onlyで同signature連続) | val:1394-1410 | 統一judge導入後`stop_retrying=False`固定(er006:1147)のため無影響。残置 |
| 固有名詞ASR救済系Open Items | OPEN-318/327/330/331/335 ほか | Status整理候補(閉じるのはFable/ユーザー)。DESIGN §7参照 |
| 静的辞書`{"Reicher":"Riker"}` | er003_v1_n3_01_tts_generate.py:990-999 | 残置(Family A共有・編集不可)。供給moduleは当該語を二重適用しない(`static_overrides`) |

## 2. Pronunciation Ledger / Stage 1 / Stage 2の現況(読取)
- Ledger: 38 entry(うちja_reading 7、cascade_unresolved_entity 21)。`human_approved`・`evidence_tier`未保存(キー無し)。hintはAI出力(例 meink='MAY-ngk'[Wikipediaは『MEENK』]、khaite='KAYT'、melos='MEE-lahs' low)。**AI出力のhintだけでは供給根拠にならない**(Stage 2 Trialの結論)。
- Stage 1(配線済み): 最終slotのHR用に`resolve_span_for_review`(er097:527)が調査・否定記録・引用実在確認(V1')を行い、`source_page_check_v1`/`evidence_tier`をLedgerに保存(`upsert`の任意キー、er006_pronunciation_ledger_01.py:192-196)。**ただしこの保存は今後の調査からで、既存38件は未調査のまま**。
- Stage 2: 判定側方式`REJECTED`、TTS入力側供給はKhaite型(綴りがTTSに追従する語)で`VALIDATED(条件付き)`。Meink/Altuzarraは置換でも制御不能。誤供給は置換後比較で通ってしまう(Meink→Mink)。(`STAGE2_TRIAL_CLOSEOUT_01.md`)

## 3. 実データによる校正結果(API 0、`calibrate_replay_01.py`/`calibrate_replay_01_result.json`)
保存HR queue 113行 = 混入(単体テストmock)25行 + 実質88イベント。受理判定(DESIGN §2)を各イベントのPrimary/Secondary保存転写へ適用した結果:

| 項目 | 件数 |
|---|---|
| 実質イベント | 88(distinct canonical 45) |
| 受理(アラーム対象) | 45イベント。distinct segment: 全件受理22 / 一部受理2 / 受理なし21 |
| 不受理の主因 | Secondary側が隣接語まで別語16(Melos「drank→mellow strength」型、ELLE→L+'minaudiere'複合等)、語の脱落/見出し語9(`## Main Story`、`One Voice:`等=固有名詞ではない)、Secondary転写なし9、Primary側に非固有名詞差・数値差5、低類似度1(Meink→"mc")、一般語1(mini→many) |
| 受理された固有名詞 | khaite 10, melos 8, toteme 5, bisnow 4, gruen 4, kristie tse 4, muse 4, mimoun 3, altuzarra 3, canele 2, その他 |
| M1配線後(2026-10-14以降)の実質12イベント | 受理1(Melos、2026-10-15 `Melos said.`型)、不受理11(Melos「hands held out for the chains」2、数値/見出し等) |
| Family Z Melos実イベント | 11件中8受理・3不受理(不受理3は同一clip「…held out for the chains」=Secondaryが隣接語を別語に聞き取る) |
| 混入25行(単体テストmock) | 全件「受理」判定になるが実害なし(Production queue行ではない。OPEN-447で隔離済み) |

→ 受理境界は「固有名詞の発音不一致のみ」を機械的に拾え、Melosの「Mellow Strength」型・見出し語・数値は拾わない。**ただし校正は保存データ88件のみ**(1日15作品時の実頻度は未検証)。境界パラメータ(`MAX_DIFFS_PER_SEGMENT=3`、`MIN_SPAN_SIMILARITY=0.40`、`MAX_ASR_TOKENS_PER_CANON_TOKEN=2`、一般語zipf基準4.0)は暫定値でOpusレビュー対象。

## 4. 一般リスナー非露出の現況
- GitHub Pages `user_test/*`はコミットしたファイルがそのまま公開される(`docs/pm/PM_GOVERNANCE.md`の運用記述、`user_test/articles_2026_0918.html`)。ZのページはSTORY_REGISTRYの`e2e_pages_dir`に出力(`er026:1020`)。
- 現行の`PASS_WITH_WARNING`節は同じpagesに載る(参考情報)。アラームは**ここに出さない**。`audit/`(run配下)はページ生成の入力ではあるが公開物ではない(ページ生成は`rows`/`kp_rows`/pww listだけを読む)。
- 将来の本番配信ではオペレーター専用エンドポイントが必要だが、本委任の範囲は「公開ページ生成コードが`pronunciation_alarms`を読まない」ことのテスト化まで(DESIGN §6)。
