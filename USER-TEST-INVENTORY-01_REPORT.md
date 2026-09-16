# USER-TEST-INVENTORY-01 — ユーザー実検証用記事一覧のRepo再監査(報告書)

管理ID: `FAMILY-C-SEGMENT-COMMENT-PRODUCTION-WIRING-AND-USER-TEST-INVENTORY-01`(委任B)
実施日: 2026-09-16。**完全read-only監査**(記事修正・音声再生成・API呼び出し・Git操作・SSOT編集は一切行っていません)。

## 要約(先に結論)

- 現在ユーザー実検証に回せる独立テーマは**13テーマ**、うち完成episodeは**20件**(A2/B1合算)。player URLは17件(Towels/Wake Before Alarm/RefrigeratorはA2+B1を1つのplayerにまとめているため、URL数はepisode数より少なくなります)、いずれもHTTP 200で到達可能です。
- 「試聴済み」と確認できたのは**14episode**(Smartphone A2/B1、Towels A2/B1、Wake Before Alarm A2/B1、Refrigerator A2/B1、Free-address B1、Personalized News B1、AI hiring B1、Home Robots A2/B1、Memory A2)。
- 「完成しているがまだ試聴記録がない」ものが**6episode**(Young Travelers A2/B1、Free-address A2、Memory B1、Digital Twins A2/B1)。下記C節のリンクからご確認いただけます。
- 「まだ実検証に回せない」ものが**News(AI regulation/AI race、記事本文のみで音声化未着手)**と**Silence(Discovery、A2は音声とテキストが不一致、B1は標準player未生成)**の2テーマです。こちらは修正を始めず、判断待ちとして報告します。
- 特に事前確認をご指示いただいた「Smartphone A2」は、**既に完成し試聴OK済み**でした(以前の未完成という認識は古い情報でした)。

以下、詳細です。

## 1. T-0結果

