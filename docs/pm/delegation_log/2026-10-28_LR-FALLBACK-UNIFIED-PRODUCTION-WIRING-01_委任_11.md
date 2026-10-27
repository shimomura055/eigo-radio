# 委任_11(Phase B / B-wire): 統合配線commit(1 commit)=三者一致Gate・M3/Y/Z Gateの分類核切替・表示overlay・Z注記撤去・X公開ページLR行非表示・Z `style_actual`是正(B6)・check_page検査+全回帰(API 0)

共通事項=`…_委任_00_COMMON.md`。設計=`INTEGRATION_01.md`(F-4/F-5/F-7/F-9/F-16)+`OPUS_REVIEW_01.md`((b)-5/(b)-8、M-7/M-8/M-9/M-10、R-6、Fable照合)。前提成果物(必読): `B1_FINAL_ADOPTION_01.md`(d3775dae7)、`B2_LEDGER_MODULE_01.md`(e56c9a04f、er129)、`B4_CLASSIFY_CORE_AND_DIFF_AUDIT_01.md`(er130、差分監査)、`B3_OVERLAY_AND_PARITY_GATE_01.md`+`patches/B3_wiring_01.patch`(er132)、`B5_FINAL_HUMAN_REPORT_01.md`(er131)。成果物=`docs/research/LR-FALLBACK-UNIFIED-PRODUCTION-WIRING-01/BWIRE_INTEGRATED_WIRING_01.md`。**実装委任**。

## 配線内容(Opus R-6: すべて1 commitに入れる。途中状態をmainへpushしない)
1. **三者一致Gate**: X/Y/Zの各assemble入口1か所で`er132.assert_text_parity`(er129 ledger導出)を呼ぶ。不一致/位置不能=技術STOP(HRキューへ入れない)。LR 0のrunは不変。
2. **Gate切替**: X `m3_assembly_gate`(`er019_family_x_style_profile_01.py` ~L685-760)、Y gate(`er121_family_y_audio_01.py` ~L874-1000、**直読して照合**)、Z `run_audio_gate`のStyle/Fallback/LR項(`er063` ~L2063-2212、`Z_STYLE_FALLBACK_ADOPTED` 2138-2140)を`er130.classify_adopted_take`へ接続。正常LR/Fallback=PASS_WITH_WARNING(`LR_APPLIED`/`FALLBACK_APPLIED`、HR非要求)、異常/UNKNOWN/記録不一致/品質NG/overlap/parity不一致=従来どおりBLOCK/STOP。承認済みStyle照合・ASR判定・速度Gate・他Gate項目は不変。W3 §5の撤去予定(旧LR項・旧Fallback項とそのtest)を実施し、Dangling Referenceを残さない(撤去一覧を成果物へ)。
3. **表示overlay**: X/Y/Zページ描画をer132 overlay経由(書換え後文、SLOT-23ハイライト維持)に切替(`B3_wiring_01.patch`適用)。
4. **Z公開ページ注記撤去**(LR/Fallback由来のみ、`er063:2464-2468`)。`Voice:`/`TTS方式`は維持(page_verify不変)。
5. **X公開ページ事後試聴リストのLR行**をpublic audienceで非表示(HRは従来)。
6. **B6 Z `style_actual`是正**: `build_style_actual_record`(`er063:1996-2036`)の採用attempt同定を`er129.resolve_adopted_take`に置換(M-8: 本commitで同時に入れる)。
7. **check_page(public)**へ混入検知(`fhr-`/注記文言/`LR_REWRITTEN`/`LR_APPLIED`/`FALLBACK_APPLIED`/Fallback Style名)を追加。
8. **最終Human報告生成器(er131)の呼出**: E2E_STAGESには入れない(原文§2)。assemble/pages完了後にrunnerが**任意の後処理として**呼ぶ場合も既定OFFのCLI実行に留める(本委任では配線しない。運用手順を成果物に記載)。

## 検証(commit前、全部PASSが条件)
- 変更module関連test+新規(er127/er020/er129/er130/er131/er132/er019/er121/er063/er128/er117/er078)。全回帰`run_project_regression.py`(既知失敗はOPEN-543系等と差分なしを示す。HEAD^との比較)。golden A/B/C byte同一。
- 差分監査(B4)の再実行: 配線後の実Gate呼出で保存run(AI島hr_02・告げ口心臓・Y E-1・Word Gacha Adv・メロス_02・猿の手Std・tru_ev群)を読み取り専用再評価し「旧BLOCK→新PASS_WITH_WARNING(正常LR/Fallbackのみ)」「旧PASS→新BLOCK(正当性)」を再集計。**告げ口心臓Adv kp2_en=ENGLISH_LOCK→承認済みFallback警告で通過**(M-10)。偽BLOCK 0。
- mock E2E(X/Y/Z、API 0): LRありmock・Fallbackありmock・異常Style mock・記録欠落mock・parity不一致mockで、通過/停止が仕様どおり。
- **告げ口心臓run_reselect_01の位置確認**(Opus R-6): 完了済みrunのため新旧Gate混在なし。公開ページ`family_z_tell_tale_heart_reselect_01`は**再生成しない**(byte不変を確認)。
- 混入検知0件(保存run実測)。

