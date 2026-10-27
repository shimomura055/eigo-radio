# AI-ISLAND-FORM-PRODUCTION-01 ユーザー指示原文(2026-10-27、逐語、委任_02の「ユーザー指示(原文・逐語)」節から保存)

# Claude Code指示｜Family X「AIの仮想の島」Std/Adv選定確定＋文法選定仕様変更・Production Wiring

## 1. 目的とユーザー正式決定

今回の指示は、次の3件を一体で進めるものです。

1. 「AIの仮想の島」StandardのKey Phrase／Key Word選定10件を正式確定する。
2. 同記事AdvancedのKey Phrase／Key Word選定10件を正式確定する。
3. 文法の新しい選定仕様をFamily X/Y/Zの全6経路に正式採用し、Production Wiringまで完了する。

**記事本文は既存の承認済み本文を再利用し、再生成しない。**

両レベルの文法は、新仕様のフォームで再選定するため、現時点では未確定として管理する。

### Status

- Std/AdvのKey Phrase／Key Word：USER_CONFIRMED。後続工程への正式反映対象。
- 文法新仕様：APPROVED_FOR_PRODUCTION。
- 文法のユーザー選定：Std/AdvともUSER_DECISION_REQUIRED。
- 文法新仕様の到達目標：PRODUCTION_WIRED（全6経路）。
- AI島完成記事：ユーザー最終試聴待ちまで進め、最終承認を受けてCloseout。

## 2. Standard｜確定内容

記事：`ai_island_temple`  
Level：`a2`  
本文SHA256：`76f80f62120b57835150b1fc35d590c0b848926ce219ecb27105f2414d376599`  
候補集合SHA256：`25a7bce9357cdaaaf58207e179fd187e97f77e0c5f30c4b511ec933bd51d028a`

候補元：
`er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_kp75_ev_01/a2/key_phrases/kp_candidates.json`

### ① Key Phrase（3件）

| 英語 | 確定日本語訳 | candidate_id |
|---|---|---|
| carry over | 持ち越す | p_1a2370a6af |
| take a detour | 寄り道をする | p_1473453d19 |
| card to play | 使える手 | p_289a665236 |

### ② 追加解説（2件）

| 英語 | 確定日本語訳 | candidate_id |
|---|---|---|
| worth paying attention to | 注目する価値がある | p_1cf1329364 |
| obstacle | 障害物 | p_d17f8079e3 |

### ③ 本文意味表示（5件）

| 英語 | 確定日本語訳 | candidate_id |
|---|---|---|
| make a difference | 影響を与える | p_801113c17d |
| separately | 個別に | p_dc8803926c |
| feature | 性質 | p_4b7615dce5 |
| Strategy | 作戦 | p_31e10e6357 |
| setup | 設定 | p_80437a44a6 |

本文表層形の対応を維持する。

- carry over → carried over
- take a detour → taken a detour
- make a difference → made a difference

文法：旧フォームで0件選択。ただし今回の仕様変更により**文法のみ再選定待ち**。0件として最終確定しない。

自由コメントなし。

## 3. Advanced｜確定内容【今回追加】

記事：`ai_island_temple`  
Level：`b1b`  
本文SHA256：`00f14092c072d9aa208778dbc1aa1b5d715262cc77b4e5420acae6c0bffca324`  
候補集合SHA256：`5d8c1b12f01b0de9265721152da508e7f8f7afb1f7f126d5d461a835457d87f9`

候補元：
`er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_kp75_ev_01/b1b/key_phrases/kp_candidates.json`

### ① Key Phrase（3件）

| 英語 | 確定日本語訳 | candidate_id |
|---|---|---|
| carry over | 次に持ち越す | p_1a2370a6af |
| call on | 頼む | p_ad091fb295 |
| take a detour | 遠回りをする | p_1473453d19 |

### ② 追加解説（2件）

| 英語 | 確定日本語訳 | candidate_id |
|---|---|---|
| card to play | 打てる手 | p_289a665236 |
| obstacle | 障害物 | p_d17f8079e3 |

