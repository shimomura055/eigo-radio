FABLE-DELEGATION-MARKER: FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01-委任_07-OPUS-A-REFLECT-AND-MEANING-TRIAL-20261023

# FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01 委任_07: Opus条件Aレビュー(DESIGN_03)の反映 → DEV/Trial(er112基盤)でStd日本語意味・Adv英語説明の品質改善Trialを実行し、Fable評価用に結果を出す。Production変更0。到達上限=VALIDATED候補(採否はユーザー)。

## 0. 先に読むもの
`docs/pm/PM_BRIEF.md`、`docs/pm/ACTIVE_TASK.md`(固定ヘッダ、line 2 Git注意、line 21 KP行)、`.claude/agents/sonnet-worker.md`、`docs/pm/delegation_log/2026-10-23_FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01_USER_03.md`(ユーザー原文: §2要求品質、§3根本原因、§4改善・検証方針[検証項目1〜6]、§5配線)、`docs/research/FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01/{ROOT_CAUSE_02,DESIGN_03,OPUS_REVIEW_REQUEST_03,TRIAL_RESULT_01,A3_VERIFICATION_01,WIRING_DESIGN_01}.md`、`kp_probe_03*`、`er112_kp_gm_trial_01.py`/`er112_kp_gm_judge_01.py`(+eval/report/test)、`er019_family_x_kp_explanation_01.py`、`er003_key_words_gloss_alignment.py:300-330,575-612`、`er019_family_x_audio_production_runner_01.py:1077-1095`、`er026_family_z_fiction_production_runner_01.py:1517-1543`。

## 1. Fable判断(Opusレビュー照合済み)
Opus総合判定=「必須修正を入れればTrialに進んでよい」。Fableは、Claude案(案A+案B、案S不採用、B仕様変更はVALIDATED後ユーザー判断、Judge修正先決、段階gate)とOpusが方向で一致し、対立点はいずれもTrial設計の精度に関するもの(新仕様・Product原則・承認済み内容の変更なし、費用は7-7範囲内)と判断し、**Opus必須修正OF-KPGM-D3-01〜06を全て反映し、推奨07〜12も原則採用**してTrialへ進める。E4を推奨の核にせず、要因分解でE1型を第一候補として比較する。

## 2. Opusレビュー(逐語保存すること → `OPUS_REVIEW_03.md`)
以下をそのまま保存(見出し「Opus独立技術レビュー(条件A) DESIGN_03 2026-10-23」付き):
---
総合判定: 必須修正を入れればTrialに進んでよい。方向性(一方向の伝染を断つ・案Sは不採用・B仕様の変更はVALIDATED後にユーザーへ諮る・Judge基準の修正を先に行う・段階gate)は支持する。ただし推奨の核であるE4の読み方、評価指標の定義、cacheの無効化、Std側の結論の強さに、結論を左右する欠陥がある。

