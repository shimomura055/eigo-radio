# OPUS_REVIEW_REQUEST_05: 2課題(①Std字義訳・②見出し語人称placeholder)包括対策のOpus独立レビュー依頼(条件A: 新しい構造・処理フローの設計)

管理ID: FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01 委任_13 / 2026-10-23 / 依頼元: Fable(本書は実行層Sonnetが作成した依頼文案)
レビュー対象: `ROOT_CAUSE_03.md`(原因)・`DESIGN_05.md`(設計)。Production変更0・API 0の設計段階。判断基準は`docs/pm/PM_GOVERNANCE.md` 11-3(条件A)。
前提資料: `AUDIT_01/AUDIT_SUMMARY_01.md`・`FABLE_VERIFICATION_01/02.md`(NG分類の訂正: 所有者誤り3件はNGから外れ、見出し語の人称placeholder不整合へ)・`ROOT_CAUSE_02.md`・`TRIAL_RESULT_02/03.md`・`OPUS_REVIEW_03/04.md`・`WIRING_DESIGN_01/03.md`。
ユーザー要件(USER_06): 2課題を実際に解消する/個別対策禁止/X・Z共通/既存の正しいKPを壊さない/不要なLLM工程を避け速度・単価を最適化/既存Promptの微修正に固執しない/未承認仕様のProduction Wiring不可。

## 依頼する論点(それぞれ「妥当/要修正/不採用推奨」と理由を)

### 論点1: 原因の十分性(ROOT_CAUSE_03)
1. ②: 「指示対象の判定工程・規定の欠落(許可表と選択の分離)」で、Trial_01 arm間の揺れ(同一入力でone's/someone's/無変更)と`apply its findings→one's`を説明しきれているか。他の原因(A-1のarm差、temperature、記事内の表現の頻度)の見落としは。
2. ①: 「字義/慣用判定を誰も検査していない+稀なKP群で再現確率が高い(希釈)」という説明は十分か。事後層別(G0 4/7対G3 0/7)の選択バイアスの扱いは妥当か。Std gloss callの「全語を反映」という指示(`er003_key_words_gloss_alignment.py:585-586`)が字義訳を誘発する寄与は、G1(除去でも直らない)の結果から否定されたと見てよいか。
3. 29件(ラベル=実行層の目視、REFに根拠)と66KP(Std独立KP)という標本の小ささに対し、結論の強さは適切か。

### 論点2: ②の設計(`possessor_role`先行判定+決定論写像/修復)
1. role4値(none/self/other_person/non_person)の定義は網羅的か。曖昧ケース(擬人化主語の所有格=self扱い、組織・集団の`their`、総称の`you`、受動態の主語、`our`の話者側、`turn X on its head`のように目的語を指す`its`)で誤写像しないか。non_personを「原形のまま」にする倒し方は妥当か。
2. 修復(roleに合わせてトークン1個を決定論で書換え)は、既存の「LLM出力の自由文補正禁止」の思想と矛盾しないか(選定段のParseError方針との整合)。INVALID→retryにする方が良いか(retry枠・STOPリスクとのトレードオフ)。
3. 許可表の変更(`my`・`our`にother_personの`someone's`を追加)の副作用: `er003_key_words_gloss_alignment.py:167,243`・`er105_kp_fulltext_selector_01.py:676`への波及と、人称整合検査(`:205-228`)との整合。
4. A-1(規則5)との同梱: 同一テンプレートへの`_EDITS`連結とdrift guard、規則3追記が人称語を含まない項目の出力を変えるリスク。
5. 追加call 0・単価+0.005円/記事以下という見積は妥当か。

### 論点3: ①の設計(独立再読検査+該当itemのみ再生成)
1. 検査の偽陽性/偽陰性: 検査モデル(luna)が自らの生成物と同じ盲点を持たないか(独立性の実効)。`literal_image_only`のみをflagする設計の再現率の見込み。「日本語として確立した慣用句はsame_meaning」という一般基準が、`draw a line→一線を引く`型の正しいKPを偽陽性にしないか。
2. 再生成のattempt上限(既存の2)内で、flag項目がattempt 2も字義のままだった場合の扱い(attempt 1採用+WARN、STOPなし)と、検査call失敗時のfail-open(スキップ)は、既存retry/fallback/Gateの迂回に当たらないか。品質検査を「止めない」設計の妥当性。
3. 代替(C'=同一call自己監査、B=G3系の構造変更、D=Sol全面切替)との優劣判断は妥当か。C'で十分なら追加call 0を優先すべきか。
4. Std/Adv用法整合チェック(案A)を不採用とした理由(a2にAdvが無い、B仕様変更、共有で悪化=E3)は妥当か。見落としはないか。
5. a2とb1bのgloss生成単位が別callである場合の検査call数(記事あたり最大2回)と単価見積。

### 論点4: B仕様(Adv)への影響
Adv Prompt・schema・`PROMPT_SHA256`(`er019_family_x_kp_explanation_01.py:142`)は両課題とも不変という整理は正しいか。glossまたは見出し語が変わった項目のAdv再生成は既存signature(X `:1073-1086`、Z `:1517-1528`)で連鎖し、仕様ID追加は不要という整理は正しいか。

### 論点5: X/Z共通性・Store reuse・既存KP非劣化
1. X/Z・a2/b1bで同一モジュールを通ること(`er003_v1_n3_01_scaffold_generate.py:524-532`)の確認と、Zの永続化済みartifact人称整合修復経路への影響なし(新規生成のみが対象)の確認。
2. 非劣化の測り方(未flagはバイト同一、人称語なし項目は2rep間ノイズ基準)は十分か。既存の完成記事は自動では変わらず、KP stage再実行時のみ新方式、という整理で良いか。
3. Store reuse(TTSはText+Style一致でreuse)に仕様IDを入れない判断。

### 論点6: 費用・検証計画(DESIGN_05 §5)
上限60円(見込み約37〜39円、最大約54円、KP案件累計≈170円→≈224円)の内訳と、層別設計(結果に依らないF/N層)、事前宣言基準(F層字義訳NG≤B0の1/3、新規悪化≤1%、追加費用≤0.15円/記事)、検出力(F層90KP×2rep)の妥当性。Fable盲検の負荷(同一文字列は1回採点)。

### 論点7: 見落とし・重大リスク
本設計が見落としている原因、導入によって生じうる新規の品質悪化(薄化・過剰再生成・費用)、または既存承認済み仕様との矛盾があれば指摘。

## レビュー出力に求める形式
各論点ごとに: 判定(妥当/要修正/不採用推奨)・根拠(file:lineまたはデータ)・修正案。末尾に「Trial実施可否(可/条件付き可/不可)」と、Trial前の必須修正(MF-xx)と任意(OF-xx)の一覧。
