# RESULT_PACKET_CNT_01 — SELECTION-UI-OCCURRENCE-COUNT-01 委任_01(2026-10-31、OPEN-632、設計・精度検証のみ)

Status=**設計中**(Production未変更・コード配線0・UI変更0・API 0円)。Opus条件Aレビュー前。詳細=docs/research/SELECTION-UI-OCCURRENCE-COUNT-01/{CURRENT_STATE_01,DESIGN_01,PRECISION_01}.md、証跡=同evidence/、試作=同tools/。
結論: 回数は選定フォーム生成時に決定論で数えてmember data JSONの各entry `occurrence` に焼き込む(難易度表示と同型・API 0)。確定=完全一致/活用形/人称スロット(閉集合)/句動詞の間が代名詞1語、保留(加算しない)=名詞句スロット・名詞句が間・前置詞かもしれない分離・活用済み語の他活用形。多義の判別はしない。
実測(既存batch 27 member・253項目、6水準X/Y/Z x Std/Adv): 確定335/保留3、誤カウント0(複数回出現41項目の全ヒット+非exact全件を全文確認)、取りこぼし0(緩い基準45行を人手分類)、旧occurrence_countとの不変条件251/253(不一致2=`surname_choice adopted`、intro patchで本文が変わった旧記録の陳腐化)、公開enduser 20ページ195項目でStory/In One Line一致100%、ユーザー指定5表現は本文grepの正解と全件一致(31件)、単体test 30件PASS。
原因仮説・根拠・前回差分・次の一手(QDC材料): 初回は`campaign's`と`In One Line`が不変条件で不一致(所有格's/X article.md末尾にIn One Line)->規則修正で解消。次の一手=Opus条件Aレビュー(論点10件=DESIGN_01 §8)->集計規則のユーザー承認->委任_02(実装: 集計module昇格+exporter統合 || form_logic.js/index.html表示を並列、約3〜3.5h、API 0円)。改善見込み=高(設計は実データで検証済み)。
(1) 既存仕様整合: `export_form_data_01.py:160-183,252-306`(entry/convert、`difficulty`同型の参考情報 :149-158,172)、`er105_kp_fulltext_selector_01.py:157-186,274,629-660,742,826-866`(語境界・occurrence_count・活用表を読み取り再利用)、`er138_kp_n5_generalization_01.py:1355-1387`(N5: used_form=N5形/source_span無変更)、`form_logic.js:100-108,276,321,402`(validateArticleは未知キー許容・doneSig/makeCodeはdata sha6を含む=後付け禁止)、`index.html:151-170`、`publish_selection_batch_01.py:174`(公開済みid不変)、runner stage順 X`er019...runner:970-997`/Y`er121...runner:34`/Z`er026...runner:1234`(support->kp)。
(2) 未承認機能の既定: 本委任はコード配線なし(既定値の変更0)。実装時の方針=集計規則のユーザー承認までexporterは`--with-occurrence`明示指定のみ・テストbatchのみ(Grep対象: `with-occurrence`は現状0件)。
(3) 最終成果物: 失敗終了なし(設計・検証の正常完了)。path=docs/research/SELECTION-UI-OCCURRENCE-COUNT-01/ 配下(上記3文書+tools/+evidence/)。ユーザー原文§4の目的(学習者が回数を信頼して選べる)に対し、本委任の到達点は「規則設計+既存データでの精度実証」まで。表示・配線・公開URL実操作(受入7)は未実施=完了表現は「設計中」(PRODUCTION_WIREDではない)。
(4) 撤去・残置: 撤去した規則/検査/test=なし(新規追加のみ)。新規識別子=`occurrence_count_01.py`(rule `occ-v1`)、`occurrence_count_01_test_01.py`(30件)。残存Grep: Production経路(`export_form_data_01.py`/`form_logic.js`/`index.html`)に`occurrence`は0件(未配線)。旧`item.occurrence_count`(er105/ハイライト用)は無変更で残置。
判断候補: (a) 集計規則occ-v1(確定/保留の線引き・スロット語集合)のユーザー承認 = 分類D(受入条件4『承認した集計規則』= docs/pm/delegation_log/2026-10-31_LEARNING-ITEM-QUALITY-TRIO-01_USER.md:196。規則は未承認)。(b) Title別枠表示 = 分類B(承認範囲内の表示最適化、原文「見やすさを優先して最適化してよい」)で自己解決済み、Opus論点7。他は判断候補なし。
判定整合: 重大NG=なし / 主因=なし / 是正対象=なし / STOP理由=なし / 提示=不可(Opusレビュー・規則承認前の設計)。
環境メモ: C:ドライブ空き0.8GB(100%使用)のためworktreeは sparse-checkout(必要dirのみ)で作成。git push前にfetch->ff-merge済み。
