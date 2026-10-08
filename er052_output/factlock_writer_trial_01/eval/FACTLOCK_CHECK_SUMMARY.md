# FACTLOCK_CHECK_SUMMARY(照合指標、測定のみ。照合は6-luna自己判定で盲検rubricの代替ではない)

対象run数=24(照合結果が存在するrun: r0=24, r1=24, r2=24)

## 1. (i) 文単位: タグ付き文数・整合/不整合/判定不能(全run合計 / 記事平均)
| 段 | タグ付き文 合計 | 整合 | 不整合 | 判定不能 | 不整合率 | 判定不能率 | unknown_tags | 主張 supported/unsupported/undecidable |
|---|---|---|---|---|---|---|---|---|
| R0 | 195 | 171 | 13 | 11 | 6.7% | 5.6% | 4 | 335/21/8 |
| R1 | 192 | 174 | 14 | 4 | 7.3% | 2.1% | 4 | 346/23/2 |
| R2 | 189 | 169 | 13 | 7 | 6.9% | 3.7% | 4 | 338/24/3 |

### 1-1. 主張別 unsupported 件数(run別、R0/R1/R2) と タグ外根拠件数
| run | R0 不整合文/タグ付き文 | R1 | R2 | R2 unsupported主張 |
|---|---|---|---|---|
| hormuz/b1__factlock__r1 | 1/10 | 0/7 | 1/8 | 1 |
| hormuz/b1__factlock__r2 | 1/7 | 0/7 | 1/6 | 1 |
| hormuz/b2__factlock__r1 | 0/9 | 0/8 | 0/9 | 0 |
| hormuz/b2__factlock__r2 | 0/9 | 0/6 | 0/5 | 0 |
| hormuz/b3__factlock__r1 | 0/7 | 1/8 | 0/8 | 0 |
| hormuz/b3__factlock__r2 | 0/7 | 0/8 | 0/8 | 0 |
| hormuz/b4__factlock__r1 | 1/10 | 1/10 | 0/9 | 0 |
| hormuz/b4__factlock__r2 | 1/11 | 1/12 | 1/11 | 1 |
| meta/b1__factlock__r1 | 0/3 | 0/3 | 0/3 | 0 |
| meta/b1__factlock__r2 | 1/6 | 0/5 | 0/3 | 0 |
| meta/b2__factlock__r1 | 0/6 | 0/5 | 0/5 | 0 |
| meta/b2__factlock__r2 | 0/5 | 0/5 | 0/5 | 0 |
| meta/b3__factlock__r1 | 0/10 | 0/10 | 0/9 | 0 |
| meta/b3__factlock__r2 | 0/7 | 0/6 | 1/7 | 1 |
| meta/b4__factlock__r1 | 0/6 | 1/6 | 0/6 | 0 |
| meta/b4__factlock__r2 | 0/5 | 1/5 | 0/5 | 0 |
| space_weapons/b1__factlock__r1 | 0/8 | 0/10 | 0/10 | 0 |
| space_weapons/b1__factlock__r2 | 0/5 | 0/12 | 0/12 | 0 |
| space_weapons/b2__factlock__r1 | 0/12 | 0/12 | 0/12 | 0 |
| space_weapons/b2__factlock__r2 | 0/11 | 0/10 | 1/11 | 1 |
| space_weapons/b3__factlock__r1 | 2/17 | 3/13 | 2/13 | 5 |
| space_weapons/b3__factlock__r2 | 5/9 | 5/8 | 5/8 | 13 |
| space_weapons/b4__factlock__r1 | 1/10 | 1/11 | 1/11 | 1 |
| space_weapons/b4__factlock__r2 | 0/5 | 0/5 | 0/5 | 0 |

## 2. (ii) タグなし文の5分類(title含む。全run合計)
| 段 | タグなし文 | neutral | untagged_brief_fact | hedged_speculation | background_general | new_specific_claim | titleの分類(分布) |
|---|---|---|---|---|---|---|---|
| R0 | 275 | 122 | 109 | 31 | 6 | 7 | untagged_brief_fact:13, neutral:10, background_general:1 |
| R1 | 314 | 152 | 127 | 26 | 5 | 4 | untagged_brief_fact:16, neutral:8 |
| R2 | 331 | 187 | 122 | 17 | 1 | 4 | untagged_brief_fact:13, neutral:11 |

## 3. (iii) 数値(決定論。title含む)
| 段 | 数値トークン | match | match_surface_diff | hedge_changed | not_core | 不一致計 | core_used_without_tag | marks_echoed | 数量語(副指標) |
|---|---|---|---|---|---|---|---|---|---|
| R0 | 79 | 78 | 0 | 1 | 0 | 1 | 26 | 0 | 3 |
| R1 | 79 | 78 | 0 | 1 | 0 | 1 | 11 | 0 | 1 |
| R2 | 83 | 78 | 0 | 1 | 4 | 5 | 12 | 0 | 4 |

### 3-1. R2の不一致数値トークン(hedge_changed / not_core)run別
- hormuz/b1__factlock__r1: 一件(not_core), 2.6%(hedge_changed)
- hormuz/b1__factlock__r2: 一件(not_core)
- hormuz/b3__factlock__r1: 一件(not_core)
- space_weapons/b4__factlock__r2: 一人(not_core)

## 4. (iv) R0→R1→R2 タグ付き文の 維持/改変/削除/added/number_changed(全run合計)
| 区間 | 維持 | 改変 | 削除 | added | number_changed |
|---|---|---|---|---|---|
| r0_to_r1 | 94 | 61 | 40 | 37 | 0 |
| r1_to_r2 | 100 | 57 | 35 | 32 | 1 |
| r0_to_r2 | 77 | 61 | 57 | 51 | 1 |

## 5. タグ除去後の残存「【」/ 広め除去のみで消えた変形タグ
| 段 | residual_brackets_after_strip 合計 | broad_only_tags_removed 合計 |
|---|---|---|
| R0 | 0 | 0 |
| R1 | 0 | 0 |
| R2 | 0 | 0 |

manifest `residual_bracket_scan.unexpected_total` 合計=101