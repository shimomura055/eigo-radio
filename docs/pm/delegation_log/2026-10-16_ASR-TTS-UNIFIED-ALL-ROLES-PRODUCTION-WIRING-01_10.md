# 委任_10 全文(T-0保存)

## 管理ID

`ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01` 委任_10(A-3 U1是正の実装+A-4 U2整理+Regression[unit負例・frozen・live負例対照・保存wav×live Azure]+SSOT反映+commit/push)。並行: `FAMILY-C-JA-TTS-PRODUCTION-FIX-01` 委任_02(er013系を編集・commit/pushを行う。本委任とは編集ファイルが重ならない)。DQI/AUW_09の未追跡ファイルはaddしない。Git競合回避: commit時に`.git/index.lock`があれば60秒待って再試行(最大10回)。mainへの反映は`C:\Users\tensh\eigo-radio-crbn`で`git pull --ff-only origin main`→`git merge --ff-only <branch>`(ff不可なら`--no-ff`、競合は中止報告)→`git push origin main`(rejectedなら`pull --ff-only`して再push、最大3回)。

## 前委任(委任_09)の受入記録(Gate 7)
- 当初目的(ユーザー原文逐語、`docs/pm/delegation_log/2026-10-16_ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01_09.md`「ユーザー指示(原文)」節): A-3「固有名詞差でもPrimary NGならSecondary確認。低類似度でもPrimary NGならSecondary確認。Secondaryが原稿を正当に支持すればWARNING付き採用。数値・否定等の保護差、独立QAは例外として維持。既存日本語ASR Validator・Pronunciation Ledgerとの整合確認。過剰救済・誤受理がないことをRegressionで確認。」A-4「Primary PASS時のSecondary強制照合を、根拠なく全レベルへ拡大してはならない。」
- 最終成果物: `er058_output/unified_all_roles_production_wiring_01/U1_U2_SECTION_PLAN_09.md`。
- 証拠: judge.py:65/111-118/128-129、frozen replay 25行(g7/g8のみ変化、C群NG維持)、U2実体=`er003_v1_crosslevel_audio_02_common.py:364`(2026-08-26承認)。
- 一致・不一致: 計画としては一致。Opus条件Cレビューで、frozen replayに解放クラスの負例が無い(誤受理0は未検証)、登録読み保護の素通り経路(BLOCKER)、空転写→技術STOP経路(MAJOR)、A3の根拠誤り(MAJOR)が判明→本委任で是正。
- 判定: 委任_09=ACCEPTED(計画)。QDC: 費用JPY0/改善見込み高/次=本委任。

## 性質/到達上限Status/禁止事項

- 性質: ユーザー承認済み統一仕様(2026-10-16指示A-2/A-3)への実装修正(Production判定フローの是正)。到達上限Status: `U1_FIXED_EVIDENCE_PENDING_FABLE`。`PRODUCTION_WIRED`は書かない。
- 禁止: `git add -A`/`-f`、amend、rebase、force push、stash、clean、`reset --hard`、`checkout -f`、STOPセンチネル削除・回避、HR Lock変更(U4=現行許容)、`force_secondary`の適用拡大(A-4)、PHONETIC_MATCH等「読みでの受理」の導入(2026-10-11安全条件)、A4(C2同形異音)・P1(数値・否定)の変更、β test(最終判定の安全性を検証するtest)の期待値変更、EN側の除外挙動変更(A5/A6はJAのみ)、有料runの再起動(26節)。
- 条件付きSTOP(Fableへ): (s1)live負例対照で1件でもPASS/PASS_WITH_WARNINGが出た(誤受理)→当該結果を記録し、解放をrevertせず定数をTrueに戻した状態でcommitして報告。(s2)Melos japanese_title(Hangul転写)の保存wav×live Azureで「TTSが日本語でない音声なのにAzureが原稿どおり返しPASS」と判明→言語判定QAは新仕様のため実装せず報告。(s3)既存失敗2件(koro系)がAUW起因と判明し、β期待値変更なしに直せない。
- Opus独立技術レビューGate(11-3): 条件C 実施済み(2026-10-16)。Fable採否=下記「Opus指摘の反映要件」(全件採用、A3は別委任_11へ)。
- 時間見込み: 3〜4時間。費用: 見積 約JPY6、上限¥12(Guardrail)。承認区分: C。
- T-3定型文: 「上限¥12(Guardrail)。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時のみSTOPし、原因・既使用額・想定追加額・残作業を報告する。」

