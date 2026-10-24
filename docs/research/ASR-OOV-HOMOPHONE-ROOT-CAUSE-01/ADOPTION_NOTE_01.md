# ADOPTION_NOTE_01 (ASR-OOV-HOMOPHONE-ROOT-CAUSE-01 委任_03) E2W 採用申請文の草案(Fable→ユーザー用。**草案であり承認ではない。Production変更0**)

根拠資料: `TRIAL_03_RESULT_01.md`(実測)、`DESIGN_03.md`(配線・Store制限設計)、`OPUS_REVIEW_02.md`(条件Cレビュー)、`DESIGN_02.md`/`TRIAL_02_RESULT_01.md`/`ROOT_CAUSE_01.md`。Status案=VALIDATED_LIMITED(最終判定はFable)。

## 1. 何の申請か(1段落)
英単語ガチャ記事で起きた「辞書にない語(gacha)をASRが同音の辞書語(gotcha)と書いてNGになり、TTS再試行・Azure・Local Rewrite・HR Lock・人間承認の連鎖が起きた」問題への対策として、**Ledger(Tier3調査で登録した出典付きの読み)と音素が完全一致する同音語をASRが書いた場合に限り、独立エンジン(ローカルWhisper)も同じ位置で一致したときだけ`PASS_WITH_WARNING`で受理する層(E2W)**をFamily X/Zの本番経路へ追加することの採否。

## 2. 先に訂正する点(Opus条件C OF-OOV-09)
1. **「TRUE_CONTENT_MISMATCHをPrimaryの判定だけで受理する初めての経路」ではない。** er109(表記違い同音の同値判定、2026-10-23ユーザー承認、X/Zのみ、`er006_secondary_asr_01.py:1135`)が、独立エンジンなしでPrimaryの判定だけで`TRUE_CONTENT_MISMATCH`を受理する**先例**。E2Wの新しい点は、**Tier3調査で作った二次情報のLedger読み(`evidence_tier=NAME_IN_CITED_PAGE`=名称は出典にあるが読みの本人音声は無い)を根拠にする点**。E2Wはer109より厳しい形(ローカルWhisperの位置一致を必須)。
2. **E2は過去に保留した方式の再導入。** OF-184で「直接音素置換は範囲外。需要はtelemetryで測る」として保留された方式。**測った需要は188 run中1件(0.53%)**。ユーザー原文§3(過去に不採用とした方式を無断で再導入しない)に当たるため、ここで明示して承認を求める。
3. **独立確認はローカルWhisper(faster-whisper small)。新規のProduction依存ではない。** 連結音同値層(2026-09-07承認)とKPの3票判定が同じ関数`_connected_speech_equivalence_local_asr_text`を本番で使用中。API費用0、E2が受理候補になったときだけ実行(47〜50秒segmentで約11秒、CPU)。

## 3. 設計(DESIGN_03.md。コード数十行+test)
- 判定ロジック=M1 moduleの隣接関数(凍結候補・audit・`aggregate_by_ledger_key`共有)。**呼出点=er109ブロック直後(1131〜1142行の直後)**。範囲は**既存の`ortho_scope.is_active_for_run()`のX/Z判定を再利用**(新しい範囲管理の仕組みは作らない)。Family A/B/Cは従来コードパス。
- **rollback flag**: er109と同形(module定数1つ・読取関数1つ・env/引数/設定dictから変更不可・既定の扱いはFable/ユーザー決定)。
- **Store再利用制限(OF-OOV-10、設計済み・実装0)**: E2W受理テイクは範囲外(A/B/C・flag False=rollback後)で再利用しない(`LEDGER_PHONEME_E2_AUDIO_OUT_OF_SCOPE`、er109の`OUT_OF_SCOPE_BLOCK_REASON`と同形)。該当Ledger entryが削除・無効化・更新(`updated_at`/`ipa_raw`変化)・confidence低下・出典消失したら再利用をブロック(`LEDGER_PHONEME_E2_LEDGER_ENTRY_CHANGED`)。auditに`ledger_key`を必ず残す。
- 既存のretry/fallback/3回上限/LR/HR Lock/Style Gate/Secondary 1回+cache/Primary#2廃止は不変。PASS→NG変化なし(受理を足すだけ)。

## 4. 受理条件(固定。TRIAL_03_RESULT_01 §1)
差分が正準1語→ASR1語のreplace 1件のみ(置換は揃えた位置の1か所)/正準語はCMU未収録でM1凍結候補のC2候補を持つ(OF-179:segment開始前登録、OF-181:sources非空・disabled無・canonical_spelling==surface)/Ledger confidence=medium以上/ASR語はCMU収録で代表発音(rank0)がLedger読みと完全一致・3音素以上/対象role=Tier3と同じ5 role/置換後判定=既存`classify_asr_match`のshould_pass かつ F1残差0、最終ANDゲート(値・否定)を元転写・置換後転写の両方に適用/**独立確認=ローカルWhisperが『揃えた位置の1語』で正準綴りまたは同じLedger読みのCMU語を書いた場合のみ(正の一致)。Whisperの失敗(None)・位置が確定しない・不一致は全て不受理(fail-closed)**/Azure転写が既に手元にある経路は矛盾時に不受理(OF-183)。

