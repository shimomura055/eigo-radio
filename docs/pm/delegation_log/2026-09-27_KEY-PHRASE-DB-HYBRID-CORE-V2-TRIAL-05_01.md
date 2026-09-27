# 委任文全文(2026-09-27、KEY-PHRASE-DB-HYBRID-CORE-V2-TRIAL-05、初回)

管理ID: KEY-PHRASE-DB-HYBRID-CORE-V2-TRIAL-05(ユーザー承認 2026-09-27)。一時ファイル `docs/pm/ACTIVE_TASK_KPV2.md` / `docs/pm/RESULT_PACKET_KPV2.md`(commitしない)。委任文全文を `docs/pm/delegation_log/2026-09-27_KEY-PHRASE-DB-HYBRID-CORE-V2-TRIAL-05_01.md` に保存しcommitに含める。Guardrail **¥70**(v2で13〜15本文×約¥1.1+予備。v1側は既存artifact再利用で再実行しない。事前見積>¥60ならSTOP)。APIキーは環境変数のみ。**到達可能Status: REJECTED / VALIDATED / USER_DECISION_REQUIRED(仮分類、確定はFable)。Trial成功でもAPPROVED_FOR_PRODUCTIONにしない。Production配線禁止。**

## ユーザー指示(逐語要旨、厳守)
目的: Family Z Trialで見つかった候補生成段階の2つのCore課題を一般化して改善し、Family X側を悪化させずに共通Core品質を上げられるか確認する。「Family Z向け特殊化」ではなく「共通Coreの一般的な候補生成品質改善」。
Core v2の主対象:
1. **word bucket ranking改善**: 生wordfreqの屈折形バイアスを減らす。lemma正規化後の頻度利用を第一候補。必要ならCEFR-J等の既存資産との併用可。**新DB追加禁止**。`loyalty` のような重要語が活用形の見かけ上の低頻度に押し出されないことを確認する。
2. **multiword/idiom lookup改善**: `in someone's place` のような重要multiword表現がlookup対象に入らない問題を改善。lookup候補優先順位・budget配分見直し。単純なbudget増だけで解決せず候補選定の質改善を優先。idiom/phrasal verb/重要multiwordを優先できる一般化。**Family Z固有hardcode禁止**。
3. **proper noun / dialogue tag除外の明示化**: `Echo said` 等の会話タグFPが偶然wordfreq閾値で落ちているだけの状態を解消。登場人物名・固有名詞・dialogue attributionが候補に混入しにくい一般機構。一般英単語と固有名詞が同形の場合のfalse exclusionに注意。既存の真のphrase/idiomを落とさないこと。
評価データ: Trial-04のFamily X 12本文 + Family Z Melos A2 + 利用可能なら既存Melos B1B相当または既存Fiction本文(`er026_output/`、`er013_output/`(Family C legacy、read-only参照可)等をGrepで探す)。新規記事生成は最小限。**新規生成が必要なら勝手に作らず「既存素材不足」として報告。**
比較: Core v1 vs v2 を同一本文・同一条件。
Family X側必須確認: 既存重要語保持が悪化しない / Trial-04 structural PASS 12/12維持 / 既知bug A〜E再発なし / small_bag一般語偏重が悪化しない / shortlist quality / phrase・idiom quality / rare・technical single word / cost / call数 / 全文非送信 / 1本文1 call / runtime model・routing。
Family Z側必須確認: `loyalty` が候補生成段階へ復帰するか / `in someone's place` 相当の重要multiwordが候補化されるか / proper noun・dialogue tag FP / narrative relevance / phrase・idiom quality / 一般語偏重 / 既存Family Z Production KPとの比較。
STOP条件(該当時はUSER_DECISION_REQUIREDで報告、拡張しない): 新DB追加が必要 / 追加LLM callが必要 / Production moduleを直接変更する必要 / Family X v1 baselineを変更しないとTrialできない / 大幅なcost増 / 重要な既存KP regression / 新しい大規模仕様変更が必要 / Trial途中で別の改善仕様を追加したくなった場合。
受入観点(理想): X 12本文 regressionなし / Z: loyalty・important multiword回収改善 / structural PASS維持 / cost同等 / 1本文1 call / 全文非送信 / proper noun・dialogue tag FP悪化なし。

## 並行ルール(厳守)
- **v1 baseline固定**: er029(Trial-04, commit 57b61273)・er030(別AgentがProduction昇格中)・er028/027・er003_key_words_* は**変更禁止**(read-only import)。
- Core v2は新規 `er032_key_phrase_db_hybrid_core_v2_trial_05_{stage1,run,test}.py` に閉じる(er029をimportして差分だけをoverride/拡張する形が望ましい。複製する場合はv1との差分をREPORTに明示)。
- 共有ストア非書込み。出力 `er032_output/key_phrase_db_hybrid_core_v2_trial_05/`。SSOT編集なし(記載案のみ)。

## 作業
1. 既存資産照合: Trial-04 REPORT留保①〜④、Family Z Trial REPORT(切り分けa/b、会話タグ非再現の真因)、er029 stage1の該当関数(word bucket ranking / `select_unmatched_ngram_candidates_for_lookup` / 固有名詞ガード)。
2. v2実装(1〜3)。lemma化は既存資産(CEFR-Jのlemma/pos情報、既に依存にあるライブラリのみ。新規pip依存が必要ならSTOP)。固有名詞判定は文頭以外の大文字開始・dialogue attribution動詞(said/asked/replied等の一般リスト)・記事内一貫大文字などの一般規則+同形一般語のfalse exclusion回避(小文字出現がある語は除外しない等)。各規則をunit testで固定(loyalty復帰、in someone's place候補化、Echo said除外、"Mark" vs "mark" false exclusion回避、既存phrase/idiom保持)。
3. v1 vs v2: X 12本文はv1=Trial-04既存artifact(`er029_output/`)を再利用、v2のみ実行。Z Melos A2はv1=Family Z Trial Z0 artifact再利用、v2実行。追加Fiction本文があればv1/v2両方実行(v1側もcall必要、見積に含める)。同一条件(1本文1 call、全文非送信assertion、Strategy L model routingは既存)。
4. 比較表: 本文ごとに structural PASS / shortlist件数・構成(word/phrase/multiword) / 最終5件 / 重要語保持(Trial-04で確認した核心語+loyalty/in someone's place) / 一般語比率 / 固有名詞・会話タグFP件数 / bug A〜E / cost / input tokens。X側regression判定(悪化本文があれば明示)。
5. REPORT `KEY-PHRASE-DB-HYBRID-CORE-V2-TRIAL-05_REPORT.md` 新設(Closeout必須項目: v1→v2差分 / X側regression / Z側改善 / cost / shortlist変化 / false positive / unresolved limitation / **Production採用時に共有Core(er030)差し替えが必要か**とその影響範囲・regression計画 / STOP該当 / Status仮分類 / 素材不足の有無)。

Git: er032_*・出力・REPORT・delegation_logのみpath指定add(`git add -A`禁止、他Agent[er030_*, er019_*, er003_v1_*, er025_*, SSOT]のstageを外さない、index.lockリトライ)。トレーラー `Management-ID: KEY-PHRASE-DB-HYBRID-CORE-V2-TRIAL-05`。push origin main。reset/amend/rebase/force push禁止。RESULT_PACKETに費用・commit hash・変更ファイル・比較表要約・STOP該当・Status仮分類を記載。
