# 委任_10(Phase B / B3準備): 表示本文overlay・三者一致Gate・Z注記撤去・X公開ページ事後試聴リストの実装(**配線はしない=関数と差分パッチを用意**)+混入検知test(API 0)

共通事項=`…_委任_00_COMMON.md`。設計=`INTEGRATION_01.md`(§1・F-1/F-5/F-9)+`OPUS_REVIEW_01.md`((b)-5/(b)-8、M-1/M-7/M-8、R-6、Fable照合)+`W2_UD1_BODY_REFLECTION_DESIGN_01.md`(§3反映点・§7 test計画)。前提module=`er129_lr_display_reflection_01.py`(委任_07)。成果物=`docs/research/LR-FALLBACK-UNIFIED-PRODUCTION-WIRING-01/B3_OVERLAY_AND_PARITY_GATE_01.md`。**実装委任(限定)**: 新関数・新testは追加可。**既存Production関数の呼出切替(配線)はしない**。配線に必要な変更は、適用可能なpatchファイル(`docs/research/LR-FALLBACK-UNIFIED-PRODUCTION-WIRING-01/patches/B3_wiring_01.patch`、`git diff`形式)として用意し、統合配線commit(別委任)で適用する。

## 作業
1. **表示overlay関数**(X `er019_family_x_listening_page_01.py`/`er_user_listening_page_common_01.py`、Y相当、Z `er063` pages 描画 ~:2459,2502)に対し、er129 ledgerの`lr.after`+anchor位置で表示本文を書換え後文へ差し替える純関数を**新規追加**(既存描画関数は未呼出のまま)。ハイライト解決(SLOT-23 `data-hl`)が書換え後文でも確定候補IDに紐付くこと(確定語句がLR範囲外である前提=overlap T1非干渉)。
2. **三者一致Gate関数**(assemble入口1か所、Opus (b)-5): X/Y/Z各assembleの直前に置く`assert_text_parity(run, level)`を新規追加(未呼出)。不一致・位置不能=技術STOP(X/Y `BLOCKED_LR_DISPLAY_CONSISTENCY`、Z `FamilyZ…Stop`)、HRキューへ入れない。未配線中は常に異常側(配線後に初めて通る)設計の確認。
3. **Z公開ページ注記撤去**(F-9、M-7で限定): `er063:2464-2468`のLR/Fallback由来注記のみ撤去するpatch。`Voice:`/`TTS方式`表示は維持(`er063_family_z_page_verify_01.py:68,70`の検査が偽NGにならないことをtestで固定)。
4. **X公開ページ事後試聴リスト**(M-7): `er019_family_x_listening_page_01.py:159-166`のLR行(`LR_REWRITTEN`ラベル・期待文・ASR文)を`audience="public"`では非表示にするpatch(HR audienceは従来どおり)。
5. **混入検知test**: 公開HTML・TTS入力・ASR期待文・Style Prompt・KP表示・study_textに注記文字列・`fhr-`class・`LR_REWRITTEN`/`LR_APPLIED`/`FALLBACK_APPLIED`/Fallback Style名が0件(保存run実測)+`check_page(public)`への検査追加patch。
6. mock integration(X/Y/Z、API 0): overlay+parity Gateを一時的に呼んだ場合にAI島Std/Adv(LR 1語)・猿の手Std・Word Gacha Advで表示が書換え後文になり三者一致PASSすること、LR 0のrun(告げ口心臓・メロス_02)で不変(byte同一)であることをtest内で確認(Production呼出は変えない)。
7. Git: 新関数ファイル(既存module内への**未呼出関数追加**は可)+test+patch+成果物のみ`git add`、commit「LR-FALLBACK-UNIFIED-PRODUCTION-WIRING-01 委任_10(B3準備): overlay/parity Gate関数+配線patch+混入検知test(未配線、API 0)」+`Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`、`git push origin HEAD:main`(競合時`git pull --no-rebase origin main`)。同時進行の委任_08(`er130_*`)・委任_09(`er131_*`)のファイルには触れない。
8. 最終応答: 成果物パス+要約10行(追加関数file:line/patch内容/test件数/mock結果/既定動作不変の根拠)。
