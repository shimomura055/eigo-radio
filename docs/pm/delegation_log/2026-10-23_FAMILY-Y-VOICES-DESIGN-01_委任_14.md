FABLE-DELEGATION-MARKER: FAMILY-Y-VOICES-DESIGN-01-委任_14-PHASE-B-SIX-STAGE-PIPELINE-TRIAL-20261023

# FAMILY-Y-VOICES-DESIGN-01 委任_14(Phase B): Opus条件Aレビュー(OPUS_REVIEW_03、DESIGN_PROPOSAL_05)の必須修正を反映→新DEV module(6段階Persona選定〜R0パイプライン)実装→2題材(school_phone_ban、office_seating[固定席/フリーアドレス])+再現runを実行→Fable/Opus盲検用資料→報告。DEV/Trial経路のみ、X/Z Production変更0、既存er110無変更、未承認配線なし。**費用上限180円**(Family Y累計上限600円の内。現在約330.3円→最大約510円。音声化は本委任に含めない)。

## 0. 先に読むもの
`docs/pm/PM_BRIEF.md`、`docs/pm/ACTIVE_TASK.md`(line 2、Family Y行[26行目付近])、`.claude/agents/sonnet-worker.md`、`docs/pm/delegation_log/2026-10-23_FAMILY-Y-VOICES-DESIGN-01_{USER_05,委任_13}.md`、`docs/research/FAMILY-Y-VOICES-DESIGN-01/REDESIGN_02/{ROOT_CAUSE_02,DESIGN_PROPOSAL_05,OPUS_REVIEW_REQUEST_03}.md`、`REDESIGN_01/{OPUS_REVIEW_02,SPEC_MAPPING_01,INVENTORY_OLD_B_VOICES_01}.md`、`TRIAL_03/{WORLD_SETTING_01,TRIAL_03_RESULT_03}.md`、`er110_family_y_persona_text_trial_01.py`(現行Prompt・Leakage判定器・Acceptance Gate呼出)、`er110_output/family_y_persona_trial_01/school_phone_ban/it3/`(旧稿)、旧稿(オフィス席): `er012_output/editorial_b_voices_trial_06/`(research ledger・旧2V本文)。

## 1. Fable判断(Opus照合済み)
Opus総合判定=「必須修正後にPhase B可、再設計不要」。方向(探索と選定の分離・世界設定先行・S3に台帳Fact非入力・Voice Prompt指定の撤去・手作業禁止・点数ゲートなし・DEV分離・題材(b))はClaude案と一致。対立点は評価・再現性・安全網の精度でありTrial設計の範囲。**必須OF-Y5-01〜06を全反映、推奨07〜12も採用**する。費用: OF-04(再現runをS6まで)を入れ、sol補助盲検は外す。上限はFable裁量で**180円**(USER_05 §7のY予算600円内。音声化分は後日、必要なら前広に報告)。

