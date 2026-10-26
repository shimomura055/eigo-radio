## 依頼種別

Opus独立技術レビュー(PM_GOVERNANCE 11-3 任意レビュー、Fable裁量)。対象=FAMILY-Y-STYLE-PROFILE-FIX-01 委任_01の設計(commit b633a612b)。read-only。結論は返信本文で(Fableが転記)。所要の目安20分、論点を絞る。

## 背景

OPEN-537: Family Y正式runner `er121_family_y_runner_01.py:37 STYLE_PROFILE="default"`固定により、承認済み共通Style profile `fx_20261017`(PD06/S3/E1/K2/P8-KP/P7)が実記事に適用されていなかった(承認側=設計台帳・DEV Trialは全て継承、`default`の承認・除外記録0件)。ユーザー緊急指示(原文=`docs/pm/delegation_log/2026-10-26_FAMILY-Y-STYLE-PROFILE-FIX-01_USER.md` §1): 原因究明・再発防止(定数修正で終わらせず正式初回経路のStyle確認と受入検証に組み込む)、正しいStyle適用(Voice 1〜3は人物別の声・主観性維持、PD06一律適用で個性を失わせない、Y固有承認Styleがあれば優先、未承認Style禁止)、再配達記事の影響音声のみ再生成・再提出。

## 読む物

1. `docs/research/FAMILY-Y-STYLE-PROFILE-FIX-01/OPUS_REVIEW_REQUEST_01.md`
2. 同dir `DESIGN_01.md`、`STYLE_MATRIX_01.md`、`PREVENTION_01.md`、`REGEN_PLAN_01.md`、`ROOT_CAUSE_01.md`(§Q2のみ)
3. 必要に応じ `er019_family_x_style_profile_01.py`(`resolve_run_profile`、Gate `m3_assembly_gate` 685-753、checked=[]でPASSになる695-696)、`er121_family_y_audio_01.py:354-363,590-605,703-726,798-815`、`er121_family_y_runner_01.py:30-40,960-1040`

## 論点(これだけ)

- P-1 **Voice 1〜3本文へのPD06適用**: 設計は「承認記録(A19『Voice別Styleは設けない』・T10・28-1運用7・USER_09)が全て適用で一致、Y固有承認Styleは0件、個性はPersona原稿+Voice名で担う」としてPD06適用(V1)を推奨。ユーザー原文「PD06を一律適用して個性を失わせない」との整合をどう見るか。PD06の定義(`fx_20261017`のPD06 prefix実文)を確認し、3人の主観的な語り口を平板化する内容か、承認済み範囲でV1が正しいか、V2(Voice本文だけdefault維持=新例外)を取るべき根拠があるかを判定。
- P-2 **fail-closed Gate設計**: 記録欠落/不一致/非承認profile/checked空/role未カバーをBLOCKにする設計が、正常なresume・regenerate・chunk経路・LR再TTS・KP経路(Style不変部位)で誤BLOCKを起こさないか。`audit/style_actual_vs_approved.json`の照合キー(実送信prefix vs 承認prefix sha)が、発音hint付与・Std減速・Fallback ③(別Style)で偽陽性にならないか。並行実装中のTTS統一(er127: 採用attemptの`style_prefix`をtop-level正規化、Adv ③=短文Style)との整合。
- P-3 **再生成範囲**: 33 take(Adv 15/Std 18)の過不足。Style不変5 clip(Adv topic_intro/comment_1/comment_3、Std topic_intro/japanese_title)を再生成(案R、約2.5円)するか既存`--reuse-manifest`等で再利用できるか(新機構を作らない前提)。Voice 2/3(Zephyr/Schedar)もPD06適用で`_tts_input_sha`が変わるため再生成必須という理解は正しいか。
- P-4 **再発防止の十分性**: (a)Y Gate fail-closed、(c)(d)AST test・drift test、Gate 7受入への実測照合表追加、で「Family新設時に共通仕様表の配線漏れを機械検出」できるか。X/Z側の`checked=[]`PASSの穴(695-696)を共通helperで塞ぐべきか(影響範囲)。

## 出力形式

1. 結論(GO / GO with changes / NO-GO)+理由3行
2. P-1〜P-4の判定表(妥当/要修正、根拠ファイル:行、必須修正M-番号/推奨R-番号)
3. 見落としリスク
4. 5行要約

推測で断定しない。未確認は未確認と書く。