# RESULT_PACKET KPN5 委任_03(KP-GENERALIZATION-N5-PRODUCTION-WIRING-01、2026-10-30〜31、Fable向け)

## 1. 結論
J2を是正(Trial入力条件の再現)し、未観測項目の実runと是正後のruntime再証拠を取得した。費用**¥63.57/Cap¥70**。**PRODUCTION_WIREDとは呼ばない**(未観測=⑪人称書換の実例0件のみ。Fable受入待ち)。詳細=`docs/research/KP-GENERALIZATION-N5-PRODUCTION-WIRING-01/EVIDENCE_03.md`・`ev03/`。

## 2. J2是正(分類B)とTrial一致
- 再診断: 委任文の前提は部分的に不正確。Trial 19ケースの記録応答replay(API 0)で、包含dedupeに落ちたB1候補76件中26件は包含相手が**Trialでも**SEL非keepのP7(同一span23・厳密包含3)。④はTrialではP7候補そのもので、M10で落ちた直接原因は**Production側P7のspan境界差**(LLM非決定性)。
- 是正(Fable案(a)を厳密化): 異なるspanの包含相手がSEL非keepの場合のみB1候補をSEL再判定(`SEL_DEFERRED`)。単純案(同一span重複も再判定)はTrial 19ケース中14で再判定call発生=exact不可のため不採用。
- Trial L1選定が19ケースでexact一致(17=replay、2=実API再判定[¥0.096]が両方非keep)。④: 実API fixture(委任_02保存のP7/B1入力、¥2.49)で`set a lower limit→set a limit`保持。M10再replay(実API 3level ¥19.05): §4A①②③④⑤喪失なし、**既存Gate喪失0件(基準15%以下)**、N5 drop1(`make life work`、SEL=F、2/2回再現)。**untidi_b1bはCap見通しで未実施**(約¥7で追加可、判断はFable)。③は今回生成され`keep one's eyes on`(SAME)で正しく処理(fixtureで判定条件固定)。
- 留意: 実run10 L1中3件でdeferral発火(2件keepで候補追加)=Trialの19ケースでは0件。『Trial再現』の範囲内かは再確認推奨(限界=包含相手がSEL keepで後段QAに落ちた場合のsuperset非復活、観測0件)。

## 3. 未観測項目・runtime再証拠(正式runner CLIの複製run、本文/TTS再生成0)
- 技術失敗injection(X a2実run): GEN5を全attempt失敗→外側retry(outer_attempt 1→2)で回復、最終docのphrase候補5件全てN5記録あり(N5なし候補0)。
- Y b1b・Z a2の再選定round実run: NG句は復活せず、round1は`SUPERSEDED_1`退避。
- 人称書換(Z person_repair): 委任_02+03の全13 docで0件=**未観測**(作為的に発生させない)。
- 再証拠(X a2・Y a2/b1b・Z a2/b1b): actual model_id(luna/gemini-3.8-flash/gpt-6.1-sol)・Gemini model_version一致・Prompt sha/FLAGS hash/方式id一致・英日本文一致・gloss ALIGNED・除外計上を全件確認。他3level(X b1b等)はコード差分がL1(`er138`のみ)で影響限定。

## 4. 実測単価・費用
N5段/記事セット: Y ¥7.22(補完込み、なし¥6.11)・Z ¥4.01・X a2のみ¥3.21。委任_02と合わせた5サンプル平均**¥6.53**(Trial見積¥6.28比+4%)。再選定1 round(1 level)¥4.2〜4.3。費用内訳: J2検証¥2.58・M10再replay¥19.05・X ¥7.94・Y ¥18.90・Z ¥15.10。

## 5. 運用逸脱の記録
委任_02のM10枠超過¥1.80・起動間隔66秒違反・RESTART_STORM STOP後の別dir実施・自コード不具合の再生成¥5.3を記録(EVIDENCE_03 §7)。委任_03は起動11回で最小間隔150秒・300秒窓最大2回・違反ゼロ、既存STOP未接触。Y/Zのseed sha不一致STOPはAPI 0(worktreeのCRLF化)で原因特定後に各1回再起動。

## 6. 判断候補(停止根拠)
1. **受入基準⑪(Fable判断・ユーザー判断ではない見込み、分類B)**: 人称書換の実例は13 docで0件のためPRODUCTION_WIRED提案は不可。委任文『PRODUCTION_WIRED提案は全充足時のみ』と、ユーザー原文`delegation_log/2026-10-30_KP-GENERALIZATION-N5-PRODUCTION-WIRING-01_USER.md:120`『全6経路で必要条件が満たされた場合のみ』。⑪の実例要求の明文はユーザー原文に無く(12項目はDESIGN_01/委任文の受入基準)、mock test+0件観測で足りるかはFable判断。
2. untidi_b1b M10の追加実施(約¥7、Cap見通しで未実施)の要否=Fable判断(分類B)。

## 7. SSOT・Git
CURRENT_SPEC.md(N5節にJ2是正bullet・Status)、DECISION_LOG.md(DECISION-02と委任_03節)、OPEN_ITEMS.md OPEN-625(12項目・J2・M11)、ACTIVE_TASK。commit/push hash・raw URLは最終報告に記載。

## RESULT_PACKET必須4行
(1) 既存仕様整合: ユーザー原文`docs/pm/delegation_log/2026-10-30_KP-GENERALIZATION-N5-PRODUCTION-WIRING-01_USER.md:61-65,96,120`、`er138_kp_n5_generalization_01.py:1185-1210(collect_pool)・1245-1330(pool_and_select)`、`er119_kp_candidates_01.py:504,763`(配線無変更)、`er119_kp_backfill_01.py:23`(NOT_COUNTED_STAGES、n5_pool非計数を維持)、Trial `kpg04_methods.py ARMS['N5']`+fixture 19ケース(`TestJ2ProductionL1EqualsTrialOnRecordedCases`)。
(2) 未承認機能の既定値: 該当なし(N5はユーザー承認済みAPPROVED_FOR_PRODUCTION、flag/kill switchなし・既定ON。J2是正は同一承認範囲の入力条件再現で新flag無し)。確認=`er138_wiring_test_01.py TestDefaultOnAndOrder`とGrep(`EIGO_KP_N5`等のflagは存在しない)。
(3) 失敗終了時の最終成果物: N5技術失敗はN5なし候補を出さず外側retryで回復(実run: `ev03/x/kp_candidates_a2.json` outer_attempts=2・全phrase候補N5記録あり)、上限到達時はOUTER_RETRY_EXHAUSTED(候補0、mock test)。Y/ZのSTOP(seed sha不一致)は課金前でrun dirは変更なし。目的適合: 原文の『英語表現・日本語訳・本文根拠の整合』を壊す中途半端な候補は残していない。実際に残った成果物=複製run上のKP候補doc(Human Review PENDING、本番記事・音声の差替えなし)。
(4) 撤去・残置: 旧D/E1L/E4/N2のProduction参照は元々0(`grep -rln "kpg0[1-4]_" er119_*.py er125*.py`=0件)。残置: QA12(canon形判定、β′)・既存Gate・難易度4段階・`collect_pool`既定(defer_out=None=Trial同一)。追加した識別子: `SEL_DEFERRED`・`deferred_rejudged`・`blocked_by`・`TestJ2DeferredRejudge`・`TestJ2ProductionL1EqualsTrialOnRecordedCases`。撤去した規則・testなし。

判定整合: 重大NG=なし / 主因=[J2:ID無し] / 是正対象=[J2(完了)] / STOP理由=[なし] / 提示=証拠のみ