## 2. Opusレビュー(逐語で `REDESIGN_02/OPUS_REVIEW_03.md` に保存。見出し「Opus独立技術レビュー(条件A) DESIGN_PROPOSAL_05 2026-10-23」)
---
総合: 必須修正を行えばPhase B可、再設計不要。6段階の骨格に同意(探索と選定の分離/世界設定先行/台帳FactをS3に入れない/Voice Prompt指定撤去/手作業差替え禁止)。ROOT_CAUSE_02の結論(選定が手作業・制作都合)も妥当。弱点3: 評価・再現性設計(再現runがS4止まり、判定者の校正なし)/固定TTS Voiceとの不整合/指定撤去後の安全網(構造監視が実際の同型化を検知できない)。
[必須]OF-Y5-01 固定TTS Voiceの性別(V1男・V2女・V3男、er110:181)と自由なPersona選定が衝突(女性2〜3人のtrioが割当不能)。修正: S4では性別を選定基準にしない。S4各メンバーに `gender_intrinsic`(立場上性別が決まるか)を出力。S5前に決定論でスロット割当(性別確定の人物を先に置き、残りに空きスロットの性別をS5で付与)。成立しない場合は手作業で直さず記録・報告(声セット変更はユーザー判断)。一人称・年齢帯の3人重複も決定論で確認。
[必須]OF-Y5-02 評価が日本語本文のみで英語音声版を見ていない(前回OF-Y3-01「人物差は英訳とStd簡易化で消える」)。規則4撤去で複数の本音が混ざると、Std簡易化で芯が落ちる危険。修正: 各題材メインrunでStd英語版にもA'/B'盲検、主張抽出(E1)は英語Stdで記録(英訳含め数円)。
[必須]OF-Y5-03 判定者の校正と割れた時の規則がない。修正: 盲検セットに目印として旧V1(ユーザー評価=良)と旧V2・V3(=弱い)を混ぜ、再現できない判定者の結果は主評価に使わない。割れたら低い方を採り、引用付きでFable裁定。主要当事者リストを題材ごとに**実行前にFableが固定**し、P3「primary_parties網羅」は事前リストの網羅で判定(LLM出力同士の完全一致は要求過大)。
[必須]OF-Y5-04 再現runがS4で止まると再現性が測れない(旧V2・V3も選定理由だけならもっともらしかった、破綻はVoice本文で出た)。修正: 少なくともschool_phone_banは再現runをS2〜S6まで通す(約+30円)。相殺: sol補助盲検(約8〜10円)を外す。150円超なら事前承認(→Fable: 上限180円に設定済み)。
[必須]OF-Y5-05 S6の撤去範囲が広すぎる。修正: S5で `identity_cue` を生成しS6は規則3(冒頭2文以内の身元手がかり)を残す(位置指定は緩めてよい)。規則4は「締めで核に戻る」「核は1つだけ」を撤去するが「聞き終えた人がこの人は何を言いたいか一言で言える」を目標として1行残す(位置・型指定なし)。規則9〜13(一般化禁止、数字・実在名禁止等)は残置と明記。
[必須]OF-Y5-06 構造監視の発火条件(冒頭・締め・展開の3つ全一致)では旧V1/V3型(展開同一・締めのみ違う)を検知できない。修正: 「展開の型が一致 かつ 冒頭型か締め型のどちらかが一致」で発火。締め型の違いだけでは「異なる」とみなさない。タグのラベル集合を事前固定し「自嘲・告白で締める」を含める。
[推奨]OF-Y5-07 自然さ自己検証は同一callだとほぼ常にnatural→別call(luna)で「最も不自然な点を必ず1つ挙げ、聞き手に違和感を与えるか」、因果説明は見せない。差戻し発火回数を記録(0回なら「機能した」と結論しない)。
[推奨]OF-Y5-08 V1量産型への収束リスク: S5で痛み・失敗・矛盾を全員必須にすると自嘲告白型に収束。矛盾・弱さは属性として持たせ、語りに出すことは必須にしない。S4 `diversity_note_ja` に「感情・矛盾の出方が3人で同型でないか」を追加。
[推奨]OF-Y5-09 S1を学校題材でもLLMで1 call実行(約4〜5円)し、承認済みWORLD_SETTING_01を正解として照合(外国Fact分離の検証)。以降は承認済み設定を使い旧稿比較条件を保つ。
[推奨]OF-Y5-10 制度誤説明対策: `factual_risk`は自己申告で見落とし前提。S6入力に `world_frame.distinctions`(使用禁止/取り上げ等の区別)を加える。事後盲検に「制度の取り違え(引用付き)」を記録(Gateにしない)。許容する事実1件は status_quo IDから選ぶ `known_fact` 欄としてS5に定義。
[推奨]OF-Y5-11 高校生本人: S2/S4で除外しない。S5で18〜19歳へ寄せる誘導もしない。旧V3は成人声の制約から逆算された人物(SPEC_MAPPING_01:26)=ROOT_CAUSE_02へ追記。18歳未満が選ばれたらUJ-3として記録、R0通過後の試聴でユーザー判断。
[推奨]OF-Y5-12 量産費用: +25〜35円/記事はTrialではQ>D>Cの範囲内、70円目標とのトレードオフはVALIDATED提案時にユーザー判断事項として明示。Phase B後の削減候補: S2+S3統合、S5 effort medium比較、S4候補trioを2組に。S5の3人1 call化は独立性の観点で後回し。
[情報]OF-Y5-13 旧V3の交渉型締めは前回OF-Y3-09(締め型を人物別指定)の副作用、撤去に同意。 OF-Y5-14 量産段階では差戻し上限超過時の最終処理(人間レビュー行き等)の定義が必要(Phase Bでは不要)。 OF-Y5-15 学校題材で親・生徒・教師に収束しても失敗ではない。評価はA/B/C、新しさでは評価しない。 OF-Y5-16 別題材は(b)オフィスの席でよい。
P1〜P10判定とClaude案との一致/対立は原文どおり(一致: 原因特定・6段階・台帳Fact非入力・点数ゲートなし・手作業禁止・DEV分離・題材(b)。対立: 再現runS4止まり→S6まで、日本語のみ評価→英語も、構造監視条件、identity_cue残置、S5必須項目の緩和、固定Voice性別の決定論割当)。
---

## 3. Fable事前固定: 主要当事者リスト(OF-Y5-03。各runのS2がこれを網羅しているかで判定。S2はこれ以外も自由に探索してよい)
- school_phone_ban(日本の高校、持込可・休み時間含む校内使用禁止にするか): 高校生本人(全日制)/高校生本人(定時制・働きながら)/保護者(父または母)/担任教師/生徒指導担当/養護教諭またはスクールカウンセラー/管理職(校長・教頭)/定時制生徒のアルバイト先の雇用主/PTA・保護者会。
- office_seating(固定席かフリーアドレスか、日本の会社員): 集中作業が多い一般社員/対面の雑談・相談を重視する一般社員/チームを預かる管理職/総務・ファシリティ担当(コスト・座席率)/新入社員・若手(居場所・相談相手)/時短勤務・育児中の社員/外回りが多い営業/経営層(オフィス費用・方針)。

