# RISK-FLAGGER-PRODUCTION-WIRING-01 設計書 DESIGN_03(設計v3: W-1確定版 / Lane A)

- 管理ID: RISK-FLAGGER-PRODUCTION-WIRING-01 委任_04 = **Lane A**(2026-10-10)。**DESIGN_01(1〜13節+14節Opusレビュー)・DESIGN_02は変更しない**。本書はDESIGN_02の未決(S2-1〜S2-12)を、ユーザー確定事項(2026-10-10)で更新した追補・改訂版。
- Status: **DESIGN_READY / Phase 2着手前にOpus条件A再レビュー(S3-7、Fable手配)。USER_DECISION_REQUIRED=軽微2件(S3-1, S3-3)+Cap承認(S3-6、実行前)**。読み取り・設計+SSOT記録のみ。**Productionコード・Prompt・CURRENT_SPECは変更していない。課金API 0件。**
- 調査基準: git HEAD `4c303184`のワーキングツリー。行番号は同時点。「確認済み」=今回Grep/Read/実行で実在確認、「未確認」=確認できていない。sha256は今回`.venv`のPythonで実測(再現は15-2)。
- 並行Lane B(B3-ANNOTATION-AUTOMATION-TRIAL-01)は別agent。本書の「入力契約(3節)」がLane Bとのインターフェース。Lane Bは`docs/pm/ACTIVE_TASK.md`/`RESULT_PACKET.md`/DECISION_LOG/OPEN_ITEMS/git commitに触らない取り決め(本Laneが所有)。
- 使用モデル(PM_GOVERNANCE 25節): 本書はLLM呼出0件。Phase 2で使う予定のモデル=新Writer R0 `gpt-6-luna`(最新系)・R1/R2 `gpt-6-astra`(Trial W-1と同一、ユーザー正式採用)・RF `gpt-6-luna`と`gemini-3.5-flash-lite`(ユーザー指定)。旧/下位モデルの使用予定なし。

---

## 0. 結論サマリ(非エンジニア向け)

1. **新Writer W-1が一意に確定した**(DESIGN_02のS2-1/S2-3/S2-4が解消)。Trialで使ったPrompt・Fact Lock構造・Astra方式を「そのまま写す(byte-identical移植)」契約を、**sha256付き30項目**で列挙した(2節)。Prompt変更が要るのは**S3-1(Astra段の記号チェックを失敗した場合の再生成のしかた)の案Bだけ**で、これはユーザー判断(既定案は「Promptを変えず同じ指示で1回だけやり直す」)。
2. **注記済みB3の受け渡し契約(3節)を定義**した。Lane Bが「3ファイル(注記済みbrief・サイドカーJSON・manifest)」を出せば、Production runnerは**構造だけ検査**して受け取る。契約違反・注記なしなら**課金前に即STOP**。「注記なしB3で新Writerを動かす」逃げ道(スイッチ・自動フォールバック)は**コード上に作らない**。
3. **RF位置が確定**(4節): Advanced英訳完了 → Advanced RF → Standard向けLevel調整 → Standard RF → Review Queue保存 → (保険: TTS直前にsha照合) → TTS。StandardはAdvanced英文からのLevel調整であることをコードで確認済み(`er012_e` L615/L617)。
4. **非対称棚卸(5節)**: M1(a)=Advanced限定を**意図的差**に再分類。②(Level差で説明できない)は**新仕様判断が必要なものは0件**、運用注意1件(Standardが古いAdvancedから派生したまま残りうる)のみ。
5. **撤去28行・技術QA維持を確定**(6節)。jawのFact Check関連はC2で物理削除、W-1由来のTrial限定要素(M3・B1回復・Checker起点要素)は撤去対象。**M1(a)だけは「撤去」ではなく「無条件ON化」**(DESIGN_02のR-24から変更)。技術QAは18行+新規1行(注記契約検証=T-19)。
6. **本Wiringは「W-1全体PRODUCTION_WIRED」を名乗れない**(10節のGate依存図): Lane A実装完了 ∧ Lane B VALIDATED→ユーザー採用→配線 ∧ 最終L3 の3つが揃うまで。RF部分だけの配線完了は「RF配線完了(部分)、全体未WIRED」と記録する。
7. **今回できる実機確認(11節)**: 既存Trialの注記済みB3を契約経由で与える「**W-1下流 開発用確認run**」(約¥38〜¥127、Capはユーザー判断)。これを「W-1完全Production E2E」とは**呼ばない**(11-3に禁止表現を定義)。
8. **重要な運用論点(S3-3)**: C2(Writer差替え+旧Checker撤去)をmainへ入れると、Lane Bの配線が済むまで**Production runnerで新規記事を作れなくなる**(注記なしB3をWriterへ渡せないため)。推奨=C1(追加のみ)はmain、C2/C3は作業ブランチ+worktreeでLane B配線と同時にmainへ(12-2)。ユーザー判断。

---

## 1. ユーザー確定事項(2026-10-10)と設計への反映

| # | 確定事項 | 本書での反映 |
|---|---|---|
| 1 | 新Writer=W-1を`APPROVED_FOR_PRODUCTION`。W-2/3/4不採用(履歴・artifact保持)。W-1のPrompt/Fact Lock構造/Astra方式は改変禁止。Prompt変更要=STOP | 2節(移植契約)、13節S3-1 |
| 2 | 注記版B3のProduction自動化はLane B。W-1は注記自動化配線までPRODUCTION_WIREDにしない。注記済みB3を受けるinterfaceまで先行実装可 | 3節(契約)、10節(Gate)、12-2 |
| 3 | RF 4条件を両Level正式導入(OR・重複統合・検出元保持・非Blocking・自動修正なし) | 4節、7節 |
| 4/5 | Advanced RF=完成Advanced英文。Standard RF=Level調整完了後の完成Standard英文(主目的=簡略化によるFact意味の破壊検出) | 4節 |
| 6 | M1(a)はAdvanced限定のまま正式維持(意図的Level非対称) | 5節行3、6節R-23/24 |
| 7 | 非対称棚卸を再実施 | 5節 |
| 8 | 旧Fact Checker撤去(両Level、R0後/R2後JA/翻訳後Ledger・Deviation、MAJOR must-fix、ja_source差し戻し、Fact起点rewrite/recheck、Checker起点retry・regeneration)。OPEN-233系=Production未配線のままSUPERSEDED | 6節、SSOT記録(15節) |
| 9 | Review Queue=`review_queue/post_en/<article_id>/`にLevel明示、必須フィールド | 7節 |
| 10 | splitter共通Production module、Trial import禁止、regression 6語、文ID変更承認済み | 8節 |
| 11 | 費用機構3ギャップ修正承認、RF 4本のLevel別・model別実測費用保存、Gemini A4 0件でも自動削除しない | 8節 |
| 12 | 最終L3はB3注記自動化の正式採用・配線後。それ以前に「W-1完全Production E2E」と呼ばない。テーマ・CapはL3直前にユーザー判断 | 10節、11節 |
| 13 | Status語彙(W-1=APPROVED、RF 4条件=APPROVED、B3注記自動化=Trial) | 10節 |
| 14 | 軽微3件をFable判断で採用(audio側`compute_cost_jpy_so_far`のfail-closed化/Queue push責務をOpen Item/OPEN-233 SUPERSEDED整理) | 8-2、15節 |
| 15 | S2-5(Astra請求照合未実施)はOpen Itemに残し、Lane Aの実装を止めない | 13節、15節 |

---

## 2. W-1の一意化とbyte-identical移植契約

### 2-1. W-1の確定構成(Trial `er052_factlock_astra_e2e_runner_01.py` new腕から、Checker起点要素を除いたもの)

```
注記済みB3(3節の契約3ファイル)
  → R0: Luna `gpt-6-luna`  developer=DEVELOPER_MESSAGE, user=build_r0_prompt(storyline, annotated facts)  effort=high, 単発(previous_response_id無し)
        + 記号QA(既存Layer2: 検出時に既存violation noteで1回だけ再生成→なお残ればSTOP)
        → clean_ja_for_next(タグ除去、残存はTagLeak=STOP) → r0.md、R0復唱検出(記録のみ)
  → R1: Astra `gpt-6-astra` effort=high, user=USER_TMPL.format(body=r0.md)、developer無し、previous_response_id無し、service_tier指定なし
        → postprocess_ja → r1.p1.md
  → R2: Astra(同条件)、入力=R1の「生出力」r1.raw.md(後処理前。Trial逐語)
        → postprocess_ja → clean_ja_for_next → ja_writer/revision2.md
  → 以降は既存Production経路(Advanced忠実英訳 → 「In one line」(M1(a)) → Advanced RF → Standard Level調整 → Standard RF …)
```

Trial要素の取捨(コードで確認済み: `worker_new_r0` L643〜699、`worker_new_astra` L700〜736、`ARM_FLAGS` L58):