[必須] OF-KPGM-D3-01 E4は2つの変更を同時に入れており、悪化はgloss除去ではなく「用法先決め」の段から来ている。根拠: kp_probe_03_report_out.txt。E1(glossを外すだけ)は sense 28/28・core 26/28 でE0と同値。E4は sense 25・core 22。KP別にE4だけで失敗: wallet(E1 111/111→E4 011/011)、pull someone under、refueling support(101/101)、apply one's findings、draw a lineのcore。E4がE1に勝つのはsingleだけ。G2(差し引き0)、E3(最悪)と合わせ「lunaに字義/比喩を明示的に分類させると誤りが固定される」仕組みが3回出ている。reasoning modelは出力前に内部で考えるため、schema順で考えさせる利得は小さく、決めた内容に縛られる害が残る。修正: Adv armを要因ごとに分ける: E0 / E1 / E1+core_sense(usage_typeなし) / E4。第一候補は最も簡潔なE1型(入力行とそれを参照する規則行を消すだけ)。E4は修正後Judgeで明確に上回った場合だけ採る。
[必須] OF-KPGM-D3-02 single指標がユーザー目標例と食い違う。er112_kp_gm_judge_01.py:54「AまたはBの併記=0」だが、目標例 "to establish a clear boundary or limit" も "or" を含む。E1/E4差(single 21→28)はこの指標依存。修正:「異なる2つの語義・用法を並べた場合だけ0。同じ1つの語義を同義語で補った場合は1」と定義し直し、probe-03既存行を再判定してキャリブレーション。
[必須] OF-KPGM-D3-03 E0基準値は改善後Std glossと組み合わせて測る。probe-03のE0はG0 gloss(「線を引く」)入力で111/111だったが、Stdが「一線を引く」になるとE0はacceptable型3/4(03b)。修正: Std armとAdv armを交差。E0は各G arm(特に採用候補G)の出力を入力に測る。E1/E4はgloss非依存なので1回。
[必須] OF-KPGM-D3-04 signatureからglossを外すとXでは旧仕様の説明がそのまま再利用される(X/Zで挙動が違う)。runner:1084-1088 phrases_signature一致でgloss条件を外せば旧Prompt説明がreuse。Zは er026:1517-1528 でsig_payload形が変わりハッシュ変化→再生成。どちらもPROMPT_SHA256・仕様versionがsignatureに無い(auditにはある er019...:360)。修正: X bundleとZ sig_payload両方に説明仕様ID/PROMPT_SHA256を入れる。既存完成記事を次回runで再生成する扱いを明記。
[必須] OF-KPGM-D3-05 撤去対象の漏れ: er019_family_x_kp_explanation_01.py:79-80 "Do not just translate the Japanese reference meaning…"(外す入力を参照)、:165-167 docstring、呼び出し側 runner:1089-1091・er026:1534-1535(japanese_gloss)、schema名 `..._trial_02`。er041(Trial-02履歴module)は編集しない。逐語一致testは「Trial-02と一致」を撤去し新仕様IDのhash固定へ置換。
[必須] OF-KPGM-D3-06 Std gate「draw a line 3/3」だがSol armは8unit×1repで1サンプルしか取れない。§6-7費用「2arm×8unit×約2円=約32円→8unitに限定して約16円」は矛盾(2armなら約32円)。Sol単価はluna 688token流用でeffort highの実測なし。修正: draw a line単体は各Sol armで3rep。難例バッチはSol arm 1本に絞るかunit数削減。Sol費用は1 call実測で再見積もりしてから進める。
[推奨] OF-KPGM-D3-07 「modelの判断力が律速」はまだ仮説。試したのはlunaのみ、Prompt変更も再整合用枠組み内の2案のみ。現Promptは既存glossの全語反映判定用(er003:580-604)、新規生成文(:315-321)も「過不足なく一致」「source_sentenceは語義選択のみ」で語単位対応へ誘導。G2は「英語中心義の言い換え」方向で「区別する」に流れた。未試行手段: 新規生成(current=null)項目だけを対象に「英和辞典の定訳や対応する日本語慣用句があればそれを、無ければ中心義を平易に言い換える」という目標種類の変更、同一call内で2〜3案を出して自己選択。修正: lunaのG3 armを1本追加(約3円)、G3-solは条件付き。few-shotにdraw a lineを入れるのは個別対策で禁止。
[推奨] OF-KPGM-D3-08 因果主張を証拠の強さに合わせる。draw a line単体は強い(3/4対0/16、Fisher片側p≈0.004)、Carry the Load(2/4対0/8)は弱い。層別はKP難度が共通原因。probe-03ではgloss除去で全体coreは改善せず(E1=E0=26/28)。確実に言えるのは「glossは含意を持ち込みうる。特に目標Std(一線を引く)はE0を悪化させる」まで(除去理由として十分)。補足: 英語 "draw the line (at)" には「許容の限界」という正規語義があり、「一線を引く」がその語義を呼ぶ面がある。
[推奨] OF-KPGM-D3-09 Std/Adv整合は「同じ用法(字義/比喩)で矛盾しない」と定義。条件付き再整合を最初から入れるのは過剰設計。Trialで矛盾件数を測り、難例で1件以上出たときだけ検討。
[推奨] OF-KPGM-D3-10 Judge: core修正案(表現の定義に含まれる語は数えず、記事の対象・目的・場面・評価条件だけを混入)は妥当。加えて: 生成前に難例20件の正解ラベル(用法と許容語義範囲)をFableが固定(Carry the Loadのように正解が曖昧な例があるため)。2系統Judgeを正解ラベルに対し校正しkappa報告。Fable目視=ランダム20%+不一致行全件。Judge再判定一致(約30行)を事前に1回測る。armは伏せて判定。Sol Judgeで系統相関の偏りを補う構成は妥当。Stdの「区別をはっきりさせる」は要求文言は満たすが「一線を引く級」かは不明→単独質問にせずVALIDATED報告に代表例を並べる。「線を引く/境界線を引く」はNG確定。
[推奨] OF-KPGM-D3-11 統計: 同armの再生成で判定が揺れるKPが25〜50%あり、基準5(非劣化95%)・基準4(100%)はE0自身が満たせない可能性。修正: 非劣化はE0とE0再生成の自己一致率を基準、許容差を事前宣言。KP単位対比較で改善/悪化/不変flip件数(McNemar型)。「5%以下」はWilson信頼区間添付。全て方向判断。75KP×3rep(約225行)で足りる。
[推奨] OF-KPGM-D3-12 ユーザー検証項目6はVALIDATED前に満たす。DEV注入(Zは er026:1537 `expl_call_fn` hook、Xも同様)でX 1本+Z 1本のtext工程E2E(TTSなし、約6〜10円)をVALIDATED前に実施、retry発動統計も取る。Production moduleのhashが開始時と終了時で同一であることを記録。
[情報] OF-KPGM-D3-13 Structured Outputsはschema property順で出力。生出力でkey位置を記録し決定論的に検査すればよい。現行は english_explanation 以外読まれない(er019...:311)ので下流不変。
[情報] OF-KPGM-D3-14 E3悪化は「1回決めた判断の固定」+lunaの判断精度不足。E3-solはSol glossが難例で用法をほぼ正しく判定した場合だけ実施(条件付き、約8円節約)。canonicalization callで意味を運ぶ案は波及大の割にE3と同じ仕組み、再検討価値低。
[情報] OF-KPGM-D3-15 Sol +約1.9円/セット(+2.7%)は妥当規模だが実測前提。25節どおり評価model/本番modelは別判断。費用低減候補: Sol armでglossの入力から記事全文を外す、Solを多語動詞句に限る(決定論振り分け)。採否比較表に載せる。慣用句辞書は費用対効果不明、G3とSolが共に効かない場合の進言候補。
一致: 主因=一方向の伝染/案S不採用/新規LLM call 0/B仕様変更はVALIDATED後ユーザー/Judge修正先決/段階gate/Production model別判断。対立: 核はE1型の要因分解(01)/single定義(02)/E0交差(03)/仕様versionをsignatureへ(04)/G3並列(07)/自己一致率基準(11)/項目6をVALIDATED前(12)。費用は修正後も60円前後。
---