### ③ 本文意味表示（5件）

| 英語 | 確定日本語訳 | candidate_id |
|---|---|---|
| look at separately | 別々に検討する | p_8f3df24cb8 |
| exploration | いろいろ探ること | p_0d5feb1964 |
| technique | やり方 | p_b41c6aff6d |
| overlook | 見過ごす | p_1b8ee344f0 |
| erase | 消し去る | p_4513a423ab |

本文表層形の対応を維持する。

- carry over → carried over
- call on → called on
- take a detour → taken a detour
- look at separately → looked at separately
- erase → erased

文法：旧フォームで0件選択。ただし今回の仕様変更により**文法のみ再選定待ち**。0件として最終確定しない。

自由コメントなし。

## 4. ユーザー確定内容の保存・保護

両レベルとも以下が確定している。

- ① Key Phrase：3件
- ② 追加解説：2件
- ③ 本文意味表示：5件
- 合計10件
- 日本語訳：全件official

**英語表現、日本語訳、①②③区分、candidate_idを変更しない。**

StandardとAdvancedで同じ英語表現の日本語訳が異なる場合も、今回確定したレベル別の訳をそのまま保持する。

候補ID、本文SHA、候補集合SHAを元データと照合し、不一致があればfail-closedとする。

今回のフォーム結果で送付された `production_connected: false` は、ユーザーの選定結果がまだProductionに接続されていないことを示す。保存だけで正式反映完了と誤認しない。

AI選定理由は参考情報であり、ユーザー確定コンテンツには含めない。

既存のHuman Review記録との整合を確認する。OPEN-526の旧PENDING結果は、確定済みデータを破壊しない方法で引き継ぎ・整理する。

後続のretry／fallback／regeneration／resumeで、確定内容を再生成・変更・上書きしない。

## 5. 文法選定仕様の正式変更【全Family共通】

対象：Family X/Y/Z × Standard/Advanced。

新仕様：

1. AIが文法候補を評価して順位付けする。
2. **ユーザーにはTop 1・Top 2の最大2件のみ提示する。**
3. 表示順はAI評価の順位順（Top 1 → Top 2）。
4. 各候補の文法名と、エンドユーザー向け解説全文を選定前に表示する。
5. **ユーザーは原則1件を選ぶ。**
6. 適切な候補がない場合、0件も選択できる。
7. 2件同時選択は禁止。
8. 確定した文法名・解説全文は後続工程で変更しない。

候補が1件しかない場合は1件、0件の場合は0件を提示する。数合わせのための候補追加は行わない。

既存のTrial-08選定方式・品質基準を尊重し、今回承認された選定数・表示数の変更以外を独断で変更しない。

### 事前生成との整合

別途正式承認済みの「選定前に文法解説全文を生成する」方式を維持する。

AI評価Top 1・Top 2が特定できた後に、その2候補の解説全文だけを生成する方式が合理的であれば採用し、不要なAPI費用を削減する。ただし既存の品質仕様・Trial-08選定方式との整合を必須とする。

ユーザーが選んだ解説全文を後から生成し直すことは禁止。

### 旧仕様の整理

旧「文法最大2件を選定可能」という制約を新仕様に置換する。

対象には以下を含める。

- V3フォームのUI・選定状態・件数表示
- フォーム送信内容・schema・Validator
- 文法Human Review
- 確定保存データ
- 文法finalize
- 組立・公開表示
- retry／fallback／regeneration／resume
- CURRENT_SPEC・関連テスト・既存の旧規則参照

文法解説の公開対象は、承認済みどおり**X/Y/ZのStandard／Advancedすべて**とする。

## 6. AI島の文法再選定

現在のV3フォーム：

https://shimomura055.github.io/eigo-radio/user_test/selection_form_v3/

Standardは旧フォームで文法4候補、Advancedは3候補が提示されていた。

新仕様では、各レベルのAI評価Top 1・Top 2だけを提示する。

### 必須対応