| Trial new腕の要素 | Production W-1での扱い | 根拠 |
|---|---|---|
| Fact Lock R0ブロック(構造a: 同一LLM呼出内の【事実N】タグ+AN3第1文の数字規則置換) | **移植(byte-identical)** | ユーザー決定1 |
| Astra R1/R2 user template(系列X逐語) | **移植** | 同上 |
| 後処理(strip_markdown→normalize_ellipsis→dash_to_comma、タグ除去、R0復唱検出) | **移植** | 同上 |
| M1(a)(Advanced「In one line」入力へJA R2+Ledger) | **移植(無条件ON化、Advanced限定)** | ユーザー決定6。Production既存Prompt(`adv_gen` L585)を使うだけでPrompt追加なし |
| R0直後のJA Fact Check+must-fix 1回+STOP(`jaw.run_ja_writer_o_r1_r2(full_ledger_text=ledger)`経由) | **撤去** | ユーザー決定8(R0後Hard STOP除去) |
| R1/R2直後の`run_deviation_check`(`r1_fc.json`/`r2_fc.json`、`shadow_stop`) | **撤去** | 同上(Trialでは判定に使わない測定) |
| M3(Checkerのreclassify保護、`OPEN233_RECLASSIFY_PROTECT_FLAGS`) | **撤去** | Checker起点 |
| B1回復(Checker起点のWriter再実行、`must_fix_file`/`b1_try`) | **撤去** | Checker起点 |
| M1(b)(Checker起点の要約のみ再生成) | **撤去** | Checker起点 |
| OPEN-233 Checker(`worker_check`) | **配線しない**(SUPERSEDED) | ユーザー決定8 |
| 新規具体主張検出器`worker_ii`/影の対照`worker_shadow`/G0照合 | **移植しない**(Trial測定専用) | Production機構ではない |
| Luna R1/R2連鎖(`StopAfterR0`でTrialも未使用) | 使わない | Trialも使っていない |

### 2-2. 移植契約表(sha256はUTF-8文字列/関数ソースのsha256、HEAD `4c303184`で実測)

**A. 新規にProductionへ置く定数・関数(Trial版とbyte-identical。Production moduleは`er052*`をimportしない。同一性はtest内でのみTrial moduleを読んで機械証明)** — 21項目

| ID | 項目 | Trial所在 | sha256 |
|---|---|---|---|
| P1 | `USER_TMPL`(Astra R1/R2 user) | E2E runner L29 | 313120e94232497290e7efac2df1210dc628a8a1b497bb04e7174b5a98442f7f |
| P2 | `FACTLOCK_R0_BLOCK_HEAD` | fl L53 | e72822deeabf4d395b02e5f03b7a6a177203b123d9a41613a0347cb53e9377fc |
| P3 | `FACTLOCK_R0_BLOCK_TAIL` | fl L82 | 4ff7844384e20534ae45e1e6a19a79970cfe88cfac6d05822723d605f8396d5f |
| P4 | `MUSTFIX_PRIORITY`(R0ブロック項目7) | fl L51 | 3f4c6f3a4a54a934b5824a4b2cb2ba6e5eef07b56d5879f3b7109a154c0155ed |
| P5 | `build_r0_block(AN3)`の出力=R0 Fact Lockブロック全体(AN3第1文を数字規則5で置換、第2文[固有名詞]は逐語保持) | fl L104 | 74b948719e14fd7184ff3719d36639ede7905e45cef95b97c1cca1a5638b2bf1 |
| X1 | `TAG_RE.pattern` | fl L117 | e741d7b52c3cb0e6d13d175cd07fa0ca9dc9214a897eadefd81a42e1ce582c70 |
| X2 | `BROAD_TAG_RE.pattern` | fl L119 | 3040b63717495c49b7155dc33ed23edfb4968b1bdd37276d649d9f06d92f653d |
| X3 | `MARK_RE.pattern` | fl L120 | b1a952f90bcd82bac0938bc02fc41e524a51216ff469ef3b69fb119598ec9cf4 |
| X4 | `TAG_LEAK_RE.pattern` | E2E L164 | 2521939572da8d300ced77b6035a424afe10624c55c2487bec0ecf06834a4ed8 |
| X5 | `ECHO_RE.pattern`(R0復唱) | E2E L165 | fcce9077a398c39b9c67b76bc150474d9d9421c16d2d06a7ce9df2b5b4efa0d5 |
| F1 | `strip_tags` | fl L130 | fbc1f553adc5a73f33b7c9986a5e98e1eaf0b6a4f6b7f0c79ff5f6888e6ecc62 |
| F2 | `parse_annotated_facts`(telemetry用) | fl L390 | 67515a1efef63c7a1999bf89e83d94fb193d2a6587c5ed67b5b73b1b7c64c8b4 |
| F3 | `build_r0_block`(関数) | fl L104 | 15cd9bc7753dbbd79713efb3aea1094a19f082d74303f6bbd55e00194a88a856 |
| F4 | `strip_markdown` | E2E L168 | 1809af1445c2fb1a96ac9985194831f0418cc57c1b3b29c4ba4de4352691bbaf |
| F5 | `dash_to_comma` | E2E L182 | 0dab13bf26c73673d9e20923dd7bc20e20b98d90c038357f4472c7687f7f229d |
| F6 | `postprocess_ja` | E2E L186 | c98fd66a945bef782c501112bea27204a0c1e367ca660d49705a99a988e40bd1 |
| F7 | `assert_no_tag_leak` | E2E L192 | 4590a0650be08f7e453174806dcbcfe6e43e62c6fff6c25d3a02c408b8419391 |
| F8 | `clean_ja_for_next` | E2E L198 | 9919d5fef338e7184e217ca4f2bfb45ed7e5a4ec30cfd4a46354e97f1df1d95b |
| F9 | `detect_r0_echo` | E2E L205 | b360e7517b949959508c6a156d68a7ba7e501509ff79b8c64b240a6d8e4a0b48 |
| F10 | `parse_brief_md` | E2E L212 | 2778bee0f53db2ee3d87af4f07ac256268ed8c2fd43e1de54f338e7f3b52fd34 |
| F11 | `call_astra`(transient retry 2回+Provenance fail-closed。**許容差は`cl.logging_context(TRIAL_ID,…)`のTRIAL_IDをProductionのTHEME_TAGへ置換する1点のみ**。同一性testは「logging_context引数行を除外した正規化後sha」で比較し、除外内容をtest内に明記) | E2E L617 | d8ef033a8f9c29d5cb973e85996d02962dd326f29ef23feadcd9a5f05270c460 |

注: F1の`strip_tags`はTrial `b3_annotation_check_01.py`にも複製があるが、Productionは上表F1(`fl` L130)のみを基準とする。

**B. 既に存在するProduction資産(無変更で参照。sha固定でdrift検知)** — 9項目

| ID | 項目 | 所在 | sha256 |
|---|---|---|---|
| E1 | `R0_PROMPT` | `er019_family_x_ja_writer_o_r1_r2_01.py` L52 | 6108a7cddaa9eaf31262354ba32d33e4683ccaf810d861f27e3dcc8972028366 |
| E2 | `DEVELOPER_MESSAGE` | 同 L69 | d1fbb04224d346e79c588b8e69da4dcfe26e758ceefc71aa83d13ff7f216ed8d |
| E3 | `SYMBOL_PREVENTION_BLOCK_JA` | 同 L83 | 0629ab47a18ccb986844d8cff4ea087a9690eb8a7b8aefb28039496eec603b73 |
| E4 | `CONCRETENESS_CONTROL_AN3_BLOCK`(置換前) | 同 L102 | 067030ff53ecb76a4d1477a3deace07b3e1fac438a33cb873edbe045cf6927fe |
| E5 | `build_original_prompt`(ソース。R0プロンプト組立順=テーマ行差替→`[ニュース]`→記号予防→AN3[Trialでは置換後ブロック]) | 同 L148 | eaf0592f1936cb360e8ec0ef4b547c269ca105e8f9692691a11d25ff310455dd |
| E6 | `normalize_ellipsis_pause_ja`(関数) | `er003_audio_tts_asr_safety.py` | 57dfde90933115dcbb4952e280c09843ba44d47162a51cda7eb49e04cfa40a94 |
| E7 | `FAMILY_X_IN_ONE_LINE_INSTRUCTION_TEMPLATE_M1`(M1(a)) | `er003_v1_n3_01_advanced_adaptation_generate.py` L585 | c0bfcc90a8d287a375f91784349d6b8bb478b0533bafd2dbe7776ba6f1b93722 |
| E8 | `FAMILY_X_IN_ONE_LINE_M1_REQUIREMENT_LINE` | 同 L581 | 18b80d6e6a170176a496b7adc3030b72e77cba86d02b6ad08aee260f90377eef |
| E9 | `build_family_x_in_one_line_prompt`(ソース) | 同 L598 | d5c976c3135df5872d591484c4783944c65f2cc72170fab30f9117c9bfe9272e |

(M1なしテンプレート`FAMILY_X_IN_ONE_LINE_INSTRUCTION_TEMPLATE`=4a81f2d5c65073b4975e20cfb7799c8be128bd6020979d6ce0767978cb6f28b7 は参考。Production W-1では使われなくなる。)

**合計 A21 + B9 = 30項目。**

**C. 合成Prompt一致の機械証明(test)**: 同一入力(注記済みbrief 11本分: Trial 10テーマ+small_bag)で、(1) Production `build_r0_prompt()`の出力 == Trialの`fl.apply_factlock_patches()`適用下の`jaw.build_original_prompt()`出力(文字列完全一致)、(2) Astra user文 == `USER_TMPL.format(body=…)`、(3) `build_family_x_in_one_line_prompt(title, body, ja_text=…, ledger_text=…)`はE9のまま、をtest内でのみTrial moduleをimportして比較。

