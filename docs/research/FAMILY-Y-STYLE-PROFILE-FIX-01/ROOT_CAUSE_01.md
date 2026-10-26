# ROOT_CAUSE_01 — OPEN-537 根本原因(ユーザー§1A の4問)

管理ID: FAMILY-Y-STYLE-PROFILE-FIX-01 委任_01 / 2026-10-26 / read-only(API 0・JPY0・コード/SSOT/run dir編集0)。
表記: 「事実」=ファイル:行・commit・日時。「所見」=推論(事実と分離)。記録が無いものは「記録なし」。原文出典=`docs/pm/delegation_log/2026-10-26_FAMILY-Y-STYLE-PROFILE-FIX-01_USER.md`。
出発点=`docs/research/TTS-RETRY-FALLBACK-REWRITE-AUDIT-XYZ-01/Y_F01_STYLE_PROFILE_CHECK_01.md`(主要点を本委任で再照合)。

## 0. 結論(先に)
- 分類: **B(承認済み仕様との不一致)=不具合**。PM_GOVERNANCE 11-8(`PM_GOVERNANCE.md:2558-2572`)の不具合判定テストT1に該当(コード挙動=`default`が、承認済み設計・台帳・共通仕様原則と矛盾)。「ユーザー判断待ち」ラベルは新設/拡大にのみ付ける(同:2568)。
- 直接原因: `er121_family_y_runner_01.py:37 STYLE_PROFILE = "default"`(導入=`7d5b9f8fc`、2026-10-25 20:27:10 +0900、理由コメントなし)。これがTTS生成(:988,:990)・gate(:1016)・assemble(:1034)・stage入力sha(:966)へ渡り、基底6-role Styleだけが送信された。
- 構造原因(3層): (1)実装: Yがprofile解決(`resolve_run_profile`)を呼ばず固定記録も作らない (2)検出: Gate/構造一致test/受入のいずれも「profile実測値==承認値」を検査せず、`checked=[]`をPASSとする (3)管理: 台帳の残作業がOPEN-415(エンジン化の要否判断)に紐づき、「Y配線」の実装タスクにならなかった。
- 意図: **意図的除外の記録なし・後回しの明示記録なし**。所見=実装時の暫定値が残った見落としの可能性が高いが、実装者の意図を直接示す証拠は無い(不明)。

## Q1. なぜ設計・台帳は継承なのに、runnerは `default` になったか
事実(承認側=継承):
| 出典 | 内容 |
|---|---|
| `docs/research/FAMILY-Y-PRODUCTION-LAUNCH-01/DESIGN_01.md:84` | 「Style: profile `fx_20261017`を継承(OPEN-415はZ方式[定数参照+drift test]を採用)」 |
| 同`spec_ledger_04.json:231-243` YL-A01 | `y_applicability: APPLY` / `y_wiring_status: "DEV Trialはprofile継承+Y style gate(YL-C11)"` / `remaining_work: "Y新runのStyle記録+drift testへCROSS_FAMILY_COMMON_STYLE_MAP相当を追加"` / `completion_evidence: "Y runのaudit/style記録がprofile一致・旧style混在を課金前STOP"` |
| `docs/research/FAMILY-Y-VOICES-DESIGN-01/DESIGN_PROPOSAL_02.md:109,242`(A19,T10) | 「Full Story相当の5パートはPD06を適用(Voice別Styleは設けない)」「`fx_20261017`をそのまま」 |
| `er110_family_y_audio_trial_01.py:40,171` | DEV Trial=`STYLE_PROFILE="fx_20261017"`+`resolve_run_profile(theme, STYLE_PROFILE, write=True, …)`(固定記録作成) |
| `CURRENT_SPEC.md:1699-1706`「共通仕様のFamily別配線Status表」Y列 | PD06/S3/E1/K2/P8-KP/P7とも「未着手(Y化時に最初から配線対象)」(2026-10-17以降未更新) |
| `docs/pm/delegation_log/2026-10-17_FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01_COMPLETION-AND-CROSS-FAMILY_USER.md:126-127`(=PM_GOVERNANCE 28-1 運用6,7) | 「Family固有仕様およびユーザーが明示的に不採用とした仕様は例外」「新規Family(将来のY等)をProduction化する際は、既存の共通承認仕様を最初から配線対象に含める」 |
| `…FAMILY-Y-PRODUCTION-LAUNCH-01_USER.md:162-166`、`…_USER_02.md:70-80,150,153`、`…FAMILY-Y-VOICES-DESIGN-01_USER_09.md:64,66` | 一般規定(Yも適用対象/既存の正式な速度・Style・TTS設定を継承/未承認のStyle変更を追加しない)。個別Style名の名指しなし |