- Standardの①②③確定済み10件を保持。
- Advancedの①②③確定済み10件を保持。
- **両レベルとも文法のみ再選定**できる状態にする。
- 文法名＋解説全文を表示する。
- Top 1・Top 2の順位を明示する。
- 0件／1件の選定のみ許可。
- 旧フォームで文法0件だったことを、新フォームでの確定0件として引き継がない。
- 新フォームからの送信内容が、既存の確定済み10件と矛盾しないようにする。

**ユーザーにKey Phrase／Key Wordの20件を再選定させないこと。**

修正したフォームで、Standard／Advancedの文法をまとめて選定できる状態にする。

再提出時は、両レベルのTop 1・Top 2を文法名・解説全文付きで提示し、ユーザーには文法選定だけを依頼する。

## 7. AI島の完成記事制作

Standard／Advancedの文法選定をユーザーから受領したら、確定内容をそのまま正式制作工程へ反映する。

- 既存本文を再利用する。
- Key Phrase／Key Wordの①②③を正確に反映する。
- 文法0件なら追加しない。1件なら確定解説全文をそのまま公開する。
- 必要な音声だけ生成し、既存の有効な音声を再利用する。
- 承認済みTTS Style、Voice、Chunk、ASR品質Gateを維持する。
- Human Reviewが必要な場合は承認済み手順で処理する。
- 通常のStandard／Advanced最終試聴ページを公開する。

ユーザーの最終試聴PASSまでは完成記事の最終受入としない。

## 8. Production Wiringの受入条件

文法の新仕様を全6経路で検証する。

- 正式初回Production経路でTop 1・Top 2のみ提示。
- AI評価順位と表示順が一致。
- 解説全文の事前生成と表示が正常。
- 0件／1件の選定が可能で、2件選定を拒否。
- 確定内容が後続工程で完全一致。
- Standard／Advanced双方の公開ページに正しく反映。
- retry／fallback／regeneration／resumeとの整合。
- 必須Regression／Validator／Integration Test PASS。
- 実runtimeでの発火証拠。
- actual model_id、routing、Prompt／Style等の証拠。
- Fable独立受入。
- CURRENT_SPEC／DECISION_LOG／OPEN_ITEMS更新。
- Git反映。

Family別・レベル別にStatusを判定し、証拠のない経路をPRODUCTION_WIREDとしない。

既に完了している別案件の文法事前生成・確定内容保護との実装競合を避け、重複作業をしない。

## 9. QCD・進行方針

優先順位：**品質 ＞ Delivery ＞ 量産単価 ≫ 開発費用**

- 不要な本文再生成・KP再選定・重複API呼出しを行わない。
- 確定済み20件を再利用。
- 文法の新仕様への変更と全Family配線を、既存作業との依存関係を考慮して並列化。
- ユーザーが文法選定を行える状態を優先的に準備する。
- 文法の選定待ち中も、確定済み内容の保存・非競合作業は進める。
- 開発費1,000円／日（JST）および個別承認枠内で実施。
- 不具合は承認済み範囲で自律解決。
- 未承認仕様変更、重大な品質問題、blocker、予算超過はSTOPして報告。

## 10. 次の報告

### 第1報｜文法選定待ち

1. Standardの文法Top 1・Top 2（文法名＋解説全文）
2. Advancedの文法Top 1・Top 2（文法名＋解説全文）
3. 修正後V3フォームURL
4. 両レベルのKP／KW計20件が確定保存され、変更されていないこと
5. ユーザーが文法だけを選定する方法

### 第2報｜完成記事提出

1. Standard／Advanced最終試聴URL
2. KP／KW計20件と文法確定内容の一致結果
3. 音声・公開品質Gate結果
4. 実費・作業時間・量産単価への影響
5. Fable受入・Git／SSOT・残Open Item
6. 文法新仕様のX/Y/Z全6経路Production Wiring Status

**最優先の到達点は、両レベルの確定済みKP／KWを保持したまま、文法だけ新仕様でユーザーに選んでもらえる状態にすること。その後、AI島の記事完成と、全Familyへの文法新仕様Production Wiringを確実に完了することです。**

(原文ここまで)