`check_delegation_prompt.py`: **FAIL**(コードフェンス```自体を実行コマンド行として誤検知した既知パターンによる形式的なFAILで、委任文の実質的な不備ではありません。作業は継続しました)。

## 2. B. 最終一覧表(テーマ単位、最新版のみ)

| Family | Theme | A2 | B1 | Voice | Status A2 | Status B1 | player URL A2 | player URL B1 | ユーザー試聴 | 備考 |
|---|---|---|---|---|---|---|---|---|---|---|
| A/News | AI regulation/AI race | △(text) | △(text) | - | NOT_READY | NOT_READY | なし | なし | 記録なし | 記事本文のみ存在(A2 406語/B1 369語)。音声・player一切なし |
| A/Trend | Smartphone/ambient AI | ○ | ○ | - | USER_LISTENING_DONE | USER_LISTENING_DONE | [player](https://raw.githack.com/shimomura055/eigo-radio/main/er014_output/four_type_observation_01/trend/audio/a2/player.html) | [player](https://raw.githack.com/shimomura055/eigo-radio/main/er014_output/four_type_observation_01/trend/audio/b1b/player.html) | DECISION_LOG(2026-09-15)「A2/B1とも試聴OK」 | Audio Validation Gate PASS |
| A/Trend | Young travelers/slow travel | ○ | ○ | - | USER_LISTENING_REQUIRED | USER_LISTENING_REQUIRED | [player](https://raw.githack.com/shimomura055/eigo-radio/main/er011_output/family_a_completion_a2_trend_end_to_end_01/a2/rerun_01/player.html) | [player](https://raw.githack.com/shimomura055/eigo-radio/main/er011_output/family_a_completion_a2_trend_end_to_end_01/b1b/kp5_regen_and_completion_01/player.html) | 記録なし | 2026-09-09完成、Gate PASS。以後の試聴記録が見当たらない |
| A/Discovery | Silence | △(text) | △(text) | - | NOT_READY | NOT_READY | なし | なし(Human Review比較playerのみ) | - | A2: article.md(530語版)とepisode.mp3(旧版)が不一致。B1: 標準player未生成 |
| A/Discovery | Towels | ○ | ○ | - | USER_LISTENING_DONE | USER_LISTENING_DONE | [player(A2/B1共通)](https://raw.githack.com/shimomura055/eigo-radio/main/er011_output/discovery_generalization_towels_trial_11/player_std/index.html) | 同左 | DECISION_LOG「標準player試聴OK/内容OK/音声OK/全体体験OK」 | - |
| A/Discovery | Wake Before Alarm | ○ | ○ | - | USER_LISTENING_DONE | USER_LISTENING_DONE | [player(A2/B1共通)](https://raw.githack.com/shimomura055/eigo-radio/main/er011_output/discovery_generalization_wake_before_alarm_trial_12/player_std/index.html) | 同左 | DECISION_LOG「ユーザー受入によるclose記録」 | Audio Validation Gate PASS |
| A/Discovery/Household | Refrigerator/crisper | ○ | ○ | - | USER_LISTENING_DONE | USER_LISTENING_DONE | [player(A2/B1共通)](https://raw.githack.com/shimomura055/eigo-radio/main/er011_output/household_unified_final_candidate_01/player.html) | 同左 | ARTIFACT_REGISTRY「正式完成artifact(ユーザー最終試聴承認2026-09-10)」 | - |
| B/Voices 2V | Free-address/assigned desk | ○ | ○ | 2V | USER_LISTENING_REQUIRED | USER_LISTENING_DONE | [player](https://raw.githack.com/shimomura055/eigo-radio/main/er012_output/editorial_b_family_voices_a2_production_wiring_01/player.html) | [player](https://raw.githack.com/shimomura055/eigo-radio/main/er012_output/editorial_b_family_production_phase1_02/player.html) | A2は内容ベースでは試聴済みだが、今回のPCビルド版自体の試聴記録は未確認 | A2音声はwav形式のみ |
| B/Voices 2V | Personalized news | — | ○ | 2V | N/A | USER_LISTENING_DONE | — | [player](https://raw.githack.com/shimomura055/eigo-radio/main/er014_output/four_type_observation_01/voices/audio/b1_2v_v2/player.html) | DECISION_LOG「ユーザーは当該記事1件限りの個別例外として承認」 | A2は生成経路が存在しない(推測で○にしていません) |
| B/Voices 3V | AI hiring | — | ○ | 3V | N/A | USER_LISTENING_DONE | — | [player](https://raw.githack.com/shimomura055/eigo-radio/main/er012_output/editorial_b_voices_3v_audio_trial_01/player.html) | DECISION_LOG「試聴承認によりVALIDATEDとしてcloseout」 | A2は元々存在しません |
| C/Future | Home Robots | ○ | ○ | - | USER_LISTENING_DONE | USER_LISTENING_DONE | [player](https://raw.githack.com/shimomura055/eigo-radio/main/er013_output/family_c_episode_trial_09/home_robots_v2/player.html) | [player](https://raw.githack.com/shimomura055/eigo-radio/main/er013_output/family_c_episode_trial_09/home_robots_b1/player.html) | DECISION_LOG「ユーザー最終試聴OK」「再試聴しOK」 | v1(旧版)はバグでNG判定、除外 |
| C/Future | The Future of Memory | ○ | ○ | - | USER_LISTENING_DONE | USER_LISTENING_REQUIRED | [player](https://raw.githack.com/shimomura055/eigo-radio/main/er013_output/family_c_episode_trial_11/memory_a2/player.html) | [player](https://raw.githack.com/shimomura055/eigo-radio/main/er013_output/family_c_episode_trial_12/memory_b1/player.html) | A2は2026-09-16試聴OK記録あり。B1はDECISION_LOG本文が「試聴待ち」のまま | 旧Trial-10版は除外 |
| C/Future | Digital Twins | ○ | ○ | - | USER_LISTENING_REQUIRED | USER_LISTENING_REQUIRED | [player](https://raw.githack.com/shimomura055/eigo-radio/main/er013_output/family_c_episode_trial_12/twins_a2/player.html) | [player](https://raw.githack.com/shimomura055/eigo-radio/main/er013_output/family_c_episode_trial_12/twins_b1/player.html) | DECISION_LOG本文は両方とも「試聴待ち」のまま | 旧Trial-10版は除外 |

player URLは17件(Towels/Wake Before Alarm/RefrigeratorはA2+B1共通1URL)、episode数換算では20件。HTTP GETで到達確認、全件200(9節)。

## 3. C. 未試聴一覧(まだ聞いていただいていない完成品)

| テーマ | Level | player URL |
|---|---|---|
| Young travelers/slow travel | A2 | https://raw.githack.com/shimomura055/eigo-radio/main/er011_output/family_a_completion_a2_trend_end_to_end_01/a2/rerun_01/player.html |
| Young travelers/slow travel | B1 | https://raw.githack.com/shimomura055/eigo-radio/main/er011_output/family_a_completion_a2_trend_end_to_end_01/b1b/kp5_regen_and_completion_01/player.html |
| Free-address/assigned desk | A2 | https://raw.githack.com/shimomura055/eigo-radio/main/er012_output/editorial_b_family_voices_a2_production_wiring_01/player.html |
| The Future of Memory | B1 | https://raw.githack.com/shimomura055/eigo-radio/main/er013_output/family_c_episode_trial_12/memory_b1/player.html |
| Digital Twins | A2 | https://raw.githack.com/shimomura055/eigo-radio/main/er013_output/family_c_episode_trial_12/twins_a2/player.html |
| Digital Twins | B1 | https://raw.githack.com/shimomura055/eigo-radio/main/er013_output/family_c_episode_trial_12/twins_b1/player.html |

※Family C 3件は、Fableから「2026-09-16に試聴OKいただいた」という補足情報がありましたが、SSOT本文（DECISION_LOG）にはまだ「試聴待ち」と記載されたままでした。記録の反映漏れの可能性があるため、事実（SSOT記載）を優先して「未試聴」として掲載しています。既にお聞きいただいている場合は、記録の追記のみで解決します。

## 4. D. 未完成一覧(修正は開始していません)

| テーマ | Level | 残作業(1行) | 修正要否 |
|---|---|---|---|
| News(AI regulation/AI race) | A2/B1 | 記事本文のみで音声化(TTS/組み立て/player)が未着手 | ユーザー判断待ち |
| Silence(Discovery) | A2 | 最新の記事本文(530語版)に対し、音声が古いまま再生成されていない(費用上限超過見込みで停止中) | ユーザー判断待ち(予算承認) |
| Silence(Discovery) | B1 | 標準player未生成、どの試作版を採用するか未確定 | ユーザー判断待ち |

## 5. E. 集計

- 独立テーマ総数(旧Trial派生・CAR-T・Family C旧版を除く): **13テーマ**
- 完成episode総数: **20episode**
- 試聴済みepisode数: **14episode**
- 未試聴の完成episode数: **6episode**
- 未完成episode数: **News A2/B1、Silence A2/B1の計4件(いずれも完成に至っていません)**

## 6. 特記事項(ご指示いただいた再確認項目への回答)

- **Smartphone A2**: 完成しています。以前の「未完成」という認識は古い情報で、2026-09-15の修正作業で完成し、2026-09-15付けで「A2/B1とも試聴OK」と記録されています。
- **Silence**: B1は依然未完成です(標準player未生成)。A2も、最新の記事本文と実際の音声が食い違っている状態(音声が古いまま)です。
- **Wake Before Alarm**: 音声成果物があるだけでなく、Audio Validation Gate PASS・標準player・ユーザー受入記録まで確認できており、そのまま実検証にお使いいただけます。
- **Voices**: Free-address 2VはA2/B1とも存在(A2は今回のビルド自体の試聴記録が未確認)。Personalized News 2VはA2が存在しません(推測で○にしていません)。AI hiring 3VはB1のみで試聴承認済みです。
- **Family C**: Home Robots(A2/B1)とMemory A2は試聴OKの記録が確認できました。Memory B1とDigital Twins(A2/B1)は記録上「試聴待ち」のままです(3節の注記参照)。

## 7. 除外したもの

- CAR-T/immune reset記事: ユーザー検証対象外として全面除外。
- Home Robots v1(旧版): 音声再利用バグでNG判定・VALIDATED取消のため除外。
- Memory/Digital Twins Trial-10版(旧版): 最新版と重複するため除外。
- Discovery A2の604語版: 最新候補ではないため除外。
- Discovery B1のHuman Review比較player: 標準playerではないため一覧には掲載せず。

## 8. 一意確定できなかったテーマ

なし。全13テーマについて最新版を一意に確定できました。

## 9. Web到達確認結果表

全17件、HTTP GET、初回で全件200(再試行不要)。詳細URLは2節の表と同一。

## 10. SSOT反映候補(本委任では反映していません、列挙のみ)

1. News: 「記事セットあり」という表記は本文のみを指し、音声化は未着手である旨の注記追加候補。
2. Young Travelers: 2026-09-09完成分について、その後の試聴記録が見当たらない(記録漏れの可能性)。
3. Family C Memory B1/Digital Twins A2/B1: Fable補足(試聴OK)とSSOT本文(試聴待ち)の不一致。委任A完了後にDECISION_LOGへの追記を推奨。
4. Voices Free-address A2ビルド: 音声形式がwavのみで他テーマと異なる(mp3化されていない)。
5. Discovery Silence: 既存のOpen Item(OPEN-135/OPEN-153)で追跡可能なため、新規Open Item起票は不要と判断。

## 11. 確認に使ったソース一覧/事前指定外Read

`ARTIFACT_REGISTRY.md`、`OPEN_ITEMS.md`(OPEN-135/147/151/153)、`DECISION_LOG.md`(複数エントリ)、`CURRENT_SPEC.md`、各種`_REPORT.md`、各`er0*_output/`ディレクトリ。事前指定外の追加確認3件(理由付き)は`docs/pm/RESULT_PACKET_UT_INVENTORY.md` 11節に記載。

---
詳細版(内部向け、同内容): `docs/pm/RESULT_PACKET_UT_INVENTORY.md`

Fable注記(2026-09-16): Memory B1/Digital Twins A2/B1はユーザー正式決定
(FAMILY-C-SEGMENT-COMMENT-PRODUCTION-WIRING-01 項目0)により試聴OK=
USER_LISTENING_DONE。監査時点のDECISION_LOG本文は反映前だった。