事実(実装側=default):
- `git log -S "STYLE_PROFILE" -- er121_family_y_runner_01.py` → `7d5b9f8fc`(委任_02B、`STYLE_PROFILE = "default"`が初出、同commit:36)の1件のみ。以後`default`のまま(変更commit 0)。commit本文にStyle言及なし。
- 委任_02Bの指示文`docs/pm/delegation_log/2026-10-25_FAMILY-Y-PRODUCTION-LAUNCH-01_DELEGATION_02B.md:8`(M-3)は「…TTSのPNAP hook・Run Entity Table・Chunk判定・prune_cached・style record…は**X/Zが使う共通moduleを直接importして呼ぶ**」と指示。同ファイルのStyle言及はこの1箇所のみ(Grep)。
- Y音声module(`er121_family_y_audio_01.py:544,632`)はXの関数シグネチャを継承した`style_profile: str = "default"`既定引数を持つ(Xでは「defaultは現行とバイト同一」の後方互換: `er019_family_x_style_profile_01.py:13-14,229-230`)。Xのrunnerは`resolve_run_profile`で解決した値を渡す(`er019_family_x_audio_production_runner_01.py:3352-3357`)が、Yのrunnerはリテラルを渡す。`resolve_run_profile`のGrep(`er121_*.py`)=0件。
- 「意図的除外」「後回し」の記録: DECISION_LOG/OPEN_ITEMS/CURRENT_SPEC/UDR/commit本文/EVIDENCE_01〜03/OPUS_REVIEW_01のGrep=0件(Y_F01 §3)。
- OPEN-415(`OPEN_ITEMS.md:927`)は「Y導入時にprofileエンジン化の**要否を判断**する…設計課題の記録。Production挙動変更なし」であり、Y配線そのものの実装タスクではない。

判定(証拠ベース): 「意図的除外」=**否**(除外の承認・記録が0件)。「後回し」=**宣言記録なし**。「見落とし」=**疑い高・直接証拠なし(所見)**。
所見(事実ではない): Y runnerは「Z型stage framework」で作られた(`7d5b9f8fc`のcommit題)。Zはprofile記録を持たず定数参照(`er063_family_z_audio_01.py:266-283`)で、テンプレート側に`resolve_run_profile`の呼出し例が無かった。M-3は「style record」と書いたが、Y runnerでのresolve呼出しを要求する文は無く、構造一致test(下記Q2)にも載らなかった。