**D. 移植で改変が避けられない箇所の洗い出し**(STOP候補の検査結果): 上表A/Bの範囲では**改変不要**。差が出る点は(1)F11のlogging tag(許容差、上記)、(2)R0の`original_must_fix`(B1回復用)引数の削除=B1撤去に伴いその分岐のPromptが消えるだけで、通常R0 Promptは不変、(3)Production `build_r0_prompt()`はjawのグローバルAN3差替え(monkeypatch)ではなく、**P5を直接差し込む純関数**として実装(結果は(C)(1)で同一性を証明)、(4)Trialの`r0_meta.json`のうち`tagged_sentences`(JA文分割に依存)はTrial moduleの`split_sentences`が必要なため移植せず、`tags_used`・`marks_echoed`・`facts_in_brief`等の記録のみ移す(telemetryの縮小であり生成挙動は不変)。**Prompt文言の変更は0件**。

**E. Production W-1とTrial W-1の実行上の差分(一覧、Fable確認用)**: (a)R0後FC+must-fix 1回とそのSTOPが消える(ユーザー決定8)、(b)R1/R2直後FCが消える(測定のみだった)、(c)B1回復が消える、(d)R0のsymbol QA(Luna、既存Layer2)は維持、(e)**Astra段(R1/R2)のsymbol QAはTrialでは記録のみ(findingsを書くだけ)。Productionの既存方針(T-02: 検出時1回再生成→STOP)をAstra段にどう適用するかが未決=S3-1**。Trial 16 Astra応答(`er052_output/factlock_astra_e2e_trial_01/runs/*/new/new_writer/r[12].response.json`)の`symbol_gate_findings`は**全て0件**(今回実測)で、発動頻度は低い見込み(ただし16件のみ)。(f)Luna R0のmodel_id requested/returnedを記録(Trialも`r0_meta.json`に記録)。不一致時は既存`fallback_detected`記録+Gate 3 E2(mismatch 0)で検査し、新規STOP条件は追加しない。

### 2-3. モデルrouting(`er006_model_routing_contract_01.py`へ追加のみ。環境変数上書きなし)

| routingキー | 値 | reasoning | 呼出箇所 | fail-closed |
|---|---|---|---|---|
| `FAMILY_X_FACTLOCK_R0` | `gpt-6-luna`(=`WRITER_MODEL`、現行値を実測確認) | `effort="high"`(`jaw.WRITER_EFFORT`、Trialと同一) | R0単発(developer+user) | `require_model("FAMILY_X_FACTLOCK_R0", …)`をAPI call前に呼ぶ。不一致/None=`ModelContractViolation` |
| `FAMILY_X_FACTLOCK_REVISE` | `gpt-6-astra` | `{"effort":"high"}`(Trialの`call_astra`と同一値) | R1/R2(userのみ、previous_response_id無し、service_tier指定なし) | 同上+返却`resp.model`が`gpt-6-astra`で始まらない場合は`ProvenanceViolation`で**STOP**(Provenance)。**Astra model不一致はSTOP**(ユーザー指示) |

- Trialは`routing.require_model_or_override("B1_WRITER", ASTRA_MODEL, override_reason=…)`で迂回していた。Productionは専用キーを`PROCESS_MODEL_MAP`へ追加し`require_model`(override無し)を使う=Trial的な迂回経路はProductionに存在しない。
- 単価: Astraは`pricing_snapshot.json` L339-357に登録済み(Standard tier)。noteの「Trial/DEV用、採用ではない」を、Production採用に伴い「W-1 Production採用(2026-10-10ユーザー決定)、請求ダッシュボード照合は未実施(OPEN-246)」へ更新する(C3、料金値は不変)。

### 2-4. 出力ファイル契約(下流が読むもの。`ja_writer/`)

`derive_japanese_title`(`er019 audio runner` L133)は`ja_writer/runtime_evidence.json["title"]`、無ければ`revision2.md`/`revision1.md`/`original.md`の1行目を読む。W-1 moduleは次を出力する(従来と同形): `ja_writer/original.md`(=R0のタグ除去後)・`revision1.md`(=R1後処理後)・`revision2.md`(=R2最終)・`runtime_evidence.json`(`original`/`r1`/`r2`のstage meta[requested/returned model、response_id、prompt sha]、`chain_method="factlock_r0_luna__astra_r1_r2_independent"`、`verbatim_shas`=本書2-2のsha群、`title`)。Trial相当の生ファイルは`ja_writer/factlock/`(`r0_with_tags.md`、`r1.raw.md`、`r2.raw.md`、`r1.response.json`、`r2.response.json`、`r0_meta.json`)へ。これで`er019 entertainment runner`の再利用分岐(`ja_writer/revision2.md`存在時)と`audio runner`は無変更で動く(再利用分岐自体は技術的に残す)。

---

## 3. 注記済みB3 入力契約(Lane Bとのinterface)

### 3-1. 方針

- Production runnerの「Writer段」は**注記済みB3 artifactだけを受け取る**。注記なしの`storyline_b3/selected_brief.md`をWriterへ渡す経路は**コード上に存在させない**(runtime switch・CLI引数・環境変数・自動フォールバックなし)。artifactが無い/契約違反=`AnnotatedB3ContractViolation`で即STOP(課金前)。
- 検証は**構造検証=技術QA**であり、Fact内容の正誤判定ではない(ユーザー指定)。検証関数はProduction側(`er053_annotated_b3_contract_01.py`、仮名)に置く。**Lane Bの検査器(`b3_annotation_check_01.py`等)をimportしない**(Trial module import禁止)。
- 検証関数が見るもの=ファイルの存在・形式・番号の連続・ID整合・sha整合・manifestの検査結果欄。見ないもの=注記がFactとして正しいか、数値の中核/周辺分類の妥当性(それはLane Bの責務)。

### 3-2. Artifact(出力先: `<out_dir>/storyline_b3/`)

| ファイル | 必須 | 内容 |
|---|---|---|
| `selected_brief.md` | 既存 | 注記前のB3出力(`run_storyline_b3`が従来どおり出す)。無変更 |
| `selected_brief_annotated.md` | **必須** | 注記済みbrief。`# Selected Fact Brief` / `## Storyline` / `## Selected Facts`の3見出し、Facts各行が`- 【事実N】本文`(Trial実物 `er052_output/factlock_astra_e2e_trial_01/annotation/final/<slug>/selected_brief_factlock.md`と同形を今回確認) |
| `annotation.json` | **必須** | サイドカー。Trial実物(`annotation/final/<slug>/annotation.json`)と同schema: `slug`/`annotator`(`A`\|`B`\|`MERGED`)/`spec_sha256`/`brief_sha256`/`facts[{n, ledger_ids[]}]`/`numbers[{surface, kind, class, concept?, role?}]`/`unmapped_claims[]`/`annotation_notes[]` |
| `annotation_manifest.json` | **必須** | Lane Bが出力する整合manifest(下記) |

`annotation_manifest.json`の必須キー: `schema_version`(=`"b3_annotation_manifest_v1"`)/`producer`(自由文字列。例`"b3_annotation_automation_v1"`/`"trial_fixture"`。**Production検証はこの値で分岐しない**=記録のみ)/`source_selected_brief_sha256`(`selected_brief.md`のsha256)/`ledger_sha256`(`research_ledger/verified_fact_ledger.txt`のsha256)/`annotated_md_sha256`/`sidecar_sha256`/`spec_sha256`/`generated_at`/`checks`(`{a_alignment, b_numbers, c_core_peripheral, d_tags, e_sidecar}`の各`"PASS"`または`"PASS_LAYOUT_NORMALIZED"`=Lane B検査器の自己申告)/`model_ids`(注記にLLMを使う場合の使用model、記録のみ)。

### 3-3. Production側の構造検証(`validate_annotated_b3(out_dir) -> AnnotatedB3`、いずれか不一致=STOP)

| # | 検査 | 種別 |
|---|---|---|
| V1 | 4ファイルの存在・UTF-8読込・JSON構文 | 構造 |
| V2 | manifest `schema_version`一致、必須キー全て存在 | 構造 |
| V3 | `selected_brief.md`のsha256 == `source_selected_brief_sha256`、台帳sha256 == `ledger_sha256`、annotated md/sidecarのsha256 == manifestの値(stale・改竄・取り違え検知) | 整合 |
| V4 | `parse_brief_md`(F10)が成功(`## Storyline`/`## Selected Facts`形式、空でない) | 構造 |
| V5 | Selected Facts各行が`FACT_LINE_RE`形式に一致、番号Nが1..Kで連続・重複なし(K>=1)、タグ形式は`【事実N】`のみ(`BROAD_TAG_RE`に掛かる変形タグが無い) | 構造 |
| V6 | 数値印は`【中核数値】`/`【周辺数値】`(X3)のみ。印の総数 == サイドカー`numbers`件数 | 構造 |
| V7 | サイドカー`facts[].n`の集合 == V5のNの集合。`facts[].ledger_ids`の全IDが台帳に実在(台帳ID整合=技術QA T-17/T-18と同種) | ID整合 |
| V8 | `manifest.checks`の5項目が全て`PASS`/`PASS_LAYOUT_NORMALIZED`(hash束縛された自己申告。FAILまたは欠落=STOP) | 受領条件 |
| V9 | `sidecar.spec_sha256 == manifest.spec_sha256`、`sidecar.brief_sha256 == manifest.source_selected_brief_sha256` | 整合 |

