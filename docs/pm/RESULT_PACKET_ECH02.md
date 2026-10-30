# RESULT_PACKET ECH02 (ENDUSER-CLICK-HIGHLIGHT-NO-SEEK-01 委任_02)

結論: 英文クリック=英日選択ハイライトのみ(再生/シーク/一時停止なし)を asset `rev01-h` で実装し、既公開8dirを再produce(API 0)、runner X/Y/Z の pages段を各1回実走、push後の live(Pages)も PC+mobile 全NG0。**PRODUCTION_WIRED_PENDING_FABLE**(Fable独立受入待ち)。**未完は1件: ⑨ Meta(rev01-gのまま=クリックで再生される旧動作)**。費用 約¥0.99/Cap¥10。
code commit: `ff84fdb7d`(+ SSOT/RESULT_PACKET commit は本パケットを含む次commit)。

## 変更結果
- 新asset `enduser_page_assets/rev01-h/`(rev01-gから許可リスト派生。`derive_assets_01.py` EDIT J37-J49): `selectedSid`/`selTime`、`selectSentence(sid)`(`audio.play/pause/currentTime`を呼ばない)、`tick`分岐(再生中=選択解除し自動ハイライト優先 / 停止・一時停止・ended中=選択維持 / 再生位置が0.3秒超動いたら解除)、位置操作(シークバー・±10秒・ここから再生・全体再生・KP/Vocab再生・レベル切替)で解除。旧`seekSentence`と`syncKind!=='none'`ガードを撤去。style.css・DEV rev01-e・rev01-g/f/e は不変(残置)。
- `er135_enduser_rules_01.py` ASSET_BUILD_ID=rev01-h(:12)/`ASSET_TRANSLATION_KINDS`に rev01-h 追加(:22)。版固定test(`er135_enduser_align_test_01.py`/`er135_enduser_vocab_audio_test_01.py`)更新、静的test `A9_ClickSelectOnly` 追加。
- `er135_enduser_page_verify_01.py`: F `sentence_click_plays_from_sentence` を `sentence_click_does_not_play_or_seek`(paused維持・currentTime不変・`sel==sid`)へ反転(:277-283)、J3/J3b/M7をタップ/クリック共通`_click_sent`へ、M7 pause/resumeを`#pp`再生から再構成、K検査(`click_no_seek_checks` :513-)を追加(項目1,2,3,6+同一文再クリック+位置操作解除)。
- 範囲外は未実施: 翻訳仕様・本文/音声/TTS/Prompt・キーボード操作・日本語側クリック・rev01-e凍結dir・⑨。

## 6経路 Wiring 表(X/Y/Z × Std/Adv)
共通点: 3 runner の pages段は `eu.hook_run` → `er135_enduser_page_01.py:42 ASSET_DIR`(=`R.ASSET_BUILD_ID`=rev01-h)から出力。Std/Adv は同一ページ内の2レベルで同じ実装。
| 経路 | hookの入口(file:line) | 実走(runner CLI、code=origin/main rev01-h・data=既存run) | asset_build | Std/Adv click検査(PC+mobile) |
|---|---|---|---|---|
| X Std/Adv | er019_family_x_listening_page_01.py:262 | `er019 --slug ai_chat_sponsored_persuasion --run-name run_fx4_01 --web <scratch>` rc=0 TOTAL 270 NG0(`evidence_02/runner_x_final.log`) | rev01-h(scratch enduser/build_info.json) | std/adv×pc/mobile 各K 6項目+F click OK(K-OK=16, NG0) |
| Y Std/Adv | er121_family_y_runner_01.py:1388 | `er121 --slug surname_choice --run run_02 --mode real --approved-budget-jpy 1 --stages pages,page_verify --theme-package <surname_choice_package_01.json>` rc=0 TOTAL 268 NG0(`runner_y.log`) | rev01-h(run_02/pages/enduser) | 同上 |
| Z Std/Adv | er026_family_z_fiction_production_runner_01.py:2784 | `er026 --story yuki_onna --run run_yo_prod_01 --mode real --approved-budget-jpy 1 --stages pages,page_verify --pages-dir <scratch>` rc=0 TOTAL 264 NG0(`runner_z.log`) | rev01-h(scratch) | 同上 |
実走の補足: 各runのcost_log.jsonlは不変(Y run_02/Z run_yo_prod_01 = 17:49/17:46の最終書込のまま)=API 0。launch_gateで起動間隔≥150秒(`evidence_02/launch_times.txt`)。X moon(run_reselect_01)は assemble BLOCKED_STYLE_PROFILE_GATE、X untidiness/ai_chat は初回で `os.chdir(ROOT)`によりrun data(別worktree)が見えず失敗→環境shim(cwd固定)で解決(`runner_x_*_try*.log`)。Y初回は `--theme-package` 不足でSTOP(`runner_y_try1.log`、run状態は不変)。いずれも今回の変更起因ではない。