## Q2. なぜ配線・受入検証で検出できなかったか
事実:
1. **Gateが「記録なし/空」をPASSにする**: `m3_assembly_gate`は`profile_id==default`で`{"status":"PASS","checked":[]}`を返す(`er019_family_x_style_profile_01.py:695-696`)。Y Gateはこれを呼び(`er121_family_y_audio_01.py:798`)、Adv側検査は`prof=get_profile(style_profile)["overrides"].get("FULL_STORY")`が`None`のとき実行しない(`:802,815` `prof=…get("FULL_STORY")` → `if prof is not None:`)。「profileがdefaultである」こと自体を検査する行がない。run_01の`y_style_profile_gate.json`は`x_gate={status:PASS, checked:[]}`(Y_F01 §4)。
2. **固定記録が無くても通る**: Yは`audit/style_profile.json`を作らない。`assemble_level`/Gateは記録の存在を要求しない(Y側に`read_record`呼出し0件)。
3. **構造一致test(M-3b)の網羅範囲外**: `er121_family_y_structure_match_test_01.py:75-82`の`_check`は、Xの`generate_family_x_b1_segments`/`generate_family_x_a2_segments`が呼ぶ共通関数がY音声module内に存在するかだけを比較する(呼出名の集合)。Xのrunner `main`の`resolve_run_profile`呼出し(`er019_family_x_audio_production_runner_01.py:3352`)も、引数の**値**(`default`リテラル)も対象外。profile関連の項目は許可リストにも比較対象にも0件(`_base_role_style`のみ:61)。
4. **台帳の完了証拠が検査に落ちていない**: YL-A01の`completion_evidence`「Y runのaudit/style記録がprofile一致・旧style混在を課金前STOP」は文言のみで、対応するtest/Gateが無い(`spec_ledger_04.json:243`)。追跡先はOPEN-415/520(エンジン化の要否判断)で、実装タスク化されなかった。
5. **runtime evidenceにStyle項目が無い**: E-1 EVIDENCE_01〜03とOPUS_REVIEW_01にStyle profile確認の記述0件(Y_F01 §3-5)。EVIDENCE_02 F-4(`EVIDENCE_02.md:88`)は「y_style_gateのPASS≠音声OK」を指摘したが、「PASSでもStyleが承認値か」は問われなかった。
6. **PM Closeout項目33の充足方法**: 項目33(`PM_GOVERNANCE.md:618-625`)は「未配線のFamilyがあれば理由・残作業・解消条件をOPEN_ITEMSに**記録したか**」を問う。YL-A01の残作業はOPEN-415/520に記録済みのため、記録の存在で充足され、実測Styleの照合には進まなかった。
7. **Y列の更新なし**: `CURRENT_SPEC.md:1699-1706`のY列は「未着手」のまま、Y Production run公開(`user_test/family_y_production_redelivery_fee_01/`)でも更新契機がなかった。Y節(`CURRENT_SPEC.md:3082-3115`)にStyle継承の記述0件(Grep)。
所見: 失敗の型は「**仕様が文書(台帳)にあるだけで、実行時に実測値と突き合わせる仕掛けが無かった**」。XはM2/M3、Zは`assert_style_table_integrity`(`er063_family_z_audio_01.py:303`、runner起動時`er026_family_z_fiction_production_runner_01.py:1335`)でruntime assertがあり、Yだけ欠落(Z側の実測prefix照合の網羅性は本委任では未確認)。

## Q3. なぜ発見後も完成版提出を優先したか(Fable/PMの判断経緯。弁明ではなく事実)
| 日付(2026-10-26) | 事実 | 出典 |
|---|---|---|
| TTS棚卸し統合 | U-15=B疑い・高。「Fable確認先行」。再配達完成版の制作は(A)default固定/(B)fx切替のどちらも可能と整理。是正は未実施 | `docs/pm/RESULT_PACKET_TRA2.md:30-34` |
| 〃 | OPEN-537起票、11-8分類=B「修正へ進む候補・重要度高。ただし**適用時期はユーザー判断**」。UDR-TRA-3: 選択肢①次記事から/②再配達も是正して再生成、Fable推奨=①(理由=「ユーザーが試聴済みの現行版と同条件を保てる・Voice 1変更の効果を単独評価できる・費用最小」) | `OPEN_ITEMS.md:1052`、`docs/pm/USER_DECISION_REGISTER_01.md:466` |
| FINAL-PUCK-01 委任文 | ユーザー指示原文: 「Voice 2／3、その他の正常な音声は原則再利用」(:32)、**「ただし、再利用によって最新の承認済みProduction仕様や品質検査と不整合が生じる場合は、必要な部分のみ再生成・修正すること」**(:33)、「現行の正式TTSモデル・Style・速度・Retry／Fallbackを使用」(:38) | `docs/pm/delegation_log/2026-10-26_FAMILY-Y-REDELIVERY-FEE-FINAL-PUCK-01_USER.md:32-33,38` |
| 〃 実行 | 現行runner(`default`)のまま制作。報告に「Style=default(現行公開版と同一、U-15未解決)」と明記して提出(`_02`) | `docs/pm/RESULT_PACKET_YRF2.md:6` |
| 〃 後 | UDR-TRA-3「変更なし・ユーザー判断待ち継続」。OPEN-540(TTS統一)のScope外とした | `DECISION_LOG.md:22590`、`OPEN_ITEMS.md:1052` |

