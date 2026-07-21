# ER-003-P2I 決定記録: B2 Key Words選定方式Lの正式採用

## 1. 決定

**方式L(Listening Blocker Ranking)を、B2 Key Words選定の標準方式として採用する。**

- 製品仕様の項目数は5(変更なし)。
- 対象記事: A01, A02, ADD03(3記事すべてでP2G成果物のL方式Rank1-5をそのままapproved化)。
- API再生成・項目の差し替え・日本語グロスの手修正は一切行っていない。

## 2. 採用理由(ユーザー指定の文言、そのまま記録)

> 製品仕様で使用するTop 5の評価はLとUが同点であり、ユーザーの定性的比較でも明確な優劣はなかった。
> そのうえでLは、個別学習者プロファイルへの依存がなく、
> 「初回リスニングで理解を止める可能性が高い表現を選ぶ」という単純で説明可能な原則を持つため、標準方式として採用する。

## 3. スコアの記録方法(重要な制約)

**Lが数値上Uへ明確に勝ったとは記録しない。Top5同点後の標準運用上のtie-breakとして記録する。**

| 指標 | L | P | U |
|---|---:|---:|---:|
| Top5合計(30点満点、製品採用範囲) | 24 | 22 | **24(Lと同点)** |
| Total合計(60点満点、Rank1-10全体) | 46 | 33 | **48(Lより高い)** |

- 製品仕様で使用するTop5では、L・Uは**同点**である。
- Total(研究目的のRank6-10まで含む全体)では、**Uの方がLより高い**。
- 記事内1位(total_score基準)回数: U=3記事すべてで1位または同率1位、L=A02・ADD03で同率1位、A01はUが単独1位。**Lが単独1位の記事はない。**
- したがって、L採用理由を「記事内1位回数」や「Total score」で正当化しない。採用理由は上記2節の説明可能性・非依存性のみである。

## 4. L以外の方式の扱い

- **方式U(Observed Learner Profile)**: 標準方式としては不採用。ただしTop5評価はLと同点であり、将来の学習者プロファイル別パーソナライズ機能の候補として明示的に保持する(`future_personalization_candidate`)。
- **方式P(Difficulty Portfolio)**: Top5・Total双方の評価で他方式に劣ったため、標準方式候補から除外する。ただしP2G/P2Hで取得した実験データはすべて監査・研究記録として保持し、削除・上書きは行わない。

## 5. 承認済み成果物の生成方法

- API再実行なし。ER-003-P2Gで既に生成・保存済みのL方式(Listening Blocker Ranking)Rank1-5の内容を、そのままapproved状態へ昇格した。
- 各記事のblind_mapping.jsonからL方式に対応するSetラベルを特定し(A01: Set A, A02: Set B, ADD03: Set A)、そのSetのkey_words_selection.jsonのRank1-5を`er003_output/p2i/{article_id}/key_words_approved.json`として保存した。
- ユーザーが△・×評価を付けた項目(例: A01「provide an assist」=×、A02「by default」=△、ADD03「be in place」=△、ADD03「breathe a sigh of relief」=△)を含め、個別の項目差し替え・グロス修正は一切行っていない。方式そのものと初期の決定的出力をまとめて採用する決定であり、個々の記事の最良5項目を人手で選び直す決定ではない。
- 将来の改善(標準方式Lの追加記事検証、本番運用後のユーザーFeedback反映)は本ステージのスコープ外とする。

## 6. 公式リファレンスの切り替え

- P2D/P2E/P2F/P2G/P2Hの成果物はすべて「実験的証跡(experimental evidence)」として保持し、削除・上書きは行わない。
- 本番運用における承認済みKey Wordsの参照元は、`er003_output/p2i/{article_id}/key_words_approved.json`および`key_words_approved_reading_copy.md`のみとする。
- 詳細は`er003_output/p2i/key_words_reference_manifest.json`を参照。

## 7. 本ステージのスコープ外

Key Words APIの再生成、個別項目の差し替え、日本語グロスの手修正、TTS実行、音声のペース・間の調整、B1/A2 Key Words、方式Uの実装、パーソナライズUI、追加記事での比較、B2本文・概要の変更、製品仕様の項目数変更(5から10への変更)、およびpushは、いずれも本ステージでは実施していない。