## 3. 作業
### T-0 記録(API 0)
- 委任文逐語保存: `.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-23_FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01_委任_07.md`(先頭MARKER一致を確認)。
- `ACTIVE_TASK.md` line 21(KP行)のみ更新: 委任_07 Status=`MEANING_TRIAL_IN_PROGRESS`、上限70円(目標60円)、報告=`docs/pm/RESULT_PACKET_KPGM7.md`。
- **予算**: 当日累計を `daily_dev_cost_01` で確認。当日上限は**1,400円**(ユーザー2026-10-23改定)。他案件の予約枠(Family Y 残334.25円、ASR②/B工程 ≤25円)を差し引いても本Trial上限70円が収まることを確認して記録。収まらなければSTOPしFableへ。費用は raw_usage_log 出典で段階ごとに `TRIAL_02/BUDGET_LOG_01.md` へ記録し、**累計55円到達時点で完成見込みを再計算、70円超過見込みなら停止前にFableへ報告**。
### T-1 設計改訂(API 0) → `DESIGN_04.md`
OF-01〜12を反映した改訂設計: arm構成(下記)、Judge定義修正(single/core)、正解ラベル手順、統計設計(自己一致率基準・McNemar flip・Wilson CI・方向判断・事前宣言の許容差)、Std/Adv整合の定義(用法一致・矛盾なし、矛盾件数を計測)、費用表(Sol 1 call実測後に確定)、X/Z配線差分(OF-04/05: signatureへ仕様ID/PROMPT_SHA256追加[X bundle・Z sig_payload]、撤去一覧、既存完成記事の再生成扱い、逐語一致testの置換方針)→ `WIRING_DESIGN_02.md`(設計のみ。Production編集は行わない)。
### T-2 Judge改修・校正(API小)
- `er112_kp_gm_judge_01.py`: single再定義(異なる語義併記のみ0)、core基準修正(表現の定義語は数えず、記事の対象・目的・場面・評価条件のみ混入)。probe-03既存行で再判定しキャリブレーション結果を記録。
- **難例20件の正解ラベル案**: 難例(過去Trial/probeで不合格が出たKP+慣用句・句動詞を中心に20件)について、用法(字義/比喩)と許容される中心義の範囲(日本語・英語)を`TRIAL_02/GOLD_LABELS_DRAFT_01.md`に案として作る(各KPに代替解釈も併記)。**Fableが確定する**ため、確定前はdraftとして扱い、Judge校正は draft で先行、Fable確定後に差分があれば再判定(再判定費用は小さいので見込みに含める)。
- 2系統Judge(現行Sonnet系+Sol)を正解ラベルで校正、kappa、再判定一致(約30行)を事前計測。arm名は伏せる。
### T-3 Trial実行(DEV er112のみ、Production変更0)
- KP集合: ≥75 KP(既存Trialデータ再利用優先。慣用句・句動詞・多語動詞句・通常KPの構成比を記録)。
- Adv arm: E0(G0出力入力)/E0(採用候補G出力入力、交差)/E1/E1+core_sense/E4。E1/E4系は1回でよいが、自己一致率測定のためE0とE1は難例20件で3rep。
- Std arm: G0/G2/G3(luna、新規生成項目のみ対象: 定訳・対応する日本語慣用句優先、無ければ中心義を平易に、同一call内2〜3案自己選択。draw a line few-shot禁止)/G0-sol/G2-sol(**Sol 1 call実測→再見積→Fableへ報告不要で実行、ただしSol合計≤25円**)/G3-sol・E3-sol(条件付き: Sol glossが難例で用法をほぼ正しく判定した場合のみ)。draw a line単体は各Sol armで3rep。
- Std/Adv矛盾件数(用法不一致)を全組合せで計測。
- 全てのarm出力・Judge生出力・費用を `er112_output/kp_gm_trial_02/` に保存、Fable目視用 `fable_sampling_list_02.md`(ランダム20%+Judge不一致全件、arm伏せ+keyファイル分離)。
### T-4 検証項目6(VALIDATED前): DEV注入E2E
- 第一候補arm(E1型+採用候補G)を、X 1本+Z 1本のtext工程(TTSなし)でDEV注入(Zは `expl_call_fn` hook、Xは同等の注入点。Production fileに注入コードを残さない)により実行(約6〜10円)。retry発動統計、語数/新規Fact fallbackの挙動、出力をFableへ。開始時/終了時のProduction module(er019_family_x_kp_explanation_01.py、er003_key_words_gloss_alignment.py、両runner)のsha256一致を記録。
### T-5 結果・SSOT・Git
- `TRIAL_RESULT_02.md`: ユーザー検証項目1〜6との対応表、代表例(draw a line Std/Adv、他の慣用句・句動詞≥10件の実績表)、arm比較(方向判断+CI+flip)、Std/Adv矛盾件数、Sol費用実測と70円目標への影響(+x円/セット、低減候補の比較表 OF-15)、残リスク、自己判定(VALIDATED候補/未達/USER_DECISION_REQUIRED候補)と理由。**手段の成否と目的(要求品質到達)の達成を分けて記す**(Closeout項目32)。
- OPEN-474追記。`CURRENT_SPEC.md`/Production code変更0。
- Git: `secret_scan --staged` hits=0 → `git diff --cached --name-status` → `git commit --only -- <path…>` → `git push origin HEAD:main`。raw URL添付。
- 報告=`docs/pm/RESULT_PACKET_KPGM7.md`(使用model名・最新か明記)。

## 4. 禁止・制約
Production code/Prompt/flag/閾値/golden変更0(er112と docs のみ)。`git add -A/-u/-f`、amend、rebase、force push、stash、clean、reset --hard、checkout -f 禁止。一時index禁止。pythonプロセスは自分が起動したPIDのみ終了可(26-6)。有料runの再起動は本委任範囲内(Trial arm実行はそれ自体が実行許可)。秘密情報出力禁止。個別対策(特定KPのfew-shot/辞書登録)禁止。上限70円を無断超過しない。
## 5. handback条件
完了/予算警告(55円到達かつ超過見込み)/blocker/USER_DECISION_REQUIRED候補(例: 要求品質に届くarmがなく方針転換[慣用句辞書等]の進言が必要)。途中経過は小刻みに返さない。