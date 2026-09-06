// =====================================
// YouTube Converter - Subtitle Font
// subtitle_font.js
//
// タブ2専用
//
// =====================================
// 【重要】JS ↔ Python 共通通信仕様
// =====================================
//
// このコメント部分は、
// subtitle_font.js と Python 側の
//
//   subtitle_font.py
//   subtitle_routes.py
//   subtitle.py
//
// の間で使用する「正式なデータ契約」です。
//
// JS内部の変数名やUI処理を大幅に変更しても、
// Pythonへ渡すデータ形式がこの仕様と一致していれば、
// 以降のPython処理を変更せずに動作できるようにする。
//
//
//
// =====================================
// 【Pythonへ渡す正式な字幕設定JSON】
// =====================================
//
// {
//     "preset": "標準",
//
//     "font": "Noto Sans CJK JP",
//
//     "text_color": "白",
//
//     "text_color_hex": "#FFFFFF",
//
//     "outline_color": "青",
//
//     "outline_color_hex": "#0000FF",
//
//     "outline_width": 5
// }
//
//
//
// =====================================
// 【各項目の意味】
// =====================================
//
// preset
//   型: string
//   内容: 選択中のプリセット名
//
//   Python:
//     settings["preset"]
//
//   例:
//     "標準"
//     "ゴシック"
//     "明朝"
//     "太字ゴシック"
//     "カスタム"
//
//
// font
//   型: string
//   内容: 字幕に使用するフォント名
//
//   Python:
//     settings["font"]
//
//   例:
//     "Noto Sans CJK JP"
//     "Noto Serif CJK JP"
//     "IPAGothic"
//     "IPAMincho"
//
//
// text_color
//   型: string
//   内容: 字幕文字色の色名
//
//   Python:
//     settings["text_color"]
//
//   例:
//     "白"
//     "黒"
//     "赤"
//     "青"
//     "黄"
//
//
// text_color_hex
//   型: string
//   内容: 字幕文字色のHTML/CSSカラーコード
//
//   Python:
//     settings["text_color_hex"]
//
//   例:
//     "#FFFFFF"
//     "#000000"
//     "#FF0000"
//
//   注意:
//   Python側では色名からASSカラーへ変換できるため、
//   この値はUI表示・確認用として扱う。
//
//
// outline_color
//   型: string
//   内容: 字幕縁取り色の色名
//
//   Python:
//     settings["outline_color"]
//
//   例:
//     "黒"
//     "白"
//     "赤"
//     "青"
//     "黄"
//
//
// outline_color_hex
//   型: string
//   内容: 字幕縁取り色のHTML/CSSカラーコード
//
//   Python:
//     settings["outline_color_hex"]
//
//   例:
//     "#000000"
//     "#FFFFFF"
//     "#FF0000"
//
//   注意:
//   Python側では色名からASSカラーへ変換できるため、
//   この値はUI表示・確認用として扱う。
//
//
// outline_width
//   型: integer
//   内容: 字幕縁取りの太さ
//
//   Python:
//     settings["outline_width"]
//
//   許可範囲:
//     0 ～ 10
//
//   例:
//     0
//     1
//     2
//     3
//
//
// =====================================
// 【JS内部の変数名】
// =====================================
//
// JS内部では camelCase を使用してよい。
//
// selectedSettings = {
//
//     font:
//         "Noto Sans CJK JP",
//
//     textColor:
//         "白",
//
//     textColorHex:
//         "#FFFFFF",
//
//     outlineColor:
//         "黒",
//
//     outlineColorHex:
//         "#000000",
//
//     outlineWidth:
//         2
//
// };
//
//
// =====================================
// 【JS → Python変換ルール】
// =====================================
//
// JS内部:
//
//     textColor
//
// ↓ Pythonへ送信:
//
//     text_color
//
//
// JS内部:
//
//     textColorHex
//
// ↓ Pythonへ送信:
//
//     text_color_hex
//
//
// JS内部:
//
//     outlineColor
//
// ↓ Pythonへ送信:
//
//     outline_color
//
//
// JS内部:
//
//     outlineColorHex
//
// ↓ Pythonへ送信:
//
//     outline_color_hex
//
//
// JS内部:
//
//     outlineWidth
//
// ↓ Pythonへ送信:
//
//     outline_width
//
//
// =====================================
// 【最重要】
// =====================================
//
// Python側が受け取る正式キーは snake_case。
//
//     preset
//     font
//     text_color
//     text_color_hex
//     outline_color
//     outline_color_hex
//     outline_width
//
// これらをJS内部の変数名と混同しない。
//
//
// =====================================
// 【Python側の処理の流れ】
// =====================================
//
// JS
//   ↓
//
// subtitle_font.js
//
//   ↓
// 字幕設定JSON
//
//   ↓
//
// subtitle_routes.py
//
//   ↓
//
// subtitle_font.py
//
//   ↓
//
// create_subtitle_font_settings()
// update_subtitle_font_settings()
// select_subtitle_font()
//
//   ↓
//
// subtitle.py
//
//   ↓
//
// FFmpeg / ASS
//
//
//
// =====================================
// 【Python側で最終的に使用する設定】
// =====================================
//
// Pythonでは最終的に以下の形に正規化する。
//
// {
//     "preset": "標準",
//     "font": "Noto Sans CJK JP",
//     "text_color": "白",
//     "outline_color": "黒",
//     "outline_width": 2
// }
//
//
//
// =====================================
// 【カラーについて】
// =====================================
//
// JS:
//
//     text_color_hex
//     outline_color_hex
//
// はUI表示用。
//
// Python:
//
//     text_color
//     outline_color
//
// を正式な色名として使用し、
// subtitle_font.py の
//
//     SUBTITLE_COLORS
//
// からASSカラーへ変換する。
//
// 例:
//
//     "白"
//       ↓
//     "#FFFFFF"
//       ↓
//     "&H00FFFFFF"
//
//
//
// =====================================
// 【縁取り太さについて】
// =====================================
//
// JS UI:
//
//     0 ～ 20
//
// として入力可能な場合でも、
// Python側の正式仕様は
//
//     0 ～ 10
//
// とする。
//
// Python側で必ず正規化する。
//
// したがってJS側の入力値を
// そのまま信用しない。
//
//
// =====================================
// 【プリセットについて】
// =====================================
//
// プリセット名そのものをPythonへ渡す。
//
// 例:
//
//     "標準"
//     "ゴシック"
//     "明朝"
//     "太字ゴシック"
//     "カスタム"
//
// Python側ではプリセット名が存在しない場合でも、
// デフォルト設定へフォールバックできる構造にする。
//
//
//
// =====================================
// 【外部公開API】
// =====================================
//
// subtitle.js から使用可能:
//
//     window.subtitleFont.getPreset()
//
//     window.subtitleFont.setPreset("ゴシック")
//
//     window.subtitleFont.getPresets()
//
//     window.subtitleFont.getSettings()
//
//     window.subtitleFont.setDisabled(true)
//
//     window.subtitleFont.isDisabled()
//
//     window.subtitleFont.update()
//
//
// =====================================
// 【getSettings()の正式戻り値】
// =====================================
//
// window.subtitleFont.getSettings()
//
// は以下の形式を返す。
//
// {
//     "preset_name": "標準",
//
//     "font": "Noto Sans CJK JP",
//
//     "text_color": "白",
//
//     "text_color_hex": "#FFFFFF",
//
//     "outline_color": "黒",
//
//     "outline_color_hex": "#000000",
//
//     "outline_width": 2
// }
//
//
//
// =====================================
// 【重要：getSettings()とPython通信】
// =====================================
//
// getSettings()の
//
//     preset_name
//
// はUI / JS内部API用。
//
// Pythonとの正式通信では
//
//     preset
//
// を使用する。
//
// つまり:
//
// JS API:
//     preset_name
//
// Python JSON:
//     preset
//
//
// この違いを維持する。
//
//
// =====================================
// 【変更禁止ではなく「契約」を守る】
// =====================================
//
// 今後 subtitle_font.js を大幅に修正しても、
//
// ・UIデザイン
// ・ダイアログ構造
// ・ボタン構造
// ・CSS
// ・イベント処理
// ・内部変数名
// ・プリセット表示方法
//
// は自由に変更してよい。
//
// ただしPythonへ渡す最終データは、
// 以下の7項目を維持する。
//
//     preset
//     font
//     text_color
//     text_color_hex
//     outline_color
//     outline_color_hex
//     outline_width
//
// この7項目が一致していれば、
// subtitle_font.py / subtitle.py 側との
// 接続部分を維持できる。
//
//
//
// =====================================
// 【現在の役割】
// =====================================
//
// ・字幕フォント設定UI
// ・#subtitle-font-button の操作
// ・選択中設定の保持
// ・プリセット管理
// ・文字色 / 縁取り色の選択
// ・subtitle.jsへの設定提供
// ・Pythonへ渡す設定データの生成
//
// =====================================