## 5. 実測(TRIAL_03_RESULT_01.md)
- 本run長segment(Adv part3): E2が受理した3 attemptすべてでE2Wも受理(3/3)。旧方式(文全体の一致判定)ではこの3件すべてが矛盾扱いで救済0になることを確認(位置1語判定で保持)。費用 実績38.58→16.38円(**-22.19円**)、確定時刻が約33分短縮(18:48:40→18:15:02)。
- 合成正例10: 救済が必要だった6件中E2Wが5件受理(X/Z voice=Charon・Erinomeを含む)。負例20(1音素違い): 正しい不受理14/既存判定のBASE_PASS(E2無関係)3/**誤受理3(skool→scold/spool、kewl→cull)**。
- 頻度: 188 run中1件(0.53%、X/Z系62 runなら1.6%)。期待効果 0.12〜0.35円/記事(70円目標の0.2〜0.5%)。**費用効果は小さい。主価値はD(確定の時間短縮)とHR Lock/人間承認の連鎖の回避(ユーザー手間)。**
- D-2'の拡張: Tier3調査由来の情報(M1に限定されていた自動PASSの根拠)を、E2Wで『同音語の受理』にも使うことになる(`cascade_unresolved_entity`はOF-180の範囲=ASR転写は調査入力に入らない、をコードとcontract testで確認済み、DESIGN_02 §5)。

## 6. 限界・リスク(必ず併記。Opus論点5)
1. **無効負例/誤受理の限界**: Primary・ローカルWhisper・Azure(第3エンジン)の3つがそろって同音語側に書いた音声は、ASRの証拠だけでは「正しい読み」か「近い別語を読んだのにASRが文脈で寄せた」かを判別できない。Phase 2の無効負例3件(loft/left/stool)と、今回の誤受理3件(scold/spool/cull)がその実例。
2. **Whisperは完全独立ではない**: PrimaryのOpenAIとWhisper系統が近く、事前知識による誤り方が似る。E2Wが防げるのは**エンジンごとに異なる単独の誤り**(Phase 2のkewl/coal #1)であり、**全エンジンに共通する事前知識による誤りは防げない**(今回の誤受理3件ではE2Wは何も防げなかった)。
3. この限界は辞書にある語の既存判定(例: 正準語coolで音声coalをPrimaryがcoolと書けば既存判定で通る)と同じ種類だが、**E2は受理を足すので、誤PASSにさらされる機会が増える**。
4. **各語の最初の発生は救えない**: Ledgerはreactive(ASRがNGを出した後、またはcascadeで調査して登録)。本runで効いたのは、A2 topic_introの大文字`Gacha`のcascadeが先にentryを作ったため。小文字のみ・後半segmentだけに現れる語は、同一run内の最初のsegmentが救えない。
5. 取りこぼし: low confidence(meink型)・同一語の複数回出現・差分が2語以上(本runのattempt 3,4,6,7)。
6. 別候補の読み(kewl型: Ledgerが有力とした/kjuːl/はおそらく誤りで、別候補/kuːl/経由の受理)の扱いは承認済み原則#52の変更になるため、採用後の集計項目(今は必須にしない)。
7. 正例・負例は合成で少数(正例10・実負例20)。

## 7. 安全網の選択肢(申請の選択肢に含める。Opus論点5)
- **E2W受理にWarningラベルを付け、事後試聴の対象にする**(`PASS_WITH_WARNING`+理由コード`E2_LEDGER_PHONEME_ACCEPT`、既存のW_*警告ラベルと同じ扱い)。
- **最初のN件(例: 採用後の最初の5件)を人が事後試聴**し、誤受理が見つかればflag False(rollback)。
- 採用後の集計: 別候補の読み経由受理件数(kewl型)、`aggregate_by_ledger_key`で同一Ledger entryの受理回数、事後試聴の結果。

## 8. ユーザー判断の選択肢(Opus論点7、DESIGN_02 §4を補正)
- **(A) X/Zに限定してE2Wを正式採用**(Yは配線時に再判定)。内容: 上記§2〜§4の設計/独立確認=ローカルWhisperで対象語の位置の一致を必須にし失敗時は不受理/D-2'の拡張/OF-184の再導入/訂正後のOF-OOV-05/rollback flag(er109と同形)/Store再利用制限(OF-OOV-10)/各語の最初の発生は救えない/実測した頻度(0.53%)と期待効果(-22.19円/件、期待0.12〜0.35円/記事)/§6の限界/§7の安全網。**長segmentで救済が保持された(3/3)ため、Opusの条件(長segmentで救済が残る場合に限りA)は満たした。**
- **(B) 現状維持＋telemetryで再検討のきっかけを決める**。きっかけの例: `E2_ACCEPTABLE_PAIRS`が増えた場合、gacha型(Ledger読みのある辞書外語×辞書の同音語)がtelemetryで複数runに出た場合。**HR連鎖を短絡する運用は(B)の中身に含めない**(HR/人間承認の変更はそれ自体がユーザー承認事項でE2Wより品質リスクが高い)。
- **(C)** Opusは「このままでよい」(DESIGN_02 §4の(C)の趣旨を維持)。
- Opusの推奨=条件付き(A)。Opusは11-7の既定OFF限定例外配線を勧めていない(効果ゼロのまま仕組みだけが増え、ONにする判断がもう一度必要になるため)。
- 判断候補の分類(PM_GOVERNANCE 27-3): D(真に新しい判断=新仕様の採用・OF-184方式の再導入・D-2'の拡張・承認済み判定フローへの層追加)。

## 9. 別件(本申請の範囲外・別管理ID候補)
ROOT_CAUSE_01で見つかった『Azureが全文単位で判定するため崩れやすい』問題(Primary非PASS 68行中31行がNG_BOTH。語ごとに見ればどちらかのエンジンが合っていた行が多い)。Azure削減の効果はE2Wよりずっと大きい可能性があり、別の管理IDとして検討する価値がある(Opus)。
