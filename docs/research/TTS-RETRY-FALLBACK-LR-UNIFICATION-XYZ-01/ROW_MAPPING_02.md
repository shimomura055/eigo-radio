# ROW_MAPPING_02 — Fallback・LR適用一覧(正式8区分・47行)

管理ID: FZ-DIALOGUE-LR-ADOPTION-01 委任_02 / 2026-10-29 / 正本=`ROW_MAPPING_02.json` / 旧=`ROW_MAPPING_01.md`(履歴)

ZセリフLR正式採用(APPROVED_FOR_PRODUCTION 2026-10-29、原文§4)により、正式一覧は8区分に整理した。旧49行から`Z-A2-DIALOGUE-LEGACY`/`Z-B1B-DIALOGUE-LEGACY`の2行(独立行)を外し、`Z-*-DIALOGUE-CTX`はLRあり・最大TTS6回・待機2回へ更新した。**従来Dialogue Styleそのものは撤去しない**(③⑥のFallbackとして現役。policy=legacy[既存run・承認済みロールバック]の互換定義は`er127.PROFILES['Z_DLG_LEGACY']`と`ROW_MAPPING_02.json`のcompat_rowsに残置)。

## 正式8区分

| # | 対象 | 3回目のFallback Style | LR | 最大TTS | policy |
|---|---|---|---|---|---|
| 1 | X/Y/Z Standard 英語本文・Voice等 | 英語短文Style(Minimal) | ○ | 6回 | EN_LR_STD |
| 2 | X/Y/Z Advanced 英語本文・Voice等 | 英語短文Style(Minimal) | ○ | 6回 | EN_LR_ADV |
| 3 | Zセリフ・文脈感情方式(Std/Adv) | 従来Dialogue Style | ○ | 6回 | Z_DLG_CTX |
| 4 | X/Y/Z 日本語音声 | 日本語短文Style(Minimal) | × | 3回 | JA_STD |
| 5 | X/Y/Z Key Phrase英語(Std/Adv) | ENGLISH_LOCK(3・4回目) | × | 4回 | KP_EN |
| 6 | X/Y/Z Advanced KP英語解説音声 | 英語短文Style(Minimal) | × | 3回 | KP_EXPL |
| 7 | X/Y/Z 英語固定案内音声 | 通常Styleのまま | × | 3回 | SHELL_EN |
| 8 | 固定MP3(Family Y) | なし | — | 0回 | NO_TTS |

## 行別(47行)

