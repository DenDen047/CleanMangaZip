# Clean Manga Zip

漫画フォルダ（連番画像が入った1つのフォルダ）を一括でクレンジング・クロップ・ZIP 化する CLI ツール。

## What it does

各フォルダに対して順に実行する:

1. AVIF 画像 → WebP 変換
2. `*.url` / `*.db` / `*.ini` の不要ファイル削除
3. 画像のクロップ（手動指定 or 自動検出）
4. フォルダごと ZIP 化（1980 年以前のタイムスタンプは自動補正）

## Setup

[pixi](https://pixi.sh) で環境を構築する。pip / venv / conda は使わない。

```bash
pixi install
```

## Usage

### 単発（1フォルダ、よくある使い方）

フォルダのパスを直接渡すだけ。自動でクロップ範囲を検出する:

```bash
pixi run clean ~/Downloads/幼女戦記/v30
```

複数フォルダもスペース区切りで OK:

```bash
pixi run clean ~/Downloads/foo/v01 ~/Downloads/foo/v02
```

### バッチ（list.txt モード）

複数フォルダを `list.txt` に羅列して一括処理:

```txt
/home/username/manga_dir/v01
/home/username/manga_dir/v02
/home/username/manga_dir/v03
```

```bash
pixi run clean-batch
```

### Crop オプションの上書き

`pixi run clean` は `--crop_area auto` をデフォルトにしている。末尾に追加引数を付ければ argparse が後勝ちで上書きする:

| やりたいこと | コマンド |
|---|---|
| 自動検出（デフォルト） | `pixi run clean PATH` |
| クロップしない | `pixi run clean PATH --crop_area none` |
| 手動指定 | `pixi run clean PATH --crop_area 43,0,1061,1440` |
| 自動検出のサンプル数を増やす | `pixi run clean PATH --auto_samples 16` |
| 自動検出後さらに数 px タイトに切る | `pixi run clean PATH --padding -2` |
| 自動検出に余裕を持たせる | `pixi run clean PATH --padding 2` |

自動検出はフォルダ内の N 枚（デフォルト 8 枚）をサンプリングし、ピクセル毎の分散を計算して「全ページ共通の枠（低分散）」と「ページ毎に異なるコンテンツ（高分散）」を分離する。

### pixi タスク一覧

| Task | 用途 |
|---|---|
| `pixi run clean PATH...` | フォルダを指定して自動クロップ + ZIP |
| `pixi run clean-batch` | `list.txt` に羅列したフォルダを一括処理 |
| `pixi run run` | 素の `python main.py` (デフォルト無し、フル制御用) |
| `pixi run lint` / `pixi run format` / `pixi run test` | 開発用 |

## Project layout

このプロジェクトは [DenDen047/project-template](https://github.com/DenDen047/project-template) に従う。詳しくは [`CLAUDE.md`](CLAUDE.md) を参照。

```
├── main.py            # CLI 本体
├── pixi.toml          # 依存・タスク定義
├── CLAUDE.md          # Claude Code 用プロジェクト指示
├── AGENTS.md          # Codex CLI 用プロジェクト指示
├── .claude/           # Claude Code 設定 (skills, hooks, agents, rules)
├── .codex/            # Codex CLI 設定 (hooks)
└── plans/             # cross-model ワークフロー計画ファイル
```

## License

[MIT](LICENSE)