## 10項目検証表(原文§3)
8dir=X月・X②・X④・X⑭・Y再配達・Y姓・Zメロス・Z雪女。produce時Playwright(PC1280x900+mobile390x844 touch/`page.tap`)全NG0=`evidence_02/produce_<dir>.log`、live(Pages)全NG0=`evidence_02/live/live_<dir>.log`。
| # | 項目 | 結果 | 証拠(file) |
|---|---|---|---|
| 1 | 停止中クリック→英日点灯・再生なし | OK(play/seekingイベント0、paused維持、currentTime不変±0.05、onSent==[sid]、onJhl==[群]) | `K ...item1_click_while_stopped_lights_en_ja_no_play`(各produce/live log、`er135_enduser_page_verify_01.py:513-`)、F `sentence_click_does_not_play_or_seek` |
| 2 | 一時停止中クリック→位置不変・英日点灯 | OK | `K ...item2_click_while_paused_keeps_position_lights_en_ja` |
| 3 | 再生中クリック→シーク/中断なし | OK(seeking 0・pause 0・currentTime単調増加・paused false・sel None・次tickで自動ハイライトへ) | `K ...item3_click_while_playing_no_seek_no_interrupt` |
| 4 | 通常再生の英日同期 | OK(従来検査 F `highlight_follows_playhead`・J4全文走査・J6を維持) | produce/live log F・J |
| 5 | 再生/停止/一時停止/再開/シーク | OK(F `seekbar_moves_to_50pct`・`play_pause_button`・G境界・J5・M7 pause/resume) | produce/live log F・G・J |
| 6 | 非1対1・null群で誤点灯なし | OK(複数文1群の2文クリック=その群のみ、null群の文=英文のみ点灯・日本語0。M7 null群・J4) | `K ...item6_multi_sentence_group_and_null_group_no_false_light`、`J M7_null_group...` |
| 7 | PC・mobile | OK(同一検査をviewport 2種×touch tapで実行) | log先頭 `pc`/`mobile` 両行 |
| 8 | X/Y/Z×Std/Adv正式Production経路 | OK(上の6経路表。8dirのbuild_info.asset_build==rev01-h) | `runner_x_final/y/z.log`、`diff_gate_ech02_out.txt` |
| 9 | retry/fallback/regeneration/resume・pages再生成との整合 | OK(pages段再実行=ASSET_DIR同一asset。再produceはcache(ASR/embedding/translate)でAPI 0=Zの再translate 2呼出を除く。publish系: 本件は`produce`のdev dir直接再生成) | 同上、`produce_<dir>_result.json` |
| 10 | Regression/Validator/Integration | OK: er135_enduser_* 9本 309 + er136_nuance 25 = **334 PASS**(`evidence_02/unit_tests_er135_er136.txt`)、diff Gate 8dir OK(`diff_gate_ech02_out.txt`) | 同左 |

## 12必須項目(PRODUCTION_WIRED提案の充足表)
原文§3の10項目 + 同最終段の必須条件(正式runtime証拠/全対象経路/テストPASS/SSOT更新/Git反映/Fable独立受入)を再掲。
| 項目 | 状態 |
|---|---|
| 1-10(上表) | 全て充足(⑨を除く) |
| 11 正式runtime証拠・全対象経路 | 充足: runner X/Y/Z pages段実走+8dir再produce+live。**⑨ Metaは未配線**(下記) |
| 12 SSOT(CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS)+Git反映 | 充足(本commit)。**Fable独立受入は未実施** |
→ 提案: `PRODUCTION_WIRED_PENDING_FABLE`。⑨の再produceが完了するまで『全Family全記事への適用完了』とは呼ばない。

## End User URL(8dir、live確認済み)
https://shimomura055.github.io/eigo-radio/user_test/family_x_moon_shrinking_reselect_01/enduser/index.html
https://shimomura055.github.io/eigo-radio/user_test/family_x_untidiness_family_resource_01/enduser/index.html
https://shimomura055.github.io/eigo-radio/user_test/family_x_ai_chat_sponsored_persuasion_01/enduser/index.html
https://shimomura055.github.io/eigo-radio/user_test/family_x_jwst_mystery_emission_line_01/enduser/index.html
https://shimomura055.github.io/eigo-radio/user_test/family_y_production_redelivery_fee_03/enduser/index.html
https://shimomura055.github.io/eigo-radio/user_test/family_y_production_surname_choice_01/enduser/index.html
https://shimomura055.github.io/eigo-radio/user_test/family_z_melos_kphr_evidence_r3/enduser/index.html
https://shimomura055.github.io/eigo-radio/user_test/family_z_yuki_onna_01/enduser/index.html

## raw URL
https://raw.githubusercontent.com/shimomura055/eigo-radio/main/enduser_page_assets/rev01-h/app.js
https://raw.githubusercontent.com/shimomura055/eigo-radio/main/enduser_page_assets/derive_assets_01.py
https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er135_enduser_page_verify_01.py
https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er135_enduser_rules_01.py
https://raw.githubusercontent.com/shimomura055/eigo-radio/main/tools/ech02_diff_gate_01.py
https://raw.githubusercontent.com/shimomura055/eigo-radio/main/docs/pm/RESULT_PACKET_ECH02.md