| ID | family | level | policy | 最大TTS | 待機 | LR |
|---|---|---|---|---|---|---|
| X-S01 | X | Std | EN_LR_STD | 6 | 2 | あり(最大1回) |
| X-S02 | X | Std | JA_STD | 3 | 1 | なし |
| X-S03 | X | Std | JA_STD | 3 | 1 | なし |
| X-S04 | X | Std | EN_LR_STD | 6 | 2 | あり(最大1回) |
| X-S05 | X | Std | EN_LR_STD | 6 | 2 | あり(最大1回) |
| X-S06 | X | Std | EN_LR_STD | 6 | 2 | あり(最大1回) |
| X-S07 | X | Std | KP_EN | 4 | 1 | なし |
| X-A01 | X | Adv | EN_LR_ADV | 6 | 2 | あり(最大1回) |
| X-A02 | X | Adv | EN_LR_ADV | 6 | 2 | あり(最大1回) |
| X-A03 | X | Adv | EN_LR_ADV | 6 | 2 | あり(最大1回) |
| X-A04 | X | Adv | EN_LR_ADV | 6 | 2 | あり(最大1回) |
| X-A05 | X | Adv | EN_LR_ADV | 6 | 2 | あり(最大1回) |
| X-A06 | X | Adv | EN_LR_ADV | 6 | 2 | あり(最大1回) |
| X-A07 | X | Adv | KP_EN | 4 | 1 | なし |
| X-A08 | X | Adv | KP_EXPL | 3 | 1 | なし(現行どおり。新設しない) |
| X-A09 | X | Adv/Std | SHELL_EN | 3 | 0 | なし |
| Y-S-01 | Y | Std | SHELL_EN | 3 | 0 | なし |
| Y-S-01b | Y | Std | JA_STD | 3 | 1 | なし |
| Y-S-02 | Y | Std | EN_LR_STD | 6 | 2 | あり(最大1回) |
| Y-S-03 | Y | Std | JA_STD | 3 | 1 | なし |
| Y-S-04 | Y | Std | JA_STD | 3 | 1 | なし |
| Y-S-05 | Y | Std | EN_LR_STD | 6 | 2 | あり(最大1回) |
| Y-S-06 | Y | Std | EN_LR_STD | 6 | 2 | あり(最大1回) |
| Y-S-07 | Y | Std | EN_LR_STD | 6 | 2 | あり(最大1回) |
| Y-S-08 | Y | Std | KP_EN | 4 | 1 | なし |
| Y-S-09 | Y | Std | JA_STD | 3 | 1 | なし |
| Y-B-00 | Y | Adv | NO_TTS | 0 | 0 | — |
| Y-B-01 | Y | Adv | SHELL_EN | 3 | 0 | なし |
| Y-B-02 | Y | Adv | EN_LR_ADV | 6 | 2 | あり(最大1回) |
| Y-B-03 | Y | Adv | EN_LR_ADV | 6 | 2 | あり(最大1回) |
| Y-B-04 | Y | Adv | EN_LR_ADV | 6 | 2 | あり(最大1回) |
| Y-B-05 | Y | Adv | EN_LR_ADV | 6 | 2 | あり(最大1回) |
| Y-B-06 | Y | Adv | EN_LR_ADV | 6 | 2 | あり(最大1回) |
| Y-B-07 | Y | Adv | KP_EN | 4 | 1 | なし |
| Y-B-08 | Y | Adv | KP_EXPL | 3 | 1 | なし(現行どおり。新設しない) |
| Z-A2-NARR | Z | Std | EN_LR_STD | 6 | 2 | あり(最大1回) |
| Z-A2-DIALOGUE-CTX | Z | Std | Z_DLG_CTX | 6 | 2 | あり(最大1回。2026-10-29 ZセリフLR正式採用) |
| Z-A2-TOPIC | Z | Std | EN_LR_STD | 6 | 2 | あり(最大1回) |
| Z-A2-JA | Z | Std | JA_STD | 3 | 1 | なし |
| Z-A2-KPEN | Z | Std | KP_EN | 4 | 1 | なし |
| Z-A2-KPJA | Z | Std | JA_STD | 3 | 1 | なし |
| Z-B1B-NARR | Z | Adv | EN_LR_ADV | 6 | 2 | あり(最大1回) |
| Z-B1B-DIALOGUE-CTX | Z | Adv | Z_DLG_CTX | 6 | 2 | あり(最大1回。2026-10-29 ZセリフLR正式採用) |
| Z-B1B-TOPIC | Z | Adv | EN_LR_ADV | 6 | 2 | あり(最大1回) |
| Z-B1B-PREVCOM | Z | Adv | EN_LR_ADV | 6 | 2 | あり(最大1回) |
| Z-B1B-KPEN | Z | Adv | KP_EN | 4 | 1 | なし |
| Z-B1B-KPEXPL | Z | Adv | KP_EXPL | 3 | 1 | なし(現行どおり。新設しない) |

## 互換(正式一覧外)

| ID | policy | 用途 |
|---|---|---|
| Z-A2-DIALOGUE-LEGACY | Z_DLG_LEGACY | policy=legacy(既存run・承認済みロールバック)の互換定義。正式一覧の独立行ではない |
| Z-B1B-DIALOGUE-LEGACY | Z_DLG_LEGACY | policy=legacy(既存run・承認済みロールバック)の互換定義。正式一覧の独立行ではない |