STOP時: 例外メッセージ`[STOP] ANNOTATED_B3_CONTRACT_VIOLATION: Vn ...`、`storyline_b3/audit/contract_violation.json`に不一致内訳を保存、**API呼出前**(課金0)。

### 3-4. Lane Bへの要求(まとめ)

- 出力先・ファイル名・schema=3-2。注記ロジックの内側(LLM使用の有無、2者注記+決定論統合など)は自由。ただし**manifestとV1〜V9を満たすこと**。
- 再利用分岐(`--regenerate-stage storyline_b3`)では注記も再生成される前提(Lane B moduleを`run_storyline_b3`直後に呼ぶ1箇所をProduction runnerへ追加。これは(G-B)の配線作業)。`storyline_b3`再生成後に古い注記artifactが残らないよう、V3のsha照合で検知する。
- Lane BのVALIDATED判定・ユーザー採用・配線は本LaneのGate(10節)の入力であり、本書ではその内容を決めない。

### 3-5. 実装の置き場所

- `er053_annotated_b3_contract_01.py`(新規、約+200行): `AnnotatedB3`データクラス、`validate_annotated_b3()`、例外クラス。
- `er019 entertainment runner`: Writer段の入口で`validate_annotated_b3(out_dir)`を呼ぶ(C2)。C1ではまだ呼ばない(追加のみ)。
- 「開発用確認run」用に、**Trialの注記済み成果物から契約3ファイルを組み立てる¥0のDEV専用adapter**(`er053_dev_annotated_b3_fixture_adapter_01.py`、Production moduleからimportしない、Production runnerから参照しない)を別に置く。adapterが作るmanifestの`producer`は`"trial_fixture"`。

---

## 4. パイプライン順序・RF挿入位置(現行`er012_e`のStandard生成経路に照らして具体化)

### 4-1. コードで確認した事実

- Advanced: `adv_gen.generate_family_x_faithful_translation(ja_text, client=client)`(`er012_e` L488)→「In one line」(`_open243_iol`、L497/L500)→段落3分割検査→(旧)deviation check。
- **Standard=Advanced英文からのLevel調整**: `advanced_text = load_text(f"{b1b_dir}/article.md")`(L615、`only="standard"`時)→`std_gen.generate_family_x_standard_a2_no_heading(advanced_text, client=client)`(**L617**)。JAは直接入らない。
- よって「Advanced RF→Standard Level調整→Standard RF」は既存の依存関係(Standard入力=Advanced完成英文)と矛盾しない。RFは記事を書き換えないので、Advanced RFの結果はStandard生成に影響しない。

### 4-2. 確定順序(Production正式初回path、`--stage all`)

```
research → ledger → B3 → [Lane B: B3注記] → validate_annotated_b3
  → W-1: R0(Luna) → R1(Astra) → R2(Astra)  [ja_writer/revision2.md]
  → Advanced英訳(+「In one line」M1(a)) → 段落3分割検査(技術QA)    [b1b/article.md]
  → ★Advanced RF(完成Advanced英文 × 完全台帳、4条件逐次) → Review Queue保存(level=b1b)
  → Standard Level調整(入力=b1b/article.md) → 段落3分割検査(技術QA)  [a2/article.md]
  → ★Standard RF(完成Standard英文 × 完全台帳、4条件逐次) → Review Queue保存(level=a2)
  → Mandatory STOP(従来どおり、ユーザー確認前に後工程へ進まない)
  … 後工程(audio runner): scaffold → tts(★保険: article sha照合) → assemble → player
```

- 主挿入点: `er019 entertainment runner main`の`efam.run_writer_stage(…only="advanced")`の**直後**(Mandatory STOP/`--stop-after advanced`の前)で`risk_flag(level="b1b")`、`only="standard"`の**直後**(Mandatory STOPの前)で`risk_flag(level="a2")`。
- 保険: `er019 audio runner`の`tts`分岐(L1908)内、`assert_production_tts_backend`(L1911)の直後・`generate_family_x_*_segments`の前に`ensure_rf_record(source_dir, level)`(記事sha256 == Queue index上の(article_id,level,sha)を照合。無ければその場でRF実行。RF_UNAVAILABLEでもTTSへ進む)。
- RFの非Blocking原則: RF結果から分岐するSTOP/Rewrite/削除/再生成/自動retry=0(API技術retryのみ維持)。Queue保存失敗・RF_UNAVAILABLEでも次工程へ進む(可視化4点はDESIGN_02 5-4を継承)。
- 逐次実行の理由(並列化しない): `er005_cost_logger._CONTEXT`がglobalで並列だとstage tagが競合する(Opus論点7)+ユーザー指定の順序。並列化可能な独立作業は12-2で扱う。

### 4-3. Standard RFの位置づけ

- 検査対象=**Level調整後の完成Standard英文**。主目的=「Advanced→Standardの簡略化でFactの意味が壊れていないか」の検出。RF 4条件のPrompt・モデルは両Level同一(ユーザー決定3)。
- Trial検証母集団はAdvancedのみ(11本)=Standardは**検証母集団外**。`MODEL_STATS`を`article_level`別に出して経過観察(DESIGN_02 6節)。Standardに関する検出精度は未測定として明記する。

---

## 5. Standard/Advanced非対称棚卸 v3(16行、DESIGN_02 3節を更新)

分類: **①意図的Level差**(英語Level/StandardがAdvancedからLevel調整/M1(a) Advanced限定/Level固有Key Phrase/JA segment) ・ **②非意図的差**(②-a既存承認仕様で説明可、②-b実装漏れ、②-c新仕様判断=STOP)。

| # | 項目 | Advanced(b1b) / Standard(a2)の現状→配線後 | 分類 | 変更点(DESIGN_02比) |
|---|---|---|---|---|
| 1 | Writer入力・経路 | Adv: JA R2全文→忠実英訳。Std: **Adv英文全文**→A2(コード確認 L615/L617)。W-1はJA R2の中身のみ変える | ① | 同じ |
| 2 | 翻訳経路 | Adv=`NATURAL_ENGLISH_ADAPTATION`、Std=`STANDARD_A2_ADAPTATION`(`WRITER_MODEL`、技術retry2・構造gate) | ① | 同じ |
| 3 | Fact Lock継承 / **M1(a)** | Fact Lock=JA段で適用→両ENが派生(①)。**M1(a)=Advancedの「In one line」生成にJA R2+Ledgerを入れる。Standardは未実装だが、StandardはAdvanced英文(M1(a)入りの「In one line」を含む)からLevel調整するので差は伝播して吸収される** | **① 意図的差(再分類)** | DESIGN_02の②-c(STOP S2-4)を、ユーザー決定6で①へ。SSOTに「意図的Level非対称」と明記 |
| 4 | RF | 現状なし→**両Levelに適用**。Adv=完成Adv英文、Std=Level調整後の完成Std英文 | ① | 位置を4節で確定 |
| 5 | 旧Fact Checker | 両方にdeviation check(M1(b)はAdvのみだった)→**両方撤去** | ①(撤去で対称化) | DESIGN_02の②-aは撤去で消滅 |
| 6 | retry | 両方: 段落3分割retry(1回)+技術retry2。Adv段落retryは「In one line」も再生成、Stdは本文のみ→同じ(Checker由来must-fix retryは撤去) | ① | Adv段落retry時の「In one line」もM1(a)ありで再生成する点を明記 |
| 7 | fallback | 両方`fallback_detected`記録。Luna chain fallback(`previous_response_id`)はW-1で不要(R0は単発、Astraは独立呼出)。Astra: model不一致=STOP | ① | 同じ |
| 8 | regeneration | `--regenerate-stage advanced/standard`が各々存在。**`advanced`単独再生成後、Standardは自動追従しない(古いAdvanced派生のまま残りうる)** | **②-a(既存仕様D4で説明可)+運用注意** | RFのtts前sha照合はStandard自体のshaしか見ず、StandardがAdvancedの最新版由来かは検知されない。観測記録の提案=S3-2(新仕様判断ではない軽微、Fable判断) |
| 9 | Review Queue | 新規。1 path=1(記事,Level) | ① | 7節 |
| 10 | TTS前Gate | 両方: paragraph_count<3 STOP、shared narration Gate、Audio Validation Gate。A2のみ`japanese_title`取得WARN | ① | +RF保険 |
| 11 | TTS routing | B1/A2でvoice・JA title segment等が異なる。`assert_production_tts_backend`は共通 | ① | 無変更 |
| 12 | Key Phrase | Adv: 英語解説+phrase_repeat+text-gate。Std: 日本語意味(`generate_a2_japanese_with_reading_safety`) | ① | 無変更 |
| 13 | audio QA | 両方disfluency/repetition/記号normalizer。ASRはAdv=EN、StdのJA segment=JA ASR | ① | 無変更 |
| 14 | technical validators | 両方: 構造Gate、Audio Validation Gate。Stdのみ`run_checks`(数字追加/欠落をAdvとの差分で観測記録。非blocking) | ① | 無変更 |
| 15 | model routing | WRITER/SUPPORT/FACT_CHECK=gpt-6-luna。+FACTLOCK_R0/REVISE+RF 2キー | ① | W-1 2キー確定 |
| 16 | runtime exception handling | 両方`RuntimeError("[STOP] …")`。**AdvのみSTOP時に`audit/rejected_advanced_*.md`を保存**(deviation由来STOP) | ②-b | 旧Checker撤去でdeviation由来STOP自体が消えるため**自動的に消滅**(追加修正不要) |