## 4. 作業
### T-0 記録・予算
- 委任文逐語保存 `..._委任_14.md`(`py docs/pm/tools/extract_delegation_from_jsonl_01.py ...`、MARKER一致)。ACTIVE_TASK Family Y行: 委任_14 Status=`PHASE_B_PIPELINE_TRIAL_IN_PROGRESS`、上限180円、報告=`docs/pm/RESULT_PACKET_FYT10.md`。
- `REDESIGN_02/BUDGET_PLAN_PHASE_B_01.md`: 段別見積(S1〜S6×2題材+再現run S2〜S6[school]+英訳Std/Adv+判定補助)、当日累計(`daily_dev_cost_01`、JST日付に注意: 10-24以降は上限1,000円)、チェックポイント(累計90円/140円で見込み再計算、180円超過見込みなら停止前にFableへ)。
### T-1 設計反映(API 0)→`REDESIGN_02/DESIGN_PROPOSAL_06.md`
OF-01〜12を反映(スロット割当の決定論、identity_cue、規則残置/撤去の一覧、構造監視の発火条件とタグ集合、自己検証別call、S5必須項目の緩和、world_frame.distinctions、known_fact、S1 LLM実行と照合、校正用センチネル[旧V1/V2/V3]を含む盲検設計、判定割れ時の規則、主要当事者リストの網羅判定、再現run範囲、費用)。ROOT_CAUSE_02へOF-11追記。
### T-2 実装(DEV)
`er110_family_y_persona_pipeline_01.py`(+`_run_01.py`+`_test_01.py`): S1〜S6をStructured Outputで実装、決定論部分(スロット割当、重複確認、構造タグ監視、主要当事者網羅チェック)、既存Leakage判定器・Acceptance Gate・Repetition前提(R0のみ、4パート構成)を呼出で再利用(既存er110 module無変更)。Production fileから参照されないことをtest(isolation/allowlist)で固定。使用model: 生成=現行Y Trialと同系(記録)、自己検証=luna、評価補助は使わない(主評価はOpus/Fable盲検)。
### T-3 実行(≤180円)
1. school_phone_ban: S1 LLM 1 call→WORLD_SETTING_01と照合(差分記録)→以降は承認済み設定で S2→S3→S4→(スロット割当)→S5(+別call自己検証、差戻し≤2)→S6 R0(日本語→Std/Adv英訳、既存Y経路)。
2. office_seating: S1(LLM、既存Ledger `editorial_b_voices_trial_06` 利用、新規Research 0)→S2〜S6(同上)。
3. 再現run: school_phone_ban の S2〜S6 を独立にもう1回(同一S1入力)。
4. 各runで記録: S2立場一覧(主要当事者リスト網羅○×)、S3立場×主張表、S4 trio候補3組と選定理由(A/B/C+最大の反論)、スロット割当結果、S5 Personaシート+自己検証結果+差戻し回数、S6 R0(日本語/Std/Adv)、構造タグと監視発火、Leakage/Acceptance結果、制度取り違えの自己点検、費用・時間・call数。
### T-4 盲検資料(Opus/Fable主評価用。arm・run伏せ)
`REDESIGN_02/BLIND_SET_03.md`+`BLIND_KEY_03.json`: 題材ごとに、新run(メイン)・新run(再現)・旧稿(school: it3 V1/V2/V3、office: 旧2V)のVoice本文(日本語、およびStd英語)をラベルなしで混在。校正センチネル=旧V1(良)/旧V2・V3(弱い)。設問=A当事者性/B主張の必然性(各Voice、3段階+引用)、C 3 Voice組合せ価値(trio単位)、制度の取り違え(引用)、同型化の有無、Q「実在の人が自分の生活から語っているか」。
### T-5 報告・SSOT・Git
`REDESIGN_02/PHASE_B_RESULT_01.md`(ユーザー§8の1〜8に対応: 根本原因/新旧差分/候補立場・主張と3人選定理由/完成Personaと主張/旧稿比較[盲検は空欄=Fable記入]/別題材結果/量産手順・費用・時間への影響[実測call数・円]/残課題・Status[自己判定はVALIDATED候補にしない。再現性の判断はFable]・必要判断[声セット、18歳未満UJ-3、70円目標とのトレードオフ等])。OPEN-463追記。DECISION_LOG(Fable判断: Opus反映・上限180円)。secret scan 0件→`git diff --cached --name-status`→`git commit --only -- <path…>`→`git push origin HEAD:main`。報告=`docs/pm/RESULT_PACKET_FYT10.md`(使用model名・最新か)。

## 5. 禁止
V2・V3等の手作業修正、特定3人・5候補の固定、few-shotでの人物例示、音声生成(TTS)、R1/R2追加、X/Z Production変更、既存er110 module変更。`git add -A/-u/-f`・amend・rebase・force push・stash・clean・reset --hard・checkout -f・一時index禁止。PIDは自分のもののみ。上限180円無断超過禁止(並列発行時は発行前累計+見込みでcap検査)。秘密情報出力禁止。
## 6. handback
完了/予算警告/差戻し上限超過(工程原因の報告付き)/スロット割当不成立/blocker のいずれかで。途中経過は小刻みに返さない。