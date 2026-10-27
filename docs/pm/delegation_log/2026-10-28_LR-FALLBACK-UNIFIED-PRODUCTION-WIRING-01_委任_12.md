# 委任_12(Phase B / B7): 既公開・未公開記事の是正(AI島 UD-2適用→Gate再評価→組立→候補ページ+最終Human報告 / Word Gacha Adv・猿の手Std=1語表示overlayの候補ページ / メロス=対象外の確認)(API 0)

共通事項=`…_委任_00_COMMON.md`。前提=統合配線commit(委任_11、`BWIRE_INTEGRATED_WIRING_01.md`)完了後。設計=`INTEGRATION_01.md`(F-10/F-11/F-14)+`OPUS_REVIEW_01.md`(R-7、(d)既公開2件)+`W2_UD1_BODY_REFLECTION_DESIGN_01.md` §8+`B2_LEDGER_MODULE_01.md`。ユーザー原文§4・§8(必読)。成果物=`docs/research/LR-FALLBACK-UNIFIED-PRODUCTION-WIRING-01/B7_PUBLISHED_ARTICLES_01.md`。**実装/制作委任(API 0。再TTS・再生成・LLM呼出は禁止)**。

## 作業
1. **AI島(X、未公開、OPEN-561/563、hr_02 run)**: 特別扱いコードなし。配線済み正式経路で(a)M3再評価(k2のLR=正常LR→`LR_APPLIED`警告で通過。他項目は従来どおり) (b)三者一致Gate(overlay後 Std `AI agents`/Adv `AI systems`=TTS入力=ASR正解) (c)assemble→pages(**既存のLR後音声を使用、再TTSなし**)→候補ページ(新dir `user_test/<既存命名規則>_candidate_…`、既存公開dirを上書きしない)→page_verify (d)`er131`で最終Human報告(Std/Adv、LR赤表示)を`final_human_report/X/ai_island/<run>/`へ生成。hr_02のHR Lock/UDR状態の整理(hr_02 Q1はUD-2で置換済み)。学習項目・解説・in_one_line(`AIs`残存=C、UD-2範囲どおり)は不変。確定KP/KW/文法との重なりT1-T3=非干渉を記録。
2. **Word Gacha Adv(X、公開中、OPEN-499、you've→you have、UDR #183(a)承認済み)**: builderで候補ページを再描画(overlay適用)し、公開版との差分が**該当1語のみ**であることをdiffで示す(2か所以上なら原因特定を先に、手修正しない=Opus (d))。候補dirへ出力、`check_page`+ハイライト検査PASS、最終Human報告生成。**公開差替えはしない**(記事単位のユーザー承認待ちとして報告)。
3. **猿の手Std(Z、公開中、guest→visitor、注記あり)**: 同様に候補ページ(overlay+LR注記撤去)、差分=該当1語+注記撤去のみ、`page_verify`PASS、最終Human報告(採用take UNKNOWN=「記録なし」表示を含む)。公開差替えはしない。
4. **メロスAdv**: 現行公開`family_z_melos_02`(run_e2e_05/06)がLR 0・不一致なしであることを再確認し、最終Human報告(発動なし)を生成。旧`family_z_melos_01`はsupersededで対象外(原文§8との差として明記)。
5. **告げ口心臓**: 変更なし。最終Human報告(Std: 発動なし/Adv: kp2_en ENGLISH_LOCK青)は委任_09で生成済みなら再利用、無ければ生成。
6. 各件の照合表(変更前後の本文・実音声sha・ASR基準・学習項目・ユーザー承認記録・注記)を成果物へ。STOP該当(確定内容との衝突)があれば該当件のみSTOPし理由を報告。
7. Git: 候補ページ・最終Human報告・成果物のみ`git add`(公開dirは不変であることを`git status`で示す)、commit「LR-FALLBACK-UNIFIED-PRODUCTION-WIRING-01 委任_12(B7): AI島UD-2適用候補ページ+既公開2件候補ページ+最終Human報告(API 0、公開差替えなし)」+`Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`、`git push origin HEAD:main`。
8. 最終応答: 成果物パス+各記事1〜3行(候補URL・最終Human報告URL・差分・Gate結果・承認待ち事項)。
