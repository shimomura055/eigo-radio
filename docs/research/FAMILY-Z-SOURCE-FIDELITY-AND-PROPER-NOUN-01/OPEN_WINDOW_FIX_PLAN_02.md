# OPEN_WINDOW_FIX_PLAN_02: 『開いた窓』結末補完の修正方針(最小構成・決定論的パッチ。設計のみ、未実施)

管理ID: FAMILY-Z-SOURCE-FIDELITY-AND-PROPER-NOUN-01 委任_02 / 2026-10-23 / API 0
位置づけ: OPEN_WINDOW_FIX_PLAN_01.md(§1現行本文確認の対応表・§4費用根拠)は履歴として有効。本書は改訂(OF-FZSF-M08・S06〜S09)反映の現行版。Production音声・本文・Promptは**無変更**。実施はU2(保留解除)とOPEN-462配線確定後。
対象: `er026_output/family_z_production_e2e_01/the_open_window/run_e2e_01/`。

## 1. 最小構成(Fable決定・推奨。Veraは既定で含める=S06)
伏線・展開は無傷(01 §1)なので、変更は次の3点に限る。目標「登場人物はFramton・Veraのみ、オチとの関係が自然に理解できる構成」はユーザー明示済み(USER.md §6)。
1. **名前の導入**: 叔母の台詞で原作どおり導入(「I hope Vera has been amusing you」型)。Framtonが少女の名前を初めて聞く位置(Adv p17相当、Stdも対応段落)。
2. **p29**: `the girl said calmly` → `Vera said calmly`(narration clip 1本)。
3. **最終文の追加(末尾に1段落、narrator)**:
   - Advanced: 原作文そのまま `Romance at short notice was her speciality.`(直前の台詞の話者がVeraなのでherはVeraに定まる)。
   - Standard: `Vera was very good at making up stories on the spot.`(Fable決定。叔母とherの取り違え防止のため名前を主語にする=S07。聴取で最終確認)。
段落数30→31で両レベル一致を維持。語数: Adv約+7〜10語、Std約+11語(目標範囲内。超過してもWARNのみ)。「the girl」の他箇所をVeraへ置換するかは追加clipが増えるため行わない(最小構成)。
`romance`の理解リスク(S08): B1-B2の聞き手が「恋愛」と誤解しうる。**本文は原文維持**し、Fableが試聴で確認、必要なら日本語補助(Comment/KP側)で手当てする。

## 2. 実施方式: 決定論的パッチ(通常の再実行はしない・M08)
- 通常の再実行は禁止。理由: `DEPENDENTS`(`er062_family_z_writer_01.py:64-67`)により`r2`の変更が`std_adjust`/`plan_b1b`/`kp_b1b`/`support`を連鎖無効化し、StdがLLMで再生成される(本文全体が変わり、#157評価も無効化)。
- パッチ対象は**本文・segment plan・話者planのみ**:
  - `writer/r2.md`・`writer/std.md`・`segment_plan_{a2,b1b}.json`へ上記3点を手で反映(LLM呼出なし)。
  - `boundaries [9,20]`固定、narrator clipを末尾(Part3最後)に追記。
  - KP/Preview/Commentは**据え置き**。Part3後にCommentがある場合は結末非言及を確認。spoiler lintはPreview/Commentのみ対象で、不変なら影響なし(`er062_family_z_structure_01.py:811` `romance at short notice`はspoiler語として維持)。
  - `provenance`に「Fable/人手パッチ(R2出力ではない)」と、パッチ前後のsha・変更箇所を記録。
- **Store再利用**: Store keyは本文基準(speaker_voice含む)。変更のないclipは再利用、新規は名前導入clip(叔母台詞、Std/Advで各1〜2)+`Vera said calmly`clip+最終文clip。実施前にStore key再割当の有無を確認(dry-run、API 0)。
- 再TTS: 約3clip×2レベル。費用約3〜6円(OPEN_WINDOW_FIX_PLAN_01 §4根拠)。ASR・Azure phrase list・shared_gateは新規clipに通常適用。

## 3. 本文確定とパッチ準備(今すぐ並列可)・TTS以降(保留)
| 工程 | 時期 |
|---|---|
| 本文・planパッチの案作成、Store key dry-run | 今すぐ可(API 0。ただし成果物ファイルは書換えない=案として別置き) |
| TTS・組立・Pages再公開 | **U2(完成音声の修正・再生成の保留解除)かつOPEN-462(Std/Adv会話速度)配線確定の後**。先に実施すると再組立が二度になる |
| 実施順序の推奨 | OPEN-462配線確定直後に1回で実施 |

## 4. #157(『開いた窓』ユーザー試聴待ち)との調整(S09)
#157の試聴対象音声(`family_z_open_window_01`)は、本パッチ実施で**差し替わる**(名前導入・p29・最終文)。扱い: (i) ユーザーが既に試聴済みの場合、評価はVoice聞き分け・Framton発音アラームなど**パッチと無関係な項目は有効**、結末部分は再試聴が必要と注記する。(ii) 未試聴なら、パッチ後に試聴ページを更新して一度に聴けるようU2と併せて案内する。#157はPASS扱いしない(現状どおり)。

## 5. 費用・リスク
- 約3〜6円(再TTS)。LLM再生成0。
- リスク: 名前導入台詞の追加により叔母clip差替え(話者plan変更なし=Speakerは既にvera/mrs_sappleton)。Voice設定への影響なし。
- 副次ドリフト(Std歌詞`why do you bound`→`why are you jumping`)は今回修正しない。
