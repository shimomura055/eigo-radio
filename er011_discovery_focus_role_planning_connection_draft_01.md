# er011_discovery_focus_role_planning_connection_draft_01

管理ID: FAMILY-A-DISCOVERY-FOCUS-ROLE-PLANNING-CONNECTION-DESIGN-01。
**draft(未配線、Production未編集)。文面案とラッパー設計のみ。実装しない。**

## 前提

`er011_point_role_planning_focus_connection_trial_03.py`が既に汎用の
接続メカニズムをNews向けにGate 1=VALIDATED済みで提供している:

```python
run_point_role_planning_connected(client, topic, verified_ledger_text,
                                   model, reasoning_effort,
                                   point_role_hint_block: str = "")
run_one_pattern_connected(client, theme_id, label, prompt,
                           verified_ledger_text, topic, out_dir, ...,
                           point_role_hint_block: str = "")
```

`point_role_hint_block`はプレーン文字列。Discovery向けTrialでは、この
関数を**import して再利用**し(コピー不要)、Discovery固有のhint文字列を
新規定義して渡すだけでよい。

## 案2(推奨、Trial-03の(b)方式踏襲): Discovery/Why用 Point Role Hint Block

Focus Module Part Aの2方針(Main Storyは現象提示に留める/Point One・Two
は異なる角度で「なぜ」を深掘りする)を、Newsのhintと同じ「短い役割候補文」
形式に圧縮した案:

```python
DISCOVERY_WHY_POINT_ROLE_HINT_BLOCK = """This is a Discovery/Why article (Main Story presents a phenomenon without \
fully resolving why it happens). When planning Point One and Point Two, prefer roles the Ledger actually supports \
from among: a distinct causal mechanism Main Story left unresolved, an unexpected contributing factor from a \
different angle (psychological, environmental/design-related, or social/contextual) than the other Point, or a \
limitation on what the evidence actually explains. Do not assign both Points the same causal angle, and do not \
let either Point simply restate the phenomenon already described in Main Story."""
```

- 既定値`point_role_hint_block=""`のままなら、既存の全呼び出し(Discovery
  baseline、他editorial_type全て)はバイト単位で不変(Trial-03のunit test
  と同型の確認を、Discovery版でも実装時に追加すべき)。
- News hintとの違い: 「mechanism/beyond-the-headline factor/limitation」
  ではなく、「causal mechanism/different-angle contributing
  factor/limitation」とし、「同じ角度を両Pointに割り当てない」という
  Focus Module Part Aの明示的な禁止事項をそのまま反映した。

## 案2'(未検証、Newsでも実施例なし): Main Story逆方向の注記を追加する変種

`build_role_planning_block()`のレンダリング文言に、Point側の役割から
逆算した「Main Storyでは述べない」注記を1文追加する案(JSON schema変更
なし、レンダリング文言の追加のみ):

```python
def build_role_planning_block_with_main_story_note(planning: dict) -> str:
    """既存build_role_planning_block()の出力に、Main Story抑制を狙う
    1文を追加する変種(draft、未配線)。schema変更は行わない。"""
    base = point_planning.build_role_planning_block(planning)
    p1, p2 = planning["point_one"], planning["point_two"]
    note = (
        "\n\n【Main Storyへの注記(Discovery/Why、Focus Module Part Aと整合)】\n"
        f"上記の根拠({p1['evidence_anchor']} / {p2['evidence_anchor']})に含まれる"
        "具体的な機序・数値の説明は、Point One・Twoが担います。Main Storyでは"
        "これらを先取りして説明せず、現象そのものの提示に留めてください。"
    )
    return base + note
```

- リスク: Writerが過剰に萎縮しMain Storyが単調になる可能性(「記事として
  の面白さ」評価項目で検知できる設計)。
- 案2単独でB1のMain Story抑制が改善しない場合の追加検証対象として、
  小規模Trialの評価軸に含めることを提案(本体REPORT 3-1/6節参照)。

## Trial driverでの結線イメージ(未実装、疑似コード)

```python
from er011_point_role_planning_focus_connection_trial_03 import (
    run_one_pattern_connected, run_point_role_planning_connected,
)
# focus単独条件: 既存 prod_gen.run_one_pattern(...) をそのまま呼ぶ(接続なし)
# focus+接続条件:
result = run_one_pattern_connected(
    client, theme_tag, label, prompt, verified_ledger_text, topic_ja, out_dir,
    point_role_hint_block=DISCOVERY_WHY_POINT_ROLE_HINT_BLOCK,
)
```

Production 3ファイル(`er003_v1_n3_01_articles_generate.py`、
`er011_point_role_value_planning_01.py`、`er006_pool_pilot_01_writer.py`)は
一切編集しない。