**集計**: ①=14行、②=2行(②-a=行8[運用注意あり]、②-b=行16[撤去で消滅])、**②-c(新仕様判断が必要)=0件**。意図的差=英語Level/StandardがAdvancedからLevel調整/M1(a) Advanced限定/Level固有Key Phrase(行1,3,12ほか)。ユーザー指定の差分カテゴリ(Writer安全機構/RF有無/Checker残存/retry・fallback/Review Queue/technical QA/routing)で**非意図的差に残るものは行8のみ**。DESIGN_02の2-1・N-5で指摘した「Trial E2E新腕はAstra段の記号検査を記録のみで迂回していた」点は、Level差ではなく**Trial対Production差**で、S3-1として分離した。

---

## 6. 撤去リスト確定・技術QA維持・dangling reference

### 6-1. 旧Fact Checker撤去(28行確定。DESIGN_01のR-01〜R-22+DESIGN_02のR-23〜R-28。変更はR-23/R-24/R-26のみ)

R-01〜R-22(DESIGN_01 2節、再掲せずそのまま有効)=jaw/entertainment runner/`er012_e`のFact Check呼出9箇所・must-fix・recheck・ja_source差し戻し・案B・evidence出力・`er019_writer_run_summary_reconstruction`。R-25(G3 telemetry env)・R-27(`OPEN243_M2`)・R-28(Trial flags)はDESIGN_02のまま。

| ID | DESIGN_02 | **DESIGN_03(確定)** |
|---|---|---|
| R-23 | `open243_m1_enabled`ラッパ削除 | **同じ(削除)**。Production側は環境変数を一切読まない |
| R-24 | `_open243_iol`を常にM1なしへ | **変更**: `_open243_iol`の環境変数条件を除去し、**常にM1(a)入力(`ja_text`+`ledger_text`)で`adv_gen.generate_family_x_in_one_line`を呼ぶ**関数へ(名前も`_advanced_in_one_line`へ改名しdangling grepから`open243`を消す)。Advanced限定(Standardは呼ばない)。初回・段落retry再生成の両方で同じ関数 |
| R-26 | `adv_gen`のM1 Promptは「Trial用として残置」 | **変更**: M1 Prompt(E7〜E9)は**Production使用中のPrompt**になる(無変更)。`OPEN243_M1_ENV`/`open243_m1_enabled`(env読取関数)は呼出元が消えて不到達。Trial runnerが使うため関数自体は残置し、静的testで「Production到達性0」を保証 |

**M1(b)(Checker起点の要約のみ再生成、R-10/R-13)は引き続き撤去。M3・B1も撤去**(2-1表)。OPEN-233 Checker一式(Trial runner、Production未接続)は撤去対象に含めず、`SUPERSEDED`整理(15節)。

### 6-2. jawに関する構造決定(Fable確認事項、S3-4)

DESIGN_02 N-1どおり、W-1はjaw本体(`run_ja_writer_o_r1_r2`)を使わない。C2で**jawからFact Check関連(R-01〜R-05、`JAFactCheckStopError`の記号QA専用例外への分離[B-1])を物理削除**する。ただし(a)`REVISION_INSTRUCTIONS`・`R0_PROMPT`等の定数、(b)Luna R1/R2連鎖(T-03)、(c)記号QA(T-01/02)のコード自体は、Trial互換のため残す。結果として`er052_*` Trial runnerは**HEAD上ではjawの削除シンボルを参照して動かなくなる**(再現はgit tag+worktree、DESIGN_02 8節の前提と同じ)。

### 6-3. 技術QA維持(18行+新規1行)

T-01〜T-16(DESIGN_01 3節)+T-17+T-18(DESIGN_02 4節)=18行を維持。W-1に伴う**所在の移管**は次のとおり(維持対象は減らさない):

| ID | 変更 |
|---|---|
| T-01 | R0直後の記号QA(Layer2)は**W-1 moduleに再実装**(同じ`safety.detect_prohibited_symbols`/`build_symbol_violation_prompt_note`、1回再生成→STOP、`JASymbolCheckStopError`)。Promptは既存のviolation noteのみで新規文言なし |
| T-02 | R2直後の記号QA。W-1ではR2はAstra出力。**再生成方式は未決=S3-1** |
| T-03 | `previous_response_id`連鎖のfallbackはW-1で不要。**API技術retry維持の原則は`call_astra`(transient 2回)へ移管** |
| T-04〜T-18 | 無変更(T-17=B3 Fact ID整合STOP、T-18=research_ledger検証) |
| **T-19(新規)** | 3節の注記契約検証V1〜V9(構造・ID整合・sha整合)。ユーザー指定の「B3・Ledger自体の構造・ID consistency」に対応 |

### 6-4. Dangling reference grep list(確定。Production scope=`er012_e`/`er019 entertainment runner`/`er019 ja_writer`/`er019 audio runner`/W-1 module/RF module/contract module)

`OPEN243_M1`・`OPEN243_M2`・`OPEN243_G3_TELEMETRY_PATH`・`OPEN233_RECLASSIFY_PROTECT_FLAGS`・`open243_m1_enabled`・`_open243_iol`・`open243_g3_record_translation_minor`・`open243_m1_summary_only_retry`・`open243_majors_only_in_summary`・`JARecheckRequiredError`・`JAFactCheckStopError`(Fact用)・`_must_fix_from_deviations`・`_major_deviations`・`build_must_fix_block`(JA)・`original_must_fix`・`ja_original_check`・`ja_r2_check`・`deviation_overall_status`・`must_fix_used`・`retried_for_deviation`・`ja_recheck`・`fact_checks_summary`・`full_ledger_text=`(JA writer)・`run_deviation_check`(Family X経路から)・`er019_writer_run_summary_reconstruction`。残ってよいのはTrial参照・legacy A/B/C・`SUPERSEDED`注記済みに限る。docs側の更新漏れチェック先は14節。

---

## 7. Review Queue schema確定(DESIGN_02 5-3を確定、ユーザー決定9を反映)

- パス: `review_queue/post_en/<article_id>/` 配下に **Level別サブディレクトリ** `<article_level>__<sha8>__<rf_run_short>/`(`article_level`は`b1b`=Advanced / `a2`=Standard。**Levelをパスとschemaの両方に必須明示**)。例 `review_queue/post_en/<article_id>/b1b__a1b2c3d4__r7f9e/`。`review_queue/post_en/index.jsonl`は1行=1 (記事,Level) の追記専用。ルートは`__file__`基準(`os.getcwd()`非依存)。
  - DESIGN_02の`<article_id>__<level>__…`単一ディレクトリから、ユーザー決定9の「`review_queue/post_en/<article_id>/`」に合わせて**article_id配下へ移した**(変更点)。
- 各ファイル: `queue.json`(schema下記)・`inputs/{article.md, ledger_full.txt, sentences.json}`同梱・`raw/`(4条件の生API応答)。
- **`queue.json`必須フィールド**(ユーザー列挙を網羅): `schema_version`/`article_id`/`article_level`/`article_sha256`/`run_id`/`timestamp`/`status`(`OK`\|`PARTIAL`\|`RF_UNAVAILABLE`)/`splitter_version`/`conditions[]`(`model_key`・`condition`[A3\|A4]・`model_id_requested`・`model_id_returned`・call数・tokens・cost_jpy・status)/`issues[]`:
  `issue_id`(=`<article_id>__<article_level>__<sha8>__<sentence_id>`)/`sentence_id`/`sentence_text`/`context`(before/after最大2文。**Queue生成時のみ付与、LLM入力に入れない**)/`related_fact_ids`/`facts[]`(Fact本文=台帳ブロック全文)/`flag_reasons[]`/`detected_by[]`(`model_key`・`model_id`・`condition`[A3/A4]・`confidence`)/`confidence`/`raw_flag_source`(`raw/`内の該当応答への参照)。`unlocated_flags[]`(文IDに対応しないFlagを別掲)。
- **`review_state`は持たない**(Opus修正c。Human Reviewの判定はChatGPT側が保持、Queueは候補一覧に徹する)。
- 重複統合: キー=(article_id,article_level,sentence_id)。同一文のA3/A4・Luna/Geminiは1 issueへOR統合し`detected_by[]`を保持。
- `index.jsonl`排他: `index.jsonl.lock`(O_EXCL+retry/timeout)、追記は1行1write+fsync、既存行不変。
- ChatGPT read-only参照可: リポジトリ上のファイルでraw.githubusercontent.comから取得できる形(`.gitignore`非該当は`git check-ignore -v review_queue/post_en/index.jsonl`のrc=1で今回確認済み。`review_queue/`ディレクトリ自体は未作成)。runnerはgitを触らない。pushは運用(Open Item起票=OPEN-245)。
- 保存失敗・RF_UNAVAILABLE時の挙動はDESIGN_02 5-4を継承(Queue保存失敗は`risk_flag_fallback/`へ、可視化4点)。

---

## 8. splitter共通module・費用機構

### 8-1. splitter(DESIGN_02 7節を確定)

