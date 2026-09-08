# EDITORIAL-B-FAMILY-VOICES-PHASE1-5-FOUR-VOICES-AXIS-DESIGN-TRIAL-01

Lane: B(設計検証Trial、Lane A[Family A棚卸し]とは独立、Lane Aファイル未参照)
テーマ(固定): "Should companies use AI to screen job applicants?"
記事本文・音声生成・Production/Prompt/Contract編集・SSOT編集・Git操作は
**一切実施していない**(タスク範囲外)。

## 1. 目的

4 Voices記事の完成を目的とせず、「4 Voicesをどういう軸で選ぶか」の設計を
検証すること。4 Voicesの選定軸そのものはユーザー判断が必要な状態で
Trialを終了する(最大Status: VALIDATED、採用可否は含まない)。

## 2. 前提確認(既存資産、Grepで引用・全文読込せず)

- `DECISION_LOG.md`(263-275行): 初回Trialは「Voice数2」に**ユーザーが
  明示的に限定**していた。3以上は当時からUSER_DECISION_REQUIRED。
- `ER-010-EDITORIAL-TYPE-WRITER-ARCH-01_REPORT.md`(223-244行): Voices
  仕様は元々「Perspective数は2〜4でFlexible」という構想であり、Trial 1は
  意図的に2に限定しただけ(4は逸脱ではなく元構想の上限)。Perspective
  定義は「立場→何を重視しているか→だからどう見えるか」で、本Trialの
  stakeholder perspective定義と一致。
- `EDITORIAL-B-FAMILY-VOICES-TRIAL-06-PERSPECTIVE-SELECTION-EDITOR-DIAG-01
  _REPORT.md`(469-476行): 選定基準は「立場・責任の非対称性を要求」から
  「一般視聴者にとって主要な意見から順に選ぶ」へユーザー判断で上書き済み
  (VALIDATED)。→ representative優先というTrial前提と整合。
- `EDITORIAL-B-FAMILY-PRODUCTION-PATH-DESIGN-01_REPORT.md`(93-174行)・
  `EDITORIAL-B-FAMILY-VOICES-COMMENT1-CONTRACT-FINALIZE-11_REPORT.md`
  (84-176行): Hook/Voice A/Voice B/Tension/Closingの5区画構造、Voice
  A=Algieba/Voice B=Erinome固定、Comment 1〜4は`APPROVED_FOR_PRODUCTION`
  済み確定版。Comment 2は「One Voiceの後、続けてAnother Voice」という
  2者間前提の文言であることを確認。

## 3. Research(backstage)

既存Research/Ledger primitiveへの追加API呼び出しは行わず、一般知識に
基づき主要stakeholder(Applicant / Recruiter / Hiring Manager /
Business・Efficiency / Legal・Compliance・HR Governance / AIベンダー /
労働者側アドボカシー / 中小企業経営者)の立場・責任・制約・守りたいもの・
懸念を整理した(数値・統計は使用していない)。LLM費用: ¥0。詳細は
`er012_output/editorial_b_voices_phase1_5_four_voices_axis_trial_01/
design.md` §1。

## 4. 4 Voices候補軸(4案)と評価

案A(ユーザー提示候補型: Applicant/Recruiter・HM統合/Business・Efficiency/
Fairness・Legal・Governance)、案B(採用パイプライン内部の4段階)、案C
(影響を受ける側2者[経歴の異なる応募者2種]+運用する側2者[急成長企業
Recruiter/中小企業経営者])、案D(企業規模×採用側・応募者側の2x2)を提示。
6項目(代表性/重複の少なさ/立場・責任・制約・守りたいものの違い/Tensionの
作りやすさ/2 Voicesとの差/4 Voicesにする価値)で3段階評価し、3 Voices
構成にした場合にどのVoiceを落とすと何が失われるかを整理した。詳細な
評価表・根拠は`design.md` §3。

## 5. 推奨案

**案A**(Applicant/Recruiter・HM統合/Business・Efficiency/Fairness・Legal・
Governance)を推奨。評価表で5項目中5項目「高」、Trial-06のrepresentative
優先原則・本Trial前提に最も素直に合致、かつ「会社側」の中にも推進
(Business)と慎重(Legal)の対立があるため単純な2陣営対立に見えにくい点を
主な根拠とした。案B/C/DはREJECTEDではなく、別テーマや将来のVoices記事の
軸候補として保持。詳細は`design.md` §4。

## 6. 既存構造への構造上の論点(列挙のみ、設計はしない)

見出しブロック数ハード制約(`h3_matches != 2`)、`five_section`物理構造の
2 Voice固定、TTS音声2声固定、Comment 2の2者間前提文言、Tension slotの
4者統合方法未設計、Point Overlap QA/Analytical Leakage Checkのペア比較
前提、語数・音声尺の倍増、Audio Validation Gate segment名の拡張可否
未確認、の8点。いずれも未承認仕様であり、本Trialでは変更・設計していない。
詳細は`design.md` §4末尾。

## 7. Gate 1分類

設計軸の妥当性: **VALIDATED(Trial範囲内)**。3案以上の代替軸・評価表・
3 Voices比較・推奨理由を根拠付きで提示できた。既存SSOT(Voice数2〜4
Flexibleレンジ、Trial-06選定原則、Perspective定義)と矛盾なし。

採用判断(どの案を選ぶか・4 Voices自体へ拡張するか): **USER_DECISION_
REQUIRED**。

## 8. 費用・Lane間影響

LLM追加費用: ¥0(既存SSOTのGrep引用と一般知識による整理のみ、TTSなし)。
Lane A管理下ファイル(`docs/pm/*`, `er011_*`, `OPEN-1xx-*` 等)は一切
参照・変更していない。新規作成物は本Report(root)と
`er012_output/editorial_b_voices_phase1_5_four_voices_axis_trial_01/
design.md`のみ。Git操作(add/commit/push)は実施していない。

---
Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01SPsKBAZP5KEqdTH9TnkJdp
