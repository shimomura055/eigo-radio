# Trend Ledger Fix Diff

管理ID: EDITORIAL-4TYPE-FOLLOWUP-02-TREND-LEDGER-FIX-REGEN
実施日時(UTC): 2026-09-14T06:15:30.064929+00:00

## 背景

前回run(run1)のFact Checker(A2, attempt 1)がFAIL判定。理由:
記事がGoogleのXRメガネについて「まだ製品デモの段階で、確認済みの発売ではない」
という趣旨で記述していたが、GoogleはFact Checker実行時点(2026-09-14)より前の
2026-05-19に、Android XR/Geminiスマートグラスを2026年秋(fall 2026)に発売する
ことをGentle Monster/Warby Parkerコレクションの一部として公式発表済みだった。
これはResearch時点で既に存在していたはずの事実であり、時間経過による陳腐化
ではなく上流Research/Ledgerの取りこぼしとして扱う(ユーザー判断)。

## 再確認方法

Sonnetにweb検索ツールが無いため、既存の`vfl01.build_verification_prompt`/
Verification呼び出し(OpenAI web_search、`er003_v1_en_direct_vfl_01_generate.py`
の`run_verification_for_topic`と同一実装)を、F008(原文)+F008_FIX(新draft)の
2件のみに限定して実行した(Research全体の再実行はしていない)。
生JSON: `research/ledger_fix_verification.json`

## 再確認結果

- Source: blog.google「Intelligent eyewear with Gemini is coming this fall」
  https://blog.google/products-and-platforms/platforms/android/android-xr-io-2026/
- 発表日: 2026-05-19
- 内容: Googleは、Android XR eyewear ecosystemの最初の商用製品であるaudio-only
  「intelligent eyewear(audio glasses、ディスプレイなし)」を2026年秋(fall 2026)に、
  Gentle Monster・Warby Parkerの各コレクションの一部として発売すると発表。F008が
  記述するカメラ/オプションのin-lens display搭載版(2025年デモ)とは別の製品tierで
  あり、後者自体の2026年秋発売は本sourceでは確認できない(具体的な発売対象国/市場
  も本sourceでは確定できず、関連するSamsung発表では"select markets"と記載)。
- Verification verdict: F008_FIX = VERIFIED (F008 = AMBIGUOUS)

## Ledger差分

| 種別 | fact_id | 内容 |
|---|---|---|
| 修正 | F008 | notes_for_writerへ「F008_FIXを参照し、Android XR eyewear全体を'no confirmed launch date'/development-stage demoのみとして記述するのは(少なくともaudio-only製品については)禁止、ただしF008自体のカメラ/display版はF008_FIXとは別tierで、その版自体の2026年秋発売は未確認」という整合caveatを追記。claim/scope/conditions/date_or_periodはF008自体のsource([blog.google] android-xr-gemini-glasses-headsets、2025-05-20デモ時点の記述として)そのまま維持(削除ではなく整合)。 |
| 追加 | F008_FIX | 新規fact。「Googleが2026-05-19に、Android XR eyewear ecosystemの最初の商用製品であるaudio-only glasses(ディスプレイなし)の2026年秋発売をGentle Monster/Warby Parkerコレクション経由で公式発表。F008のカメラ/display版とは別製品tier」。source: blog.google/android-xr-io-2026。 |

旧factで矛盾していたのはLedger本体ではなく、Ledgerに欠けていた新しいfactを
記事(Writer出力)が補えなかった点。よって「削除」ではなく「修正(F008の
notes_for_writer整合)+追加(F008_FIX)」で対応した。

counts: VERIFIED 15 -> 16
(AMBIGUOUS/REJECTEDは変更なし)
