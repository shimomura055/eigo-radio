# FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01 委任_02 報告(2026-10-12)

範囲: 手順1〜3前半(ユーザー正式決定5項目のSSOT記録・既存仕様との衝突整理・実装設計書)。コード/Prompt/Routing変更なし、有料API 0、追加費用JPY0。Opus独立レビュー(条件A)前。

## 1. 何をしたか
- SSOT記録(追記のみ、CRLF維持): `DECISION_LOG.md`(同日エントリ)、`CURRENT_SPEC.md` Family Z節(「2026-10-12決定による整理」、Z-3=Family Zでsuperseded、名前検査=superseded、レベル設計、Style採用範囲[Coffee限定承認と区別]、費用上限JPY300)、`OPEN_ITEMS.md`(OPEN-297更新、OPEN-185追記、新規OPEN-302/303)、`docs/pm/REPORT_LEDGER.md`。
- 衝突整理: `er060_output/melos_production_e2e_01/CONFLICT_RESOLUTION_01.md`(決定で解消=A表8件、技術未解消=B表16件)。
- 設計書: `er060_output/melos_production_e2e_01/IMPLEMENTATION_DESIGN_01.md`((a)〜(j)、各項に問題/変更/改善/リスク)。

## 2. 設計上の重要所見(再利用による重複回避)
- X既存の「Advanced→Standard」機構はIOL節保持を要求するためそのままは不可。共有ブロック再利用のZ専用Promptを提案。
- X B1 Comment1/2/3(Comment3=Part2-3間のBridge)は決定①のCommentx3配置と一致、無改変再利用可。Comment4のみ不使用。
- Dialogue clipは従来系の既存関数(`generate_voice_body_wide_margin`系)で決定④と一致。
- Connected Speech用IDは`er020.resolve_narrative_role`への後方互換正規表現1行を推奨(Secondary ASR層がsegment_idで再解決するためZ側aliasでは不足)。
- Validator: 決定論層+LLM判定層(gpt-6-luna、Writer=Solと別系統)の2層。F1〜F8の固定fixtureRegression、実呼出calibration 6件(約JPY2)を推奨。

## 3. Fable確認事項(USER_DECISION_REQUIREDではなく解釈確認)
1. OPEN-297「Z TTS/AssemblyはX音声仕様Fixまで保留」を本決定で解除と解釈してよいか(設計は解除前提)。
2. Advanced語数範囲(400〜560語)・Standard範囲・3分割検証値は未承認の提案(OPEN-302)。
3. Coffee evidence内の「R2」と「P2」表記不一致は実装時にsha照合(OPEN-303)。
4. 委任文の「Z-1〜Z-9」はSSOT上Z-1〜Z-4のみ存在(Z-5〜9は検索0件)。
5. Opus条件A対象: Story 3分割の境界決定方式、Validator構造、er020共有編集、Role style定数表。

## 4. 費用概算
中央約JPY125〜175、上振れ約215〜245(上限JPY300、JPY200で警告)。内訳は設計書(i)。

## 5. Status
設計完了・SSOT記録済・実装未着手。PRODUCTION_WIREDではない。次工程=Opus独立レビュー(条件A)→Fable照合→実装。
