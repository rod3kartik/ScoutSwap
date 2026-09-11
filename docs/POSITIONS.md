# ScoutSwap position vocabulary

ScoutSwap preserves the football-data.org source position on every domain
player and stores a separate normalized position for filtering, storage, and
ranking. Unknown, blank, or missing source labels map to `UNKNOWN`.

## Canonical values

| Value | Meaning |
| --- | --- |
| `GOALKEEPER` | Goalkeepers |
| `DEFENDER` | Centre-backs, full-backs, and generic defensive labels |
| `MIDFIELDER` | Defensive, central, attacking, wide, and generic midfield labels |
| `FORWARD` | Centre-forwards, wingers, second strikers, and generic attacking labels |
| `UNKNOWN` | Missing, blank, or unmapped source labels |

## Initial source mappings

| Source label | Normalized value |
| --- | --- |
| `Goalkeeper` | `GOALKEEPER` |
| `Defence`, `Defender`, `Centre-Back`, `Left-Back`, `Right-Back` | `DEFENDER` |
| `Midfield`, `Midfielder`, `Defensive Midfield`, `Central Midfield`, `Attacking Midfield`, `Left Midfield`, `Right Midfield` | `MIDFIELDER` |
| `Offence`, `Forward`, `Centre-Forward`, `Left-Winger`, `Right-Winger`, `Second Striker` | `FORWARD` |
