# OPUS_REVIEW_REQUEST_01(条件A: 新しい処理フローのProduction導入 — Family Y正式Production runner)

管理ID: FAMILY-Y-PRODUCTION-LAUNCH-01 委任_01 / 日付: 2026-10-25 / 依頼元: Sonnet(実行層)→Fable経由でOpus独立レビュー
レビュー対象(いずれも読み取り): `DESIGN_01.md`、`EXISTING_SPEC_CHECK_01.md`、`PROMPT_GATE_ALIGNMENT_01.md`、`SPEC_LEDGER_01.md`/`spec_ledger_01.json`、`BUDGET_PLAN_01.md`(同dir)、DEV資産 `er110_family_y_closing_general_trial_01.py`/`er110_family_y_audio_trial_01.py`/`er110_family_y_redelivery_revision_01.py`/`er110_family_y_persona_text_trial_01.py`、X/Z基盤 `er019_family_x_audio_production_runner_01.py`/`er026_family_z_fiction_production_runner_01.py`。
前提(レビュー対象外=変更しない): ユーザー正式決定(`docs/pm/delegation_log/2026-10-25_FAMILY-Y-PRODUCTION-LAUNCH-01_USER.md`): Y構成、Closing一般化Prompt 02(sha4713ceff…)+gpt-6.1-sol high、『宅配の再配達』のみ案B、Prompt 02・Gate基準の独断変更禁止。Prompt/Gate変更案(PROMPT_GATE_ALIGNMENT_01 §6)の採否はユーザー判断でありレビュー対象外(ただし変更案の記述の妥当性は意見可)。
状態: **設計のみ(未実装・API 0)**。レビュー目的=実装前に構造の欠陥を潰す。判定は「実装へ進んでよい/修正後/不可」と必須修正(M)・推奨(R)で。

(Opus独立レビュー観点12項目、`docs/pm/templates/OPUS_INDEPENDENT_REVIEW_BLOCK.md`の固定ブロックをFableが貼付する。以下は設計固有の重点観点。)

## O-1 新規runner(b案)か既存拡張か、DEV昇格(c案)の不採用は妥当か
主張: X runner拡張は競合・X/Zリスクが大きく、DEV昇格は`patched_*`・alias ID・DEV予算skipを持ち込むため、Zがerr026でしたのと同様に**新規runner+X共通部品import**とする。
観点: ①より単純な構造(例: Zのstage frameworkを薄くラップするだけ)がないか ②新規moduleが肥大化していないか(DEV約5,100行のうち移植が必要な範囲の見極め)③`er019`の部品import経路(例: `xr.asm`/`xr.p9a`/`xr.style_profile_mod`)が並行agentの編集で壊れる耐性 ④Y runnerがXのどのprivate関数(`_generate_or_reuse`等)に依存するか(依存が深いほど脆い)。

## O-2 Closing一般化の移植忠実性とGate運用
主張: Prompt/入力構造/schema/選定処理/決定論検査は逐語移植。Gate運用は既存`run_gate`(判定≤3・局所書換え・`LEAKAGE_RESIDUAL_STOP`)を使い、局所書換えpromptに選定済み切り口を付加する(委任_28の先例)。FAILの自動全文再生成はしない。
観点: ①局所書換えがClosingの切り口を損なわない設計か(選定済みnew_view付加で足りるか。書換えが3人の語りとの整合を壊さないか) ②Trialは判定1回・書換えなしで測定した=ProductionのGate運用との差が測定値(FAIL率25%等)の解釈を狂わせないか ③期待追加費用の見積(約0.5〜1.4円/記事)の妥当性 ④失敗時の最終成果物(未公開JA稿+FAIL記録)が安全側か。

## O-3 案B固定注入(例外の監査可能性)
主張: コード定数registry(slug・sha・承認ref)+一般化の決定論検査は適用せずGateのみ1判定+局所書換え禁止+FAILはSTOP。
観点: ①固定注入が『Gate再試行で通す抜け道』や『他記事への流用』になり得ないか ②案Bが一般化規則(問い1つ等)と異なる点をどう扱うか(承認本文を直さない設計の妥当性)③FAIL時STOPが『最終成果物が目的要件を満たす側』か(観点11): 宅配が公開できなくなるリスクと、承認本文を書き換えるリスクのどちらを取るか ④受入条件3(Prompt 02実使用)を別記事(SNS)のruntime evidenceで満たす設計で足りるか。

## O-4 Y segment IDとQA対象の網羅(T8)
主張: DEVのalias(`full_story_part3_c2/c3`)を廃止し、Y専用ID(`y_lead`/`y_intro_n`/`y_voice_n`/`y_closing`)を`resolve_narrative_role`ほか共有QAに追加する。
観点: ①共有fileへの追加が`er020`のimport時自己検査・既存IDに副作用を出さないか ②Connected Speech/Local Rewrite/Repetition/disfluency/`--only-segments`/Audio Validation Gate/telemetry/Master store keyのうち、ID追加漏れが起き得る箇所の網羅(grep対象リスト)③ID命名(意味衝突回避)の代替案。

## O-5 共有file編集(routing・scope・page・検査tool)の最小性と他Family不変
主張: 編集は列挙した5群のみ。A/B/Cは従来経路でバイト一致、X/Zは出力不変。
観点: ①`APPROVED_SCOPES`への`"Y"`追加は承認原文(X/Z)との関係で適切か(28-1運用7を根拠とする開示事項として足りるか、ユーザー確認が要るか) ②routing key新設の粒度(5 key)は過剰か(既存`SUPPORT_MODEL`等で足りる箇所)③pricing登録漏れ時のfail-closedで有料run前に検知されるか。

## O-6 再利用(来歴契約)と費用
主張: 宅配の既存成果(Voice R0・Lead/紹介・案B・英訳)は来歴検査付きmanifestで取り込み、不一致はSTOP。正常系1記事の追加費用は約28〜39円(再利用あり)/約68〜93円(再利用なしの通常記事)。
観点: ①再利用manifestが『古い成果物を黙って使う』リスクになっていないか(来歴・sha・Gate status)②Voice R0 20〜26円とClosing 17〜22円が量産単価の主因=低減策(effort、Master store、再生成削減)のうちProduction承認範囲内で取れるものはないか(medium化は不採用候補、独断変更不可)。

## O-7 進行中仕様との接続(er119/er120/Part 1)
主張: 接続点としてstage 8の直後に差込み、I/F確定後に結線。HR待ちはrc=4で中断し再開は同run内。
観点: ①別agentのI/F未確定のまま設計することで、後から大きな手戻りが出る箇所はないか ②Yだけ先行して`PRODUCTION_WIRED`と宣言しない運用の確認 ③HRあり/なし両経路のevidence計画(E-2)の妥当性。

## 追加観点(任意)
- Std減速とVoice別TTS Voiceの相互作用(『人物の語りだけ減速なし』版は未決でX準拠既定)の扱い。
- 台帳(`spec_ledger_01.json`)と既存の『共通仕様のFamily別配線Status表』の二重管理にならないか(Closeout項目33提案の妥当性)。
- 作業分解・並列案・所要見込み(DESIGN_01 §12)の妥当性。