`er053_en_sentence_splitter_01.py`(新設、標準ライブラリ`re`のみ、Trial import禁止)。略語リスト・規則はTrial `er052_open233_self_recovery_flow_runner_01.py`の`_VS_L6_ABBREV`(L5477-5480、33語)・`_vs_l6_abbrev_period`(L5486)・`_VS_SENT_END_RE`(L4944)をProduction moduleへ移植(コピー。Trial側は無変更)。regression必須6件(`U.S.`/`U.K.`/`U.N.`/`Mr.`/`Dr.`/`Jan.`)+通常文末分割+33語網羅+Trial 11入力での等価性+他経路diff 0(`er003_ja_to_en_translation.split_sentences`・`er010 split_sentences`・Trial側は不変)。出力契約: 見出し行`# `も1文、`\n`でも分割、`sid=s1…`。`splitter_version="en_split_v1"`をQueue/evidenceへ記録。**文IDはTrial照合済みIDとずれる(承認済み)**ので、`sentence_text`+`splitter_version`で照合できるよう両方保持。依存方向: RF module→splitterのみ。**他経路への影響=なし**(既存splitterは変更しない)。

### 8-2. 費用機構(承認済み3ギャップ+audio側fail-closed。DESIGN_02 6節を確定)

| # | 修正 | 計算式・出典 |
|---|---|---|
| G-1 | `pricing_snapshot.json`へ`gemini-3.5-flash-lite`を登録(provider=`gemini`、tier Standard、meter `input_tokens`/`cached_input_tokens`/`output_tokens`、source_url・取得日・確認方法を併記) | **$0.30 input / $0.03 cached input / $2.50 output(per 1M tokens、出力はthinking tokens含む)**。出典`https://ai.google.dev/gemini-api/docs/pricing`、取得2026-10-10T04:50Z(`er052_output/writer_dev_risk_flagger_01/meta_rollback_crossmodel_01/xm_prices_01.json`)。**実装時に再確認して登録**(出典付き確認済み値のみ。fallback単価の自動使用なし)。現状`pricing_snapshot.json`に`gemini-3.5-flash-lite`は0件(今回grepで確認) |
| G-2 | Gemini thinking token計上: RFのGemini呼出はREST(SDK patch非経由)→RF moduleが`er005_cost_logger.record()`で`provider="gemini"`互換レコードを書く。SDK patch側は変更しない(他経路の費用が変わりうるため) | `cost_usd = input×0.30/1e6 + cached×0.03/1e6 + (candidates+thoughts)×2.50/1e6`、円換算`×USD_JPY(160.0)` |
| G-3 | `compute_stage_cost_breakdown`(`er019 entertainment runner` L240-271)の集計を`gemini`へ拡張(現状`provider=="openai"`のみ)。stage tag=`risk_flag.<model_key>.<A3\|A4>.<level>`で**Level別・model別・条件別**に集計 | 条件別call数/tokens/costを`queue.json.conditions[]`・`runtime_evidence.json`・`raw_usage_log.jsonl`の3点で追跡 |
| G-4(軽微3件の1) | audio側`compute_cost_jpy_so_far`(`er019 audio runner` L1528)の`except StopIteration: usd = 0.0`(単価未登録を0円扱い=fail-open、audio側`_load_pricing`はStopIterationをそのまま通す)を、efam側`_load_pricing`と同じ`PricingNotFoundError`(fail-closed)へ。**前提testとして、現行Production全model(TTS含む)の単価網羅を¥0で確認してから変更** | 承認済み費用機構修正の範囲内として実施(ユーザー決定14) |
| G-5 | Luna RFは手動記録しない(SDK patchが自動記録。二重記録test) | - |
| G-6 | RF 4本のLevel別・model別**実測**費用保存。Gemini A4が0件でも自動削除・停止・モデル変更をしない(`MODEL_STATS`に経過観察を出すのみ) | `MODEL_STATS`: articles processed/A3 flag count/A4 flag count/unique issue/overlap/zero-flag article/UNAVAILABLE・PARTIAL(モデル別×`article_level`別) |

注意(S2-5関連): Productionの予算ガード(`efam._load_pricing`/`assert_budget_ok`)はAstra単価を係数1.0で計上する(Trialの`arm_cost`はAstraに安全係数1.5)。請求ダッシュボード照合は未実施。実装コードにはAstra係数を追加しない(承認済み3ギャップ外)。代わりに**Cap設定にマージンを持たせる**(11-4)。照合はOpen Item(OPEN-246)。

---

## 9. Rollback(DESIGN_02 8節を確定)

- 隠れswitch・環境変数・CLI引数は作らない。撤去はProduction pathからの物理削除。旧コードはGit履歴+Trial artifactに保持。
- tag: 実装開始前に`rollback/pre-factlock-rf-wiring-01-20261010`(撤去直前commit、Fableが`git tag`で付与。現在tagは0件を確認済み)。完了時に`post-wiring-01`を付与。
- commit分割: **C1**=追加のみ(RF module・splitter・W-1 module・契約module・集計script・README・routing追加[FACTLOCK 2キー+RF 2キー]・pricing追加[Gemini 3エントリ]・各test)。**C2**=Writer差替え(`er019 ja_writer`呼出→W-1 module)+旧Checker撤去+契約検証の組込み+RF呼出(`er019 entertainment runner`/`er012_e`/jaw)。**C3**=audio runner tts前保険+費用機構修正(G-3/G-4)+Astra pricing note更新。**revert順 C3→C2→C1**(`git revert <hash>`、force push・履歴書換えなし)。
- 旧腕再現: `git worktree add ../eigo-radio-legacy rollback/pre-factlock-rf-wiring-01-20261010`(Trial runnerの`_SCRIPTS` sha整合のため)。
- 静的test: Production module群に`fact_check_mode`/`legacy_checker`/`OPEN243_*`/`OPEN233_*`のenv参照・CLI引数が0件。

---

## 10. Gate依存関係図・Status語彙

```
[W-1全体 PRODUCTION_WIRED]
     ▲ (3条件の論理積)
     ├─(G-A) Lane A実装完了
     │      ├ C1: 追加(RF/splitter/W-1/契約/routing/pricing)  ← Opus条件A再レビュー(S3-7)後
     │      ├ C2: Writer差替え+旧Checker撤去+契約検証+RF呼出   ← S3-3の方針(ブランチ)
     │      ├ C3: audio保険+費用機構
     │      ├ Static 10項目 PASS(12-4)
     │      └ 開発用確認run PASS(11節。※これは(G-C)ではない)
     ├─(G-B) Lane B: B3注記自動化
     │      B3-ANNOTATION-AUTOMATION-TRIAL-01 = VALIDATED
     │        → ユーザーが正式採用(APPROVED_FOR_PRODUCTION)
     │        → Production配線(契約3ファイルを`run_storyline_b3`直後に生成するstage)
     └─(G-C) 最終L3(新規記事1本の完全Production E2E)
            Research→Ledger→B3→B3注記自動化→Fact Lock R0(Luna)→Astra R1/R2→Advanced英訳
            →Advanced RF→Standard Level調整→Standard RF→Queue→TTS→技術QA
            前提: (G-A)と(G-B)の配線完了後。テーマ・Cap=L3直前にユーザー判断
```

**Status語彙(SSOT記録用、PRODUCTION_WIREDを誤宣言しないため固定)**

| 対象 | 現在 | Lane A完了時 | 全体WIRED条件 |
|---|---|---|---|
| W-1(新Writer) | `APPROVED_FOR_PRODUCTION`(未配線) | `APPROVED_FOR_PRODUCTION`・W-1下流実装完了(部分)、**B3注記未配線につき未PRODUCTION_WIRED** | (G-A)∧(G-B)∧(G-C) |
| RF 4条件(Luna A3/A4、Gemini A3/A4、両Level) | `APPROVED_FOR_PRODUCTION`(未配線) | **「RF配線完了(部分)、全体未WIRED」**(RF部分の実機確認事実は記録可) | 全体WIREDとは書かない |
| 旧Checker撤去 | `APPROVED_FOR_PRODUCTION` | 撤去完了(部分)、全体未WIRED | 上と同じ |
| B3注記自動化 | `Trial`(Lane B) | 変更なし | VALIDATED→ユーザー採用→配線 |
| OPEN-233系Checker | Production未配線 | `SUPERSEDED`(2026-10-10整理済み、履歴保持) | - |

**RF部分単体の配線完了事実の記録方法**: `OPEN_ITEMS.md` OPEN-244の本体行に「配線進捗」欄(日付・commit・実機確認run名・「RF配線完了(部分)」)を追記し、`DECISION_LOG.md`へ実施記録を残す。**`CURRENT_SPEC.md`はW-1全体PRODUCTION_WIREDの確定時に更新**(部分完了では更新しない。CURRENT_SPECは現行の正式運用を表す正本であり、旧Checker撤去済み・RF常時実行・W-1運用は(G-B)が欠ける間は成立しないため)。

---

## 11. Lane Aで今回実施可能なRuntime確認(最終L3の前)=「W-1下流 開発用確認run」

### 11-1. 目的・範囲

既存の**注記済みB3 Trial artifact**を3節の契約3ファイルへ変換(¥0のDEV adapter)して与え、**W-1下流のProduction実装**(契約検証→R0 Luna→Astra R1/R2→Advanced英訳(M1(a))→Advanced RF→Standard Level調整→Standard RF→Queue保存→(保険)→TTS→技術QA)が、Production正式path(`er019 entertainment runner`→`er019 audio runner`)で動くことを確認する。**確認できること**: 下流の配線・Queue・費用記録・RF位置・技術QA維持。**確認できないこと**: B3注記自動化(Lane B)、新規記事のresearch/ledger/B3、注記自動化込みの完全E2E。

### 11-2. 入力(例)

Trialの注記済み成果物: `er052_output/factlock_astra_e2e_trial_01/annotation/final/<slug>/{selected_brief_factlock.md, annotation.json}`+凍結台帳+原B3(`FROZEN`表: `er052_factlock_astra_e2e_runner_01.py` L33-)。候補は**数値の中核/周辺印を含むテーマ**(例 `hormuz`、20％【中核数値】等を今回確認)と**印なし・軽量**(例 `meta`、3事実・numbers空を今回確認)。どちらを使うかはFable/ユーザー判断(新規記事ではなく既存Trial入力の再利用なので、PM_GOVERNANCE 13節の新規記事テーマ選定には当たらない見込みだが、Fableが確認)。runnerはresearch_ledger/storyline_b3が`out_dir`に既にあれば再利用分岐に乗る(`run_research_and_ledger`の既存Ledger再利用、`selected_brief.md`再利用、確認済み)ので、fixtureの置き方で新規のswitchは不要。

### 11-3. 呼称ルール(「W-1完全Production E2E」と呼ばない)

- 正式名称: **「W-1下流 開発用確認run」**(`W1_DOWNSTREAM_DEV_CONFIRM`)。報告・REPORT・RESULT_PACKET・DECISION_LOG・`entry_point.json`のメタ欄(`--run-label`は**制御に影響しない記録専用の自由文字列**)すべてでこの名称を使う。
- 禁止表現: 「W-1完全Production E2E」「最終L3」「L3 PASS」「新規記事E2E PASS」「W-1 PRODUCTION_WIRED」。
- 許容表現: 「W-1下流+RF+Queue+TTS+技術QAの実機確認(B3注記は既存Trial artifact経由・自動化は未確認)」。
- 結果を(G-C)の代替にしない(10節)。

### 11-4. 費用見積(根拠行は既存実測。未確認は未確認)

| 工程 | 値 | 根拠 |
|---|---|---|
| research+ledger+B3+B3注記 | **¥0**(既存Trial artifact再利用) | 11-2 |
| 契約検証・adapter | ¥0 | - |
| Luna R0 | 約¥1.24(実測) | REPORT §114 |
| Astra R1+R2 | 約¥30.6/生成(raw実測。Production budget guardは係数1.0=¥30.6、Trial方式の×1.5なら¥45.9) | REPORT §111 |
| EN Advanced+Standard(Checkerなし) | **≤¥4.22**(既存実測はChecker込み=上限値。Checkerなし単独は未測定) | DESIGN_01 11-3 |
| RF 4条件×両Level | 約¥1.49(Adv実測¥0.747、Stdは外挿=未確認) | DESIGN_01 8-4 |
| **(a) JA→RF→Queue(TTS無し)小計** | **約¥37.6(raw)〜¥52.9(Astra×1.5)** | 上記の和 |
| 音声(TTS+ASR+KP) | ¥23.98〜¥89.03(run間差、条件差は未確認) | DESIGN_01 11-3 |
| **(b) TTS込み合計** | **約¥61.6〜¥126.6(raw)、Astra×1.5なら〜¥142** | (a)+音声 |

- **Cap提案(ユーザー判断)**: 二段階。段階1=(a)のみ、上限¥60(`--budget-jpy 60`)、TTS無し(`--stop-after standard`)。段階2=(b)、累計上限¥150(runner既定`--budget-jpy 150`)。段階1の実績を見てから段階2へ進む。**注意**: 前タスク群の固定STOP条件「累計JPY60到達」に段階1の上限がちょうど触れるため、**実行前にCap承認が必要**(S3-6)。今回の設計委任は課金0。
- 実行はPhase 2(C1〜C3実装+Static全PASS+Opus条件A再レビュー後)。

### 11-5. 確認項目(Runtime evidence。DESIGN_02 9-1のE1〜E15から、本runで確認できるものを抽出)

E1(W-1 moduleがProduction経路で実行、Trial module非import)・E2(model_id requested/returned、mismatch 0。Astra不一致=STOP)・E3(旧Checker呼出0、`raw_usage_log.jsonl`のstage tagで確認)・E4(Advanced RF→Standard生成→Standard RFの順序、timestamp)・E5〜E8・E10・E11(Queue push運用とraw URL取得)・E12(RF_UNAVAILABLE fault injection=¥0)・E13(TTS以降の技術QA)・E14(非対称②行8・16)・E15(費用)。**契約検証(V1〜V9)の合格ログ**と、故意に壊した契約での即STOP(¥0 fault injection)を追加する。E9(OR統合の実例)は無ければfixtureで補完を明記。**確認できない**: 注記自動化(Lane B)、新規research/ledger/B3(L3固有)。

---

## 12. 実装順序・変更ファイル・テスト・Gate 3

### 12-1. 変更ファイル一覧(DESIGN_02 11-1から更新。★=今回変更)

| # | ファイル | 種別 | 規模(見込み) |
|---|---|---|---|
| 1 | `er053_family_x_risk_flagger_production_01.py` | 追加(RF本体) | +700〜900 |
| 2 | `er053_en_sentence_splitter_01.py` | 追加 | +100〜150 |
| 3 | `er053_risk_flagger_aggregate_01.py` | 追加 | +120〜180 |
| 4 | `review_queue/post_en/README.md` | 追加 | 小 |
| ★5 | `er053_family_x_factlock_ja_writer_01.py`(W-1、2節) | 追加 | +350〜450(DESIGN_02の+400〜600から、Checker関連が無くなり減) |
| ★6 | `er053_annotated_b3_contract_01.py`(3節) | 追加 | +150〜250(DESIGN_02の「注記stage+300〜500」はLane Bへ移り、本Laneは契約検証のみ) |
| ★6b | `er053_dev_annotated_b3_fixture_adapter_01.py`(DEV専用) | 追加 | +80〜120 |
| 7 | `er006_model_routing_contract_01.py` | 追加のみ(FACTLOCK_R0/REVISE+RF 2キー) | +15 |
| 8 | `pricing_snapshot.json` | 追加(Gemini 3エントリ)+Astra note更新 | +3 |
| 9 | `er019_family_x_audio_production_runner_01.py` | 変更(tts前保険+費用fail-closed) | +80〜120 |
| 10 | `er019_family_x_ja_writer_o_r1_r2_01.py` | 変更(Fact Check削除+例外分離。6-2) | −150〜200 |
| 11 | `er012_e_family_entertainment_two_level_runner_01.py` | 変更(Checker撤去+M1(a)無条件ON+RF呼出受け口) | −300〜350 |
| 12 | `er019_family_x_entertainment_production_runner_01.py` | 変更(契約検証+W-1呼出+Checker引数削除+RF呼出+gemini集計) | ±100 |
| 13 | tests(12-3) | 追加・更新 | +1,100(既存8本前後の更新含む) |
| 14 | `er019_writer_run_summary_reconstruction_01.py`(+test) | legacy注記 | 小 |
| 15 | CURRENT_SPEC/PM_BRIEF | 全体WIRED確定時のみ(14節に更新予定箇所) | 小〜中 |

合計: **新規約+1,500〜1,900行、テスト約+1,100、削除約−500**(DESIGN_02の+1,700〜2,100から減)。変更しない: A3/A4 Prompt、`vfl01`共有関数、legacy A/B/C、既存splitter、Trial dir、`adv_gen`のM1 Prompt本体。

### 12-2. 順序・ブランチ方針(S3-3)

1. **前提**: Opus独立レビュー(条件A: 契約interface+新パイプライン順序という新しい構造設計。内容が変わったため再レビュー)→ Fable照合(S3-7)。
2. **C1(追加のみ)**: 既存Production挙動を一切変えない。mainへ通常どおりcommit/push可。
3. **C2/C3**: 適用後は「注記なしB3ではWriter段で即STOP」になり、**Lane B配線までProduction runnerで新規記事を作れない**。推奨=作業ブランチ(例`feature/w1-wiring-01`)+worktreeでC2/C3と開発用確認runを実施し、(G-B)の配線が済んだ時点でmainへ統合。mainに入るまで既存Production(旧Writer+旧Checker)は動き続ける。代替(C2をmainへ即統合)は、新規記事生産が(G-B)まで止まる運用リスクを伴う。→ **ユーザー判断(S3-3)**。
4. 並列可(独立ファイル・独立test。同一ファイルの並行編集は禁止): RF module+Queue/aggregate、splitter+golden、W-1 module+Prompt同一性test、契約module+契約test、routing/pricing(Gemini単価再確認含む)、台帳全件走査test、静的test枠。直列(理由=同一ファイル/順序依存/予算Guardrail/runtime evidence): C1→C2(`er019 ja_writer`/`er012_e`/`er019 entertainment runner`は1ファイル1担当)→C3→static/unit回帰→開発用確認run(API支出)→SSOT更新。クリティカルパス=Opus再レビュー→C1(W-1+契約)→C2→開発用確認run。

### 12-3. テスト計画(全て¥0、mock/fixture/既存artifact)