事実としての整理(判断主体=Fable。評価語は避ける):
- 「適用時期」をユーザー判断に分類した根拠は、ユーザーの「Voice 1だけ再生成・他は再利用」指示(:32)との衝突回避とされている。一方、同指示の次文(:33)は「承認済み仕様と不整合が生じる場合は再生成」を明示しており、Style不一致はこれに該当しうる。
- 11-8(`PM_GOVERNANCE.md:2564,2568`)は、不具合の是正を「ユーザー判断待ちにしない」、「ユーザー判断待ち」ラベルは新設/拡大のみと定める。OPEN-537は不具合(B)と分類されたまま「適用時期=ユーザー判断」が付いた(分類と扱いの不一致)。
- 28節運用7・Closeout項目33(`PM_GOVERNANCE.md:618-625`)に照らすと、Y初回E-1(宅配)公開の時点で未配線のまま提出されたことになる。

## Q4. なぜPM Gate・SSOT管理で止められなかったか
事実:
1. **Gate 7受入記録の必須5項目**(`PM_GOVERNANCE.md:276-285`)は「(3)証拠(ファイル:行・観測値)」「(4)目的要件との一致/不一致」を求めるが、**正式経路のStyle/Voice/モデル実測値を承認仕様と照合する項目は無い**。Y初回の目的(Y Production化)に対し「共通仕様のStyle」が必須証拠として列挙される構造ではなかった。
2. **Closeout項目33は記録存在の確認**(Q2-6)。Y列は「未着手」表記のまま、OPEN-415/520へのリンクで充足。
3. **OPEN-537の扱い**: 「修正へ進む候補・適用時期ユーザー判断」(`OPEN_ITEMS.md:1052`)。11-8の分類(B=不具合=是正)とラベル運用(`PM_GOVERNANCE.md:2568`)が一致していない。
4. **CURRENT_SPEC**: Y節(`:3082-3115`)にStyle継承の明記なし。共通仕様Status表のY列(`:1699-1706`)は「未着手(Y化時に最初から配線対象)」のままで、Y Production公開後の更新契機・責任者が決まっていなかった。Gate 7 (a)〜(m)の音声artifact受入チェックリスト(`PM_GOVERNANCE.md:295-`)はplayer/試聴ページ要件が中心でStyle項目なし。
5. **テンプレ側**: 28-2運用2(`PM_GOVERNANCE.md:3612`)は「他対象Familyへの配線状況確認」を要求するが、確認方法が「Status表を見る」止まりで、機械照合(testやGate)の要求ではない。
所見: 止められなかった主因は、確認が全て**記録の有無**で、**実行時の実測値**の確認が必須証拠に入っていなかった点。個人の見落としではなく、Gate 7・項目33・構造一致testの3つが同じ盲点(実測値非照合)を共有していた。

## 再発防止との対応
Q1→DESIGN_01(runnerのresolve化)、Q2→PREVENTION_01(a)(c)(d)(fail-closed Gate・全roleカバレッジ・drift/構造test)、Q3/Q4→PREVENTION_01(b)(PM_GOVERNANCE改訂案)。