## Git
変更ファイルのみ`git add`、**1 commit**「LR-FALLBACK-UNIFIED-PRODUCTION-WIRING-01 委任_11(B-wire): 統合配線(parity Gate・M3/Y/Z分類核・overlay・Z注記撤去・B6)+撤去(API 0)」+`Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`、`git push origin HEAD:main`。test失敗・競合・偽BLOCK>0ならcommitせずFableへ報告。
最終応答: 成果物パス+要約12行(配線点file:line/撤去一覧/test件数/差分監査結果/告げ口心臓判定/混入0/commit)。

## 追記(Fable、委任_09完了後)
- er129 test `test_u8_no_production_module_imports_er129`は設計上の利用者(er130/er131/er132+配線先のGate/pages module)をallowlistへ更新する(「公開ページ生成器・TTS・ASR・KP表示・Promptがer129/er131をimportしない」という意図は維持し、allowlistを明示列挙)。
- check_page(public)への混入検知(`er131.check_page_fhr_contamination`)の配線は、Z公開ページ注記撤去(F-9)と同じcommitで入れる(先に入れると猿の手Stdの既存注記で即NG)。既存公開`user_test/family_z_monkeys_paw_01/standard.html`は本commitでは再生成しない(候補ページは委任_12)ので、check_pageは**新規生成ページにのみ**適用されることを確認し、既存公開HTMLの一括検査はB7/B8で扱う。
- 最終Human報告の運用: E2E_STAGESに入れない。runner完了後の手順(CLI 1行)を成果物に記載。

## 改定(Fable、2026-10-28 ユーザー原文_02 `…_USER_02.md` §3・§4・§5・§7。APPROVED_FOR_PRODUCTION)
**「報告資料」=現在の試聴・確認フォーム(`user_test/`配下の試聴ページ)**と定義された(全Family・全レベル共通。将来のエンドユーザー向けアプリ表示は未決定)。したがって本委任の配線内容4・5を次のとおり置換し、`final_human_report/`(er131)は「試聴ページ内の表示部品」として再利用する(別dirの独立資料は補助扱い。重複生成は不要、同一描画部品を使う)。
- **4'(置換)**: Z公開(試聴)ページのLR/Fallback由来の旧注記(`er063:2464-2468`)は、新しい共通表示部品(下記)に**置き換える**(撤去して終わりにしない)。
- **5'(置換)**: X試聴ページの事後試聴リストLR行は非表示にせず、共通表示部品(赤)で表示する。audience区分による出し分けはしない。
- **新規6'**: 全Family(X/Y/Z+A/B/C等の既存Familyの試聴ページ)・全レベルの試聴ページに、er129 ledger由来の共通表示部品(er131の描画関数を部品化して流用)を配線: (①)**Chunk境界 `⏸`**=実際の分割記録(X chunk plan/Y chunk/Z `segment_plan`・`chunk_tts_evidence`)に基づき、本文表示の実際の境界位置にのみ表示(Chunk分割方法・語数・追加ポーズは不変。chunk記録がないrun/Familyは表示なし)。(②)LR=変更箇所を赤(変更前・変更後の英文、適用範囲)。(③)Fallback=適用テキスト全体を濃青+Style名注記+適用範囲。英語・日本語の全Role対象。LR+Fallback重複は双方識別可能。表示は「何が発動したか/何が変わったか/どこに適用されたか」の3点。制作本文・TTS入力・ASR正解・Style Promptには一切混入しない(混入検知testの対象から試聴ページHTMLは外し、TTS入力・ASR・Prompt・KP学習用表示・study_textに限定する)。
- 受入(原文_02 §7-3〜6): 全Family・全レベルの試聴ページで⏸/赤/青が実際の記録と一致、正式経路・再生成・再開経路で維持(`pages`stage再実行で同一結果)。確認できないFamily/Levelは「未確認」と明記しPRODUCTION_WIREDにしない。
- 既存公開ページの再生成は本commitでは行わず(pages stage再実行はB7/B8で記事単位に実施)、新規生成経路の配線とtest(保存run読取で描画)まで。