## 原因仮説・観測・次の一手(QDC材料)
- 実装中に2件の自己是正: (a) 初回produceでF/J3/J3b/M7の click系16 NG(`produce_x_moon_try1_NG16_before_tick_fix.log`)=`selectSentence`が`highlight`のみで`__EUP`(tick更新)が古く`active==None`のまま(`M7_click_right_after_level_switch`の`active=None, onJhl=['14:0']`)。`tick()`経由に修正(J41、`selectSentence`内で`tick(); return;`)。(b) 選択がプログラム的seek(検証のJS `currentTime=`)後も残る問題 → `selTime`で「選択後に再生位置が0.3秒超動いたら解除」を追加(J39)。再実行でx_moon NG0。
- x_jwst 初回の1NG(`V adv_vocab_each_item_plays_own_audio_and_returns` mobile、end t=0)=Vocab音声検査側の既知競合(行364コメント: metadata未取得でのseek)で、2 Playwright並列時に発生。クリック非関連。単独再実行でNG0(`produce_x_jwst_try1_V_vocab_timing_NG1.log`)。
- 想定外: Zメロスadv_14・Z雪女std_11の各1段落は03B時点で訳不成立(英語のみ)だったが、再produceで既存retry(translate+verify各1回)が成立し、`ja_source=generated`の訳が付いた(約¥0.99、`tools/ech02_diff_gate_01.py`で2件のみと確認)。承認済み生成仕様(OPEN-618/03A)の範囲内=B。委任_04(照合NG段落の指摘付き再翻訳)とは別経路で独立に成立したため、委任_04側の反映計画と二重にならないか要確認。
- 次の一手: (1)⑨ Metaを別委任でrev01-hへ再produce(Fableが除外した理由=HR待ちは委任_10で解消済み、既にrev01-gで再produce済みのため今は旧クリック動作が残る。API 0)。改善見込み高(同手順で全dir NG0実績)。

## 判断候補(Fable向け。USER_DECISION_REQUIREDではない)
- ⑨ Meta除外の継続可否: 指示根拠=委任文「⑨はVocabulary音声Gate STOPPED中(HR待ち)」。事実=origin/main 43c5144f7(委任_10)で⑨はHR承認反映済み・rev01-g再produce済み・live NG0(5675d7781)。→ 分類 **B**(承認範囲内。ユーザー判断不要): 次委任で再produceするか、本委任の延長で今すぐ行うかのFable判断。私はauto mode判定の制約もあり、除外指示のまま未実施。
- Z2段落の生成訳(上記): 分類 **B**。許容でよいか、戻す場合は`git revert`でなく該当2 dirのarticle.json/build_infoをff84fdb7d^から戻して再produce(translate無効)が必要。
- 凍結`family_z_in_a_grove_01`: Fable確定どおり対象外(A既判断)。

## Charter 4行
1. 既存仕様整合: ユーザー原文 `docs/pm/delegation_log/2026-10-30_ENDUSER-CLICK-HIGHLIGHT-NO-SEEK-01_USER.md` §1(:A)・§3、DESIGN_01.md §0-§7、`er135_enduser_page_01.py:42`(ASSET_DIR)、`er135_enduser_rules_01.py:12,22`、runner hook(er019:262/er121:1388/er026:2784)、OPEN-618/624。
2. 未承認機能の既定値: 本件は全て APPROVED_FOR_PRODUCTION(原文§1 A)。flag/既定OFFの新機能はなし。確認=Grep `selectSentence`(rev01-h/app.js:304)、`ASSET_BUILD_ID`(rules:12)。
3. 失敗終了時の最終成果物: 失敗時はなし(全dirで produce rc=0、live NG0)。途中失敗の実例=X moon runner(assemble BLOCKED_STYLE_PROFILE_GATE)は新たな出力を書かず、公開dirも変更なし。**最終成果物の目的適合**: ユーザー原文『クリックで再生せず英日を確認する』を8dirで実装、ただし⑨は旧動作のまま(取り残し1件・上記)。設計準拠/test PASSは目的適合の根拠にしない: 実ブラウザ操作の実測(currentTime不変・play/seekingイベント0・paused維持)で確認。
4. 撤去・残置: 撤去=`seekSentence`関数とクリック経路の`syncKind !== 'none'`ガード(rev01-hのみ)、verify F `sentence_click_plays_from_sentence`(`sentence_click_does_not_play_or_seek`に置換)。残置=rev01-g/f/e(凍結dir・過去再現用)。Grep: rev01-h/app.jsに`seekSentence`0件、rev01-g/app.jsは残置(A9 testで検査)。

判定整合: 重大NG=なし / 主因=[なし] / 是正対象=[⑨ Meta再produce(次委任)] / STOP理由=[なし(stop_scope_check rc=0)] / 提示=可(⑨を除く8dir。⑨は取り残しを明記)