## 固定ブロック
E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3(委任文どおり。T-2: TTSは`TTS_EXECUTION_MODE=STANDARD`明示、実行前に差分再生成可否・キャッシュ有無・--budget明示・想定外全再生成ならSTOPの4点確認)。

## ユーザー指示(原文)
`docs/pm/delegation_log/2026-10-16_AUW-FAMILY-C-DQI-USER-INSTRUCTION.md`の「# A.」節 A-2〜A-7を正とする。A-2の太字「**Primaryの差が大きいという理由だけでSecondaryを省略したり、Secondaryの正当なPASSを拒否したりしない。**」、A-3「これは新仕様Trialではなく、**承認済み仕様への実装修正**である。」

## Opus指摘の反映要件(U1R-01〜10)
- R1(U1R-01 BLOCKER、採用) A6(C1固有名詞差)のうち`reading_dictionary_mismatch`信号だけはSecondary事前除外として残す。名目を「登録読み保護」に改める(新rule_id例 `A7_READING_DICT_MISMATCH`、langs=("ja",))。`entity_like`と辞書未登録の`latin_in_canonical_diff`は解放。A5(類似度<0.4)は解放。この範囲限定はユーザー報告で明示する。
- R2(U1R-02 MAJOR、採用) JA adapterで「エラーなし完了の空転写」を`SecondaryOutcome(text=<no_speech sentinel>, accepted=False, label="NO_SPEECH")`として返し、`NG_BOTH`にする。JA限定、EN不変。
- R3(U1R-04 MAJOR、委任_11へ分離) A3(length NG)の挙動は変えず、計画書/SSOTの「独立QA」記述を訂正し、OPEN新規起票を行う。
- R4(U1R-05 MAJOR、採用) Regression: (a)unit負例 (b)live負例対照6〜8 clip、1件でもPASS/PASS_WITH_WARNINGならs1 (c)保存wav×live Azure 8本集計に遷移件数とMelos切り分け(s2) (d)U1=Trueのmonkeypatchロールバックtest 1本。
- R5(U1R-06 MINOR、採用) U2: 死定数`U2_FORCE_SECONDARY_SCOPE`削除(test更新)、`force_secondary=True`呼出点の静的test、SSOT訂正(CURRENT_SPEC.md:1933/2685追記形式)、news_tail_fix:178はOPEN候補、sing01_audio_generate.py:118/158のProduction経路Grep記録。
- R6(U1R-09 MINOR、採用) `_scg_exclusion_reason`順とコメント更新。
- R7(U1R-10 MINOR、採用) 既存失敗2件がAUW前(`cf4aca321`)でも失敗するか一時worktreeで確認。
- U1R-07・U1R-08は委任_11。

## KPI provenance欄
frozen 25行=frozen。保存wav×live Azure 8本=reuse+fresh。live負例=synthetic+fresh。unit負例=synthetic。E2E自己確認: No。

## Opus台帳更新
`docs/pm/OPUS_FINDINGS_LEDGER.md`に`OF-AUW-U1R-01`〜`-10`追加(追記のみ)。

## 手順概要(委任文の事前指定Read/Grep/実行コマンド/SSOT追記文/Git/報告項目は、受領文の手順0〜8および手順3〜8の追記文・RESULT_PACKET_AUW10 12項目どおり)
手順0 ff+STOP check(rc=0確認済み)/手順1 実装/手順2 test(netguard)/手順3 frozen replay/手順4 保存wav×live Azure 8本(約JPY3)/手順5 live負例対照(約JPY2〜3)/手順6 R7 worktree/手順7 文書(IMPLEMENTATION_10.md, RUNTIME_EVIDENCE_06 §16, SSOT, Opus台帳)/手順8 Git(secret scan→明示add→commit→crbnでmain反映)。SSOT追記文(CURRENT_SPEC「追記(2026-10-16 委任_10、U1是正)」、DECISION_LOG委任_10エントリ、OPEN新規4件[A3再評価/news_tail minimal fallback/Melos Hangul/既存失敗2件]、REGISTER #83/#84、REPORT_LEDGER)は委任文原文どおり。
(注: 本ファイルは受領文の構造を保持した保存版。実行コマンド列のコミットメッセージ等の詳細は上記と同一。)
