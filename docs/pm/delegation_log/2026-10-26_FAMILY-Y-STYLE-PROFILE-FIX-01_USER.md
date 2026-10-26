# FAMILY-Y-STYLE-PROFILE-FIX-01 ユーザー指示原文(逐語, 2026-10-26)


# 緊急指示｜Family Y Style不整合の最優先是正・完成版再提出・Open Item整理

## 1. 最優先事項：OPEN-537

Family Y『宅配の再配達は有料にすべきか？』が、承認済み共通Styleの継承に関する不整合を残したまま完成版として提出された。

調査記録によれば、Family Yの正式Production runnerは`default`固定であり、設計・仕様台帳に記載された`fx_20261017`のStyle群が適用されていない。

**OPEN-537を最優先で解決すること。他の独立作業は可能な範囲で並列継続してよいが、本件の解消を不合理に後回しにしない。**

### A. 原因究明・再発防止

次を明確にする。

- なぜ設計・仕様台帳ではStyle継承を定めながら、Production runnerは`default`になったのか。
- なぜ正式Productionの配線・受入検証で不整合を検出できなかったのか。
- なぜ発見後も完成版提出を優先し、未解決事項を持ち越したのか。
- なぜFable受入・PM Gate・SSOT管理で止められなかったのか。

単なる定数修正で終わらせず、正式初回経路のStyle確認と受入検証に必要十分な再発防止を組み込むこと。

### B. 正しいStyleの適用

Family X/Z/Y共通の承認済み仕様と、Family Y固有の3 Voice設計を照合する。

- 共通部位：承認済みのPD06、S3、E1、K2、P8-KP、P7等の適用要否を、既存の承認・例外記録に従って確定する。
- Voice 1〜3：人物別の声・主観性・自然さを維持する。PD06を一律適用して個性を失わせない。
- Family Y固有のStyleが正式承認済みであれば、その仕様を優先し、例外を明確に記録する。
- 未承認の新しいStyleや品質基準を独断で採用しない。

**承認済み仕様の配線漏れは自律的に是正する。一方、既存承認だけでは決められない重大なStyle方針変更は、根拠と品質影響を提示してユーザー判断を求める。**

### C. 再配達記事の修正・再提出

今回の完成版は旧Styleで制作されている。

是正後の正式Production経路で、影響を受ける音声を必要な範囲だけ再生成し、Standard／Advancedの両方を再組立・公開すること。

- Voice 1=Puck、Voice 2/3の承認済みVoice、3人のPersonaを維持。
- Advanced Comment 2削除を維持。
- 既に品質PASSしている無関係な音声は再利用する。
- TTS・ASR・音声QA・組立・公開検査を実施。
- 変更前後のStyle、対象音声、品質、費用を報告。
- 修正版の試聴URLをユーザーへ提出する。

**以前の試聴承認は旧版に対する承認として記録し、新Style反映版はユーザーの再試聴・再承認を待つこと。**

## 2. OPEN-535｜Claude/Fableが自律解決

Voice変更時に旧Voiceに対するHuman Review承認が不適切に再利用され得る問題を修正する。

- 原因究明→修正→Regression→正式経路確認まで自律実施。
- Voice・Style変更後の旧承認流用を防止。
- 正常な再利用やresumeを壊さない。
- ユーザーに技術的な選択肢を逐一提示しない。

承認済み範囲で完成まで進め、必要なruntime evidenceとSSOT／Git反映を行うこと。

## 3. OPEN-527｜独立Open Itemを終了

Family Yの段落分割について、実際の記事が単一段落であることだけを理由に独立したOpen Itemを維持しない。

- 既存の分割仕様と実装状態を確認。
- 複数段落が必要な記事で通常のRegression／Production確認を実施できるようにする。
- 検証のためだけに記事本文を改変しない。
- 無理に分割を発火させる有料Trialは実施しない。
- 独立したOPEN-527は重複管理を解消してCloseoutする。ただし、未確認のProduction Wiringを検証済みと偽って記録しない。

## 4. QCD・Gate・完了条件

優先順位は**品質＞完成速度＞量産単価**。

既存の承認済みTTS Retry／Fallback／Local Rewrite共通仕様との整合も確認する。

OPEN-537・535の完了には、正式初回Production経路、retry／fallback／regeneration／resume、実際のStyle・Voice・モデル、必要な回帰・統合テスト、Fable独立受入、CURRENT_SPEC／DECISION_LOG／OPEN_ITEMS、Git反映の証拠が必要。

**開発上の不具合はClaude/Fableが自律的に解決すること。** 重大な仕様・品質変更、重要なQCDトレードオフ、予算・Scope超過、重大blocker以外をユーザー判断へ転送しない。

既存承認予算・日次1,000円（JST）・STOP条件を遵守する。超過が必要な場合は事前に根拠と見積りを示す。

## 5. 最終報告

以下を簡潔に提出すること。

1. OPEN-537の根本原因、正しい部位別Style一覧、修正・再発防止結果
2. 再配達記事の修正版Standard／Advanced試聴URL
3. OPEN-535の自律修正・回帰結果
4. OPEN-527のCloseout状況
5. Family Yの正式Production Wiring証拠、Fable受入、QCD影響
6. SSOT／Git反映、残る本質的な未解決事項

**Style不一致を未解決のまま「完成」「PRODUCTION_WIRED」として再提出しないこと。**