DESIGN_02 10節のT-1〜T-12を引き継ぎ、次を追加・更新: **T-8a**=2-2表のsha30項目の同一性+合成Prompt一致(2-2 C)、**T-8b**=R1→R2の入力が「R1の生出力」であること(Trial逐語)・postprocess順序・TagLeak/echo、**T-13**=契約検証V1〜V9(正常・各違反・stale・注記なしB3を渡してAPI呼出前にSTOP・フォールバック経路が存在しないことのAST検査)、**T-14**=DEV adapterがProduction moduleから参照されないこと、**T-15**=Advanced→Advanced RF→Standard生成→Standard RFの呼出順序(mock)とStandard入力がb1b/article.mdであること、**T-16**=M1(a)がAdvancedでのみ呼ばれ段落retry再生成でも同じ関数であること、**T-2**はM1(a)無条件ON化に合わせ「`OPEN243_*` env参照0」を維持。

### 12-4. Gate 3チェックリスト(PM_GOVERNANCE Gate 3/4)

**Static(10項目)**: S1 Production moduleが`er050`/`er051`/`er052*`をimportしない(DEV adapterはProductionから参照されない) / S2 旧Checker呼出0(AST+grep、6-4) / S3 各経路で旧Checker不到達(spy) / S4 A3/A4 prompt shaとW-1 Prompt定数shaが契約表一致 / S5 model固定(routing 4キー・env上書きなし・fail-closed・pricing登録) / S6 RF非Blocking / S7 splitter golden+他経路diff 0 / S8 Dangling Reference 0 or `SUPERSEDED` / S9 隠れswitch0(注記なしB3フォールバック含む) / S10 Standard/Advanced対称test(意図的差=M1(a)のみAdvanced)PASS。
**Runtime**: 開発用確認run(11-5。(G-A)の一部)+最終L3(E1〜E15、(G-C))。
**Model evidence**: requested/returned model_id・routing key・単価出典(URL・取得日)・1記事費用・Astra請求照合状況を`runtime_evidence.json`+REPORTへ。
**Status**: 10節の語彙に従う。Gate 3全充足まで`PRODUCTION_WIRED`にしない。

---

## 13. STOP候補の整理(DESIGN_02のS2-1〜S2-12の解消状況+新規)

| ID | 状態 | 内容 |
|---|---|---|
| S2-1 新Writer仕様 | **解消** | W-1確定(ユーザー決定1) |
| S2-2 B3注記自動化 | **Lane Bへ移管** | 本LaneはV1〜V9の入力契約まで |
| S2-3 Prompt採用 | **解消(移植契約で担保)** | 2-2。Prompt変更は0件。変更が要るのはS3-1の案Bのみ |
| S2-4 M1(a) | **解消** | Advanced限定を正式維持(①意図的差) |
| S2-5 Astra請求照合 | **Open Itemとして継続**(OPEN-246)。Lane Aの実装は止めない | Productionの予算ガードは係数1.0(8-2注意) |
| S2-6 L3 Cap | 開発用確認runのCap提案=11-4。最終L3のCap=L3直前にユーザー判断 | - |
| S2-7 L3テーマ | L3直前にユーザー判断 | - |
| S2-8 audio fail-closed | **ユーザー決定14で承認済み** | 実施(G-4) |
| S2-9 Opus条件A | **S3-7として継続(Fable手配)** | - |
| S2-10〜12 | S2-10(splitter複製禁止の解釈)=8-1で確定扱い(Production内で1実装)。S2-11=OPEN-245。S2-12=OPEN-233 SUPERSEDED整理(15節で反映済み) | - |

**新規STOP候補・要判断(勝手に解決しない)**

| ID | 内容 | 該当する固定STOP条件 | 推奨 |
|---|---|---|---|
| **S3-1** | **Astra段(R1/R2)の記号QA再生成の方式**。TrialはfindingsをR2 responseに記録するだけで再生成しなかった。Productionの既存方針(T-02)は「検出時に1回再生成→なお残ればSTOP」。Astra段にこれをどう適用するか: **案A**=Promptを変えず同じuser文でAstraを1回だけ再実行(上限1=既存T-02と同じ。Prompt変更なし)/ 案B=既存`build_symbol_violation_prompt_note`をuser文末尾に追記して1回再生成(**Prompt変更**に当たる)/ 案C=再生成せず即STOP。Trial 16応答では発動0件 | Prompt変更が必要(案Bの場合)・新仕様候補 | 案A(Prompt不変・上限1維持)。ユーザー確認。C2のR2記号QA部分だけがこの回答待ち |
| **S3-2** | StandardがAdvanced単独再生成後に古いAdvanced由来のまま残りうる(5節行8、②-a)。観測として`a2/audit/derived_from_advanced_sha256`を記録する提案(判定・STOPには使わない) | 新仕様候補(軽微、観測のみ) | 提案採用はFable判断。不採用でも実装は止まらない |
| **S3-3** | C2/C3のmain統合タイミング(12-2)。即統合すると(G-B)まで新規記事生産が止まる | 運用リスク(Production影響) | feature branch+worktreeで(G-B)配線まで保持。ユーザー判断 |
| **S3-4** | jaw/`er012_e`のFact Check削除により、HEAD上の`er052_*` Trial runnerがimport不能になる(git tag+worktreeで再現) | DESIGN_02 8節の前提と同じ | 確認のみ |
| **S3-5** | W-1の既知欠陥: brief内の指示文がFact Lock R0に事実扱いされる(OC-11、REPORT §111訂正(1)、semiconductorで新腕固有STOP事例)。Prompt/構造の変更はユーザー決定1で禁止のため本Laneでは扱わない。検知はRF/Human Review | Prompt変更が必要(対策する場合) | Open Item起票の要否はFable判断 |
| **S3-6** | 開発用確認runのCap(11-4)と、前タスク群の固定STOP「累計JPY60到達」との関係 | 累計JPY60到達 | ユーザーがCapを承認 |
| **S3-7** | Opus条件A再レビュー(契約interface+パイプライン順序+C2/C3方針)。Opusレビュー後はFable判断で次工程へ(PM_GOVERNANCE 11-3) | 必須Gate | Fableが手配 |

STOP候補の検査結果(委任文の指定): Prompt変更が必要=S3-1案Bのみ / W-1移植で改変不可避=**なし**(2-2 D) / 非対称②で新仕様判断=**なし**(S3-2は観測提案) / 技術QA境界が解消できない=**なし**(B-1/B-2は6節で解決、T-19追加) / Queue保存がProduction構造と競合=**なし**(`review_queue/`は新設ディレクトリ、.gitignore非該当を確認) / splitter共通化が他経路に影響=**なし**(既存splitter無変更)。

---

## 14. CURRENT_SPEC更新予定箇所(**今回は変更しない。W-1全体PRODUCTION_WIRED確定時に更新**)

grep実測(HEAD): L822(Fact Safety行: 旧Checker→W-1+RF+Human Review)/L1230〜L1267付近(項目4/5・W6 ja_source差し戻し・Checker再設計言及)/L1536〜L1538(Fact Checker・Ledger Deviation Checker v2)/L1870〜L1871(Hook-aware Checker・Local Rewrite)/L1951(Fact Checker retry cap)/L2067(JA Fact Check must-fix)/L2302(routing表: FACTLOCK_R0/REVISE+RF 2キー追加)/L2322付近(Ledger Deviation Checker GPT-6 Trial結果の位置づけ)。新設すべき節: 「新Writer W-1(Fact Lock+Astra)」「注記済みB3入力契約」「Risk Flagger(両Level)とReview Queue」「M1(a)=Advanced限定の意図的Level非対称」。併せて`docs/pm/PM_BRIEF.md`のWriter/Checker記述(Fact Lock/Astraは現状0件)。

---

## 15. SSOT記録(今回実施)と付録

### 15-1. 今回のSSOT変更箇所

- `DECISION_LOG.md`末尾: 2026-10-10ユーザー決定エントリ(W-1正式採用、W-2/3/4不採用、注記版B3前提+自動化は別Trial、W-1はB3注記配線までPRODUCTION_WIREDにしない、RF 4条件両Level APPROVED、RF位置、M1(a) Advanced限定=意図的非対称、旧Checker撤去範囲[R2後JA含む]、OPEN-233 SUPERSEDED整理、費用機構修正承認、文ID変更承認、Queue push運用+Open Item、L3テーマ・CapはL3直前判断)。
- `OPEN_ITEMS.md`: OPEN-244本体行を更新(W-1確定・Gate依存・配線進捗欄。旧本文は`OPEN_ITEMS_HISTORY.md`へ原文のまま切り出し)/新規OPEN-245(Review Queue push責務)・OPEN-246(Astra請求照合)/OPEN-233、OPEN-233-A1-PROD、OPEN-233-SELF-RECOVERY-PRODUCTION-WIRING-01、OPEN-233-CHECKER-FLOOR-PRODUCTION-E2E-01の各行頭へ`SUPERSEDED`整理を追記(履歴は削除せず保持)。
- `CURRENT_SPEC.md`: **変更なし**(14節)。

### 15-2. 付録: 根拠コマンド(再現)

- sha256: `.venv/Scripts/python.exe -X utf8 <scratchpad>/sha_list.py`(Trial module/Production moduleをimportして文字列・`inspect.getsource`のsha256を出力)。ファイルblob: `git rev-parse HEAD:<file>`。
- Astra symbol findings: `er052_output/factlock_astra_e2e_trial_01/runs/*/new/new_writer/r[12].response.json`の`symbol_gate_findings`(16件、全て空)。
- Standard=Advanced派生: `er012_e_family_entertainment_two_level_runner_01.py` L615/L617。
- review_queue: `git check-ignore -v review_queue/post_en/index.jsonl` rc=1、`ls review_queue`=不在。
- tag: `git tag`=0件。
