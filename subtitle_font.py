# =====================================
# Subtitle Font Dialog
# subtitle_font.py
#
# 字幕フォント設定ダイアログ
#
# 機能:
#   - プリセット選択
#   - フォント選択
#   - 文字色選択
#   - 縁色選択
#   - 縁の太さ
#   - サンプル字幕
#   - 色付き●表示
#
# 外部から:
#
#   from subtitle_font import select_subtitle_font
#
#   settings = select_subtitle_font()
#
# 戻り値:
#
#   {
#       "preset": "標準",
#       "font": "Noto Sans CJK JP",
#       "text_color": "白",
#       "outline_color": "黒",
#       "outline_width": 2
#   }
#
# =====================================

import os
import shutil
import subprocess
import tkinter as tk

from pathlib import Path
from tkinter import ttk, messagebox


# =====================================
# プリセット設定
#
# 必要に応じてここへ追加
# =====================================

SUBTITLE_FONT_PRESETS = {

    "標準": {
        "font": "Noto Sans CJK JP",
        "text_color": "白",
        "outline_color": "黒",
        "outline_width": 2,
    },

    "映画風": {
        "font": "Noto Sans CJK JP",
        "text_color": "白",
        "outline_color": "黒",
        "outline_width": 3,
    },

    "黄色字幕": {
        "font": "Noto Sans CJK JP",
        "text_color": "黄色",
        "outline_color": "黒",
        "outline_width": 2,
    },

    "赤字幕": {
        "font": "Noto Sans CJK JP",
        "text_color": "赤",
        "outline_color": "白",
        "outline_width": 2,
    },

    "水色字幕": {
        "font": "Noto Sans CJK JP",
        "text_color": "水色",
        "outline_color": "黒",
        "outline_width": 2,
    },

}


# =====================================
# 初期プリセット
# =====================================

DEFAULT_PRESET = "標準"


# =====================================
# 色設定
#
# tk:
#   Tkinter表示用
#
# ass:
#   FFmpeg ASS/SSA用
# =====================================

SUBTITLE_COLORS = {

    "白": {
        "tk": "#FFFFFF",
        "ass": "&H00FFFFFF",
    },

    "黒": {
        "tk": "#000000",
        "ass": "&H00000000",
    },

    "黄色": {
        "tk": "#FFFF00",
        "ass": "&H0000FFFF",
    },

    "赤": {
        "tk": "#FF0000",
        "ass": "&H000000FF",
    },

    "水色": {
        "tk": "#00FFFF",
        "ass": "&H00FFFF00",
    },

}


# =====================================
# フォント候補
#
# 上から優先
# =====================================

FONT_CANDIDATES = [

    "Noto Sans CJK JP",
    "Noto Sans JP",
    "Noto Serif CJK JP",
    "Noto Serif JP",
    "IPAexGothic",
    "IPAGothic",
    "IPAexMincho",
    "IPAMincho",
    "VL Gothic",
    "TakaoGothic",

]


# =====================================
# 手動検索用フォント名
# =====================================

FONT_FILE_CANDIDATES = [

    "NotoSansCJK-Regular.ttc",
    "NotoSansCJKJP-Regular.otf",
    "NotoSansJP-Regular.ttf",

    "NotoSerifCJK-Regular.ttc",
    "NotoSerifCJKJP-Regular.otf",
    "NotoSerifJP-Regular.ttf",

    "ipaexg.ttf",
    "ipaexm.ttf",

    "IPAGothic.ttf",
    "IPAPGothic.ttf",

    "IPAMincho.ttf",
    "IPAPMincho.ttf",

    "TakaoGothic.ttf",
    "TakaoPGothic.ttf",

    "VL-Gothic-Regular.ttf",

]


# =====================================
# フォントディレクトリ
# =====================================

FONT_DIRECTORIES = [

    Path("/usr/share/fonts"),

    Path("/usr/local/share/fonts"),

    Path("/opt/render/project/src/fonts"),

    Path("/app/fonts"),

    Path("fonts"),

]


# =====================================
# ログ
# =====================================

def log(message):

    print(
        "[SUBTITLE_FONT]",
        message,
        flush=True
    )


# =====================================
# fc-matchでフォント確認
# =====================================

def check_font_with_fc_match(
    family
):

    fc_match = shutil.which(
        "fc-match"
    )

    if not fc_match:

        return None

    try:

        result = subprocess.run(

            [
                fc_match,

                "-f",
                "%{file}",

                family

            ],

            stdout=subprocess.PIPE,

            stderr=subprocess.PIPE,

            text=True,

            encoding="utf-8",

            errors="replace",

            timeout=10

        )

    except Exception:

        return None

    if result.returncode != 0:

        return None

    font_file = result.stdout.strip()

    if not font_file:

        return None

    path = Path(
        font_file
    )

    if not path.is_file():

        return None

    return path


# =====================================
# フォント検索
# =====================================

def find_available_fonts():

    fonts = []

    # =================================
    # fc-match
    # =================================

    for family in FONT_CANDIDATES:

        path = check_font_with_fc_match(
            family
        )

        if path:

            if family not in fonts:

                fonts.append(
                    family
                )

    # =================================
    # fc-list
    # =================================

    fc_list = shutil.which(
        "fc-list"
    )

    if fc_list:

        try:

            result = subprocess.run(

                [
                    fc_list,

                    ":lang=ja",

                    "-f",

                    "%{family}\\n"

                ],

                stdout=subprocess.PIPE,

                stderr=subprocess.PIPE,

                text=True,

                encoding="utf-8",

                errors="replace",

                timeout=10

            )

            if result.returncode == 0:

                for line in result.stdout.splitlines():

                    family = line.strip()

                    if not family:

                        continue

                    # 複数ファミリー名の場合
                    if "," in family:

                        family = (
                            family.split(
                                ",",
                                1
                            )[0].strip()
                        )

                    if family and family not in fonts:

                        fonts.append(
                            family
                        )

        except Exception as error:

            log(
                f"fc-listエラー: {error}"
            )

    # =================================
    # フォントが何も見つからない場合
    # =================================

    if not fonts:

        # 最低限、プリセットに設定されている
        # フォントを候補として残す

        for preset in SUBTITLE_FONT_PRESETS.values():

            family = preset.get(
                "font"
            )

            if family and family not in fonts:

                fonts.append(
                    family
                )

    return fonts


# =====================================
# 色付き●を作成
# =====================================

def create_color_dot(
    parent,
    color,
    size=14
):

    canvas = tk.Canvas(

        parent,

        width=size,

        height=size,

        highlightthickness=0,

        bd=0,

        bg=parent.cget("background")

    )

    padding = 2

    canvas.create_oval(

        padding,

        padding,

        size - padding,

        size - padding,

        fill=color,

        outline="#777777"

    )

    return canvas


# =====================================
# 色選択ドロップダウン
#
# ttk.Comboboxでは文字と●を同時に
# 表示しづらいため、独自Popupを使用
# =====================================

class ColorSelector(tk.Frame):

    def __init__(
        self,
        parent,
        colors,
        initial=None,
        command=None,
        **kwargs
    ):

        super().__init__(
            parent,
            **kwargs
        )

        self.colors = colors

        self.command = command

        self.value = (
            initial
            if initial in colors
            else next(iter(colors))
        )

        self.configure(
            bg="#FFFFFF"
        )

        # ---------------------------------
        # 表示ボタン
        # ---------------------------------

        self.button = tk.Button(

            self,

            text="",

            anchor="w",

            relief="solid",

            bd=1,

            bg="#FFFFFF",

            activebackground="#F0F0F0",

            cursor="hand2",

            command=self.show_popup

        )

        self.button.pack(
            fill="both",
            expand=True
        )

        self.update_display()

        self.popup = None

    # =================================
    # 表示更新
    # =================================

    def update_display(self):

        color_info = self.colors.get(
            self.value,
            {}
        )

        tk_color = color_info.get(
            "tk",
            "#FFFFFF"
        )

        self.button.configure(
            text=f"  {self.value}   ●    ▼",
            fg=(
                "#000000"
                if self.value != "黒"
                else "#333333"
            )
        )

        # ●部分は本来色付きCanvasが理想だが、
        # Button単体では部分的な文字色変更が
        # できないため、Popupでは実際の色付き●を使用する。

        self.button_color = tk_color

    # =================================
    # Popup
    # =================================

    def show_popup(self):

        if self.popup is not None:

            try:

                self.popup.destroy()

            except Exception:

                pass

            self.popup = None

            return

        self.popup = tk.Toplevel(
            self
        )

        self.popup.overrideredirect(
            True
        )

        self.popup.configure(
            bg="#FFFFFF"
        )

        # ---------------------------------
        # 位置
        # ---------------------------------

        self.update_idletasks()

        x = self.winfo_rootx()

        y = (
            self.winfo_rooty()
            +
            self.winfo_height()
        )

        width = max(
            self.winfo_width(),
            180
        )

        self.popup.geometry(
            f"{width}x{len(self.colors) * 34}"
            f"+{x}+{y}"
        )

        # ---------------------------------
        # 枠
        # ---------------------------------

        outer = tk.Frame(

            self.popup,

            bg="#888888",

            bd=1

        )

        outer.pack(
            fill="both",
            expand=True
        )

        inner = tk.Frame(

            outer,

            bg="#FFFFFF"

        )

        inner.pack(
            fill="both",
            expand=True
        )

        # ---------------------------------
        # 候補
        # ---------------------------------

        for color_name in self.colors:

            row = tk.Frame(

                inner,

                bg="#FFFFFF",

                cursor="hand2"

            )

            row.pack(

                fill="x",

                padx=2,

                pady=1

            )

            row.bind(

                "<Button-1>",

                lambda event,
                value=color_name:
                self.select_color(value)

            )

            label = tk.Label(

                row,

                text=color_name,

                bg="#FFFFFF",

                fg="#222222",

                anchor="w",

                width=10

            )

            label.pack(

                side="left",

                padx=(8, 2),

                pady=4

            )

            label.bind(

                "<Button-1>",

                lambda event,
                value=color_name:
                self.select_color(value)

            )

            color_info = self.colors.get(
                color_name,
                {}
            )

            tk_color = color_info.get(
                "tk",
                "#FFFFFF"
            )

            dot = tk.Canvas(

                row,

                width=20,

                height=20,

                bg="#FFFFFF",

                highlightthickness=0

            )

            dot.create_oval(

                3,

                3,

                17,

                17,

                fill=tk_color,

                outline="#777777"

            )

            dot.pack(
                side="left"
            )

            dot.bind(

                "<Button-1>",

                lambda event,
                value=color_name:
                self.select_color(value)

            )

        # ---------------------------------
        # 外側クリック
        # ---------------------------------

        self.popup.bind(
            "<FocusOut>",
            self.close_popup
        )

        self.popup.focus_force()

    # =================================
    # 色選択
    # =================================

    def select_color(
        self,
        value
    ):

        self.value = value

        self.update_display()

        self.close_popup()

        if self.command:

            self.command(
                self.value
            )

    # =================================
    # Popupを閉じる
    # =================================

    def close_popup(
        self,
        event=None
    ):

        if self.popup:

            try:

                self.popup.destroy()

            except Exception:

                pass

            self.popup = None

    # =================================
    # 値取得
    # =================================

    def get(self):

        return self.value

    # =================================
    # 値設定
    # =================================

    def set(
        self,
        value
    ):

        if value not in self.colors:

            return

        self.value = value

        self.update_display()


# =====================================
# フォント設定ダイアログ
# =====================================

class SubtitleFontDialog:

    def __init__(
        self,
        parent=None,
        initial_settings=None
    ):

        self.parent = parent

        self.initial_settings = (
            initial_settings
            if isinstance(
                initial_settings,
                dict
            )
            else {}
        )

        self.result = None

        self.root = tk.Toplevel(
            parent
        ) if parent else tk.Tk()

        self.root.title(
            "文字フォント"
        )

        self.root.resizable(
            False,
            False
        )

        self.root.configure(
            bg="#F5F5F5"
        )

        # ---------------------------------
        # ウィンドウサイズ
        # ---------------------------------

        self.root.geometry(
            "420x520"
        )

        # ---------------------------------
        # 閉じる
        # ---------------------------------

        self.root.protocol(
            "WM_DELETE_WINDOW",
            self.cancel
        )

        # ---------------------------------
        # フォント一覧
        # ---------------------------------

        self.fonts = find_available_fonts()

        if not self.fonts:

            self.fonts = [
                "Noto Sans CJK JP"
            ]

        # ---------------------------------
        # 現在値
        # ---------------------------------

        self.current_preset = (
            self.initial_settings.get(
                "preset",
                DEFAULT_PRESET
            )
        )

        if (
            self.current_preset
            not in SUBTITLE_FONT_PRESETS
        ):

            self.current_preset = (
                DEFAULT_PRESET
            )

        preset = SUBTITLE_FONT_PRESETS[
            self.current_preset
        ]

        self.current_font = (
            self.initial_settings.get(
                "font",
                preset["font"]
            )
        )

        self.current_text_color = (
            self.initial_settings.get(
                "text_color",
                preset["text_color"]
            )
        )

        self.current_outline_color = (
            self.initial_settings.get(
                "outline_color",
                preset["outline_color"]
            )
        )

        self.current_outline_width = (
            self.initial_settings.get(
                "outline_width",
                preset["outline_width"]
            )
        )

        # ---------------------------------
        # メインフレーム
        # ---------------------------------

        self.create_widgets()

        # ---------------------------------
        # 中央配置
        # ---------------------------------

        self.center_window()

    # =================================
    # UI作成
    # =================================

    def create_widgets(self):

        # ---------------------------------
        # タイトル
        # ---------------------------------

        title_frame = tk.Frame(

            self.root,

            bg="#F5F5F5"

        )

        title_frame.pack(

            fill="x",

            padx=24,

            pady=(20, 10)

        )

        title = tk.Label(

            title_frame,

            text="文字フォント",

            font=(
                "TkDefaultFont",
                16,
                "bold"
            ),

            bg="#F5F5F5",

            fg="#222222"

        )

        title.pack()

        # ---------------------------------
        # 区切り線
        # ---------------------------------

        separator = ttk.Separator(
            self.root,
            orient="horizontal"
        )

        separator.pack(
            fill="x",
            padx=20,
            pady=(0, 15)
        )

        # ---------------------------------
        # 内容
        # ---------------------------------

        content = tk.Frame(

            self.root,

            bg="#F5F5F5"

        )

        content.pack(

            fill="both",

            expand=True,

            padx=30

        )

        # =================================
        # プリセット
        # =================================

        self.create_label(
            content,
            "プリセット"
        )

        self.preset_var = tk.StringVar(
            value=self.current_preset
        )

        self.preset_combo = ttk.Combobox(

            content,

            textvariable=self.preset_var,

            values=list(
                SUBTITLE_FONT_PRESETS.keys()
            ),

            state="readonly",

            width=34

        )

        self.preset_combo.pack(

            fill="x",

            pady=(3, 15)

        )

        self.preset_combo.bind(

            "<<ComboboxSelected>>",

            self.on_preset_changed

        )

        # =================================
        # フォント
        # =================================

        self.create_label(
            content,
            "フォント"
        )

        self.font_var = tk.StringVar(
            value=self.current_font
        )

        if self.current_font not in self.fonts:

            self.fonts.insert(
                0,
                self.current_font
            )

        self.font_combo = ttk.Combobox(

            content,

            textvariable=self.font_var,

            values=self.fonts,

            state="readonly",

            width=34

        )

        self.font_combo.pack(

            fill="x",

            pady=(3, 15)

        )

        self.font_combo.bind(

            "<<ComboboxSelected>>",

            self.on_manual_changed

        )

        # =================================
        # 文字色
        # =================================

        self.create_label(
            content,
            "文字色"
        )

        self.text_color_selector = ColorSelector(

            content,

            SUBTITLE_COLORS,

            initial=self.current_text_color,

            command=self.on_color_changed,

            height=30

        )

        self.text_color_selector.pack(

            fill="x",

            pady=(3, 15)

        )

        # =================================
        # 縁色
        # =================================

        self.create_label(
            content,
            "縁色"
        )

        self.outline_color_selector = ColorSelector(

            content,

            SUBTITLE_COLORS,

            initial=self.current_outline_color,

            command=self.on_color_changed,

            height=30

        )

        self.outline_color_selector.pack(

            fill="x",

            pady=(3, 15)

        )

        # =================================
        # 縁の太さ
        # =================================

        self.create_label(
            content,
            "縁の太さ"
        )

        outline_frame = tk.Frame(

            content,

            bg="#F5F5F5"

        )

        outline_frame.pack(

            fill="x",

            pady=(3, 15)

        )

        self.outline_width_var = tk.StringVar(

            value=str(
                self.current_outline_width
            )

        )

        self.outline_spinbox = tk.Spinbox(

            outline_frame,

            from_=0,

            to=10,

            textvariable=self.outline_width_var,

            width=8,

            justify="center",

            font=(
                "TkDefaultFont",
                10
            ),

            relief="solid",

            bd=1

        )

        self.outline_spinbox.pack(
            side="left"
        )

        self.outline_spinbox.bind(

            "<KeyRelease>",

            self.on_manual_changed

        )

        # =================================
        # サンプル
        # =================================

        sample_label = tk.Label(

            content,

            text="サンプル",

            font=(
                "TkDefaultFont",
                10,
                "bold"
            ),

            bg="#F5F5F5",

            fg="#444444"

        )

        sample_label.pack(

            anchor="w",

            pady=(5, 5)

        )

        self.sample_frame = tk.Frame(

            content,

            bg="#333333",

            height=70

        )

        self.sample_frame.pack(

            fill="x",

            pady=(0, 20)

        )

        self.sample_frame.pack_propagate(
            False
        )

        self.sample_label = tk.Label(

            self.sample_frame,

            text="【サンプル字幕】",

            font=(
                "Noto Sans CJK JP",
                18,
                "bold"
            ),

            bg="#333333",

            fg="#FFFFFF"

        )

        self.sample_label.pack(
            expand=True
        )

        # =================================
        # ボタン
        # =================================

        button_frame = tk.Frame(

            self.root,

            bg="#F5F5F5"

        )

        button_frame.pack(

            fill="x",

            padx=30,

            pady=(0, 20)

        )

        cancel_button = tk.Button(

            button_frame,

            text="キャンセル",

            width=12,

            height=2,

            command=self.cancel,

            cursor="hand2"

        )

        cancel_button.pack(
            side="left"
        )

        ok_button = tk.Button(

            button_frame,

            text="決定",

            width=12,

            height=2,

            command=self.ok,

            cursor="hand2",

            bg="#4A90E2",

            fg="white",

            activebackground="#357ABD",

            activeforeground="white"

        )

        ok_button.pack(
            side="right"
        )

        # ---------------------------------
        # 初期サンプル更新
        # ---------------------------------

        self.update_sample()

    # =================================
    # ラベル作成
    # =================================

    def create_label(
        self,
        parent,
        text
    ):

        label = tk.Label(

            parent,

            text=text,

            font=(
                "TkDefaultFont",
                10,
                "bold"
            ),

            bg="#F5F5F5",

            fg="#333333",

            anchor="w"

        )

        label.pack(

            fill="x"

        )

        return label

    # =================================
    # プリセット変更
    # =================================

    def on_preset_changed(
        self,
        event=None
    ):

        preset_name = (
            self.preset_var.get()
        )

        preset = SUBTITLE_FONT_PRESETS.get(
            preset_name
        )

        if not preset:

            return

        # ---------------------------------
        # フォント
        # ---------------------------------

        font_name = preset.get(
            "font"
        )

        if font_name:

            if font_name not in self.fonts:

                self.fonts.insert(
                    0,
                    font_name
                )

                self.font_combo.configure(
                    values=self.fonts
                )

            self.font_var.set(
                font_name
            )

        # ---------------------------------
        # 文字色
        # ---------------------------------

        text_color = preset.get(
            "text_color"
        )

        if text_color:

            self.text_color_selector.set(
                text_color
            )

        # ---------------------------------
        # 縁色
        # ---------------------------------

        outline_color = preset.get(
            "outline_color"
        )

        if outline_color:

            self.outline_color_selector.set(
                outline_color
            )

        # ---------------------------------
        # 縁太さ
        # ---------------------------------

        outline_width = preset.get(
            "outline_width",
            2
        )

        self.outline_width_var.set(
            str(outline_width)
        )

        self.update_sample()

    # =================================
    # 手動変更
    # =================================

    def on_manual_changed(
        self,
        event=None
    ):

        self.update_sample()

    # =================================
    # 色変更
    # =================================

    def on_color_changed(
        self,
        value=None
    ):

        self.update_sample()

    # =================================
    # 縁太さ取得
    # =================================

    def get_outline_width(self):

        try:

            value = int(
                self.outline_width_var.get()
            )

        except (ValueError, TypeError):

            value = 2

        if value < 0:

            value = 0

        if value > 10:

            value = 10

        return value

    # =================================
    # サンプル更新
    # =================================

    def update_sample(self):

        font_name = (
            self.font_var.get()
        )

        if not font_name:

            font_name = "TkDefaultFont"

        text_color = (
            SUBTITLE_COLORS.get(
                self.text_color_selector.get(),
                {}
            ).get(
                "tk",
                "#FFFFFF"
            )
        )

        outline_color = (
            SUBTITLE_COLORS.get(
                self.outline_color_selector.get(),
                {}
            ).get(
                "tk",
                "#000000"
            )
        )

        outline_width = (
            self.get_outline_width()
        )

        # =================================
        # Tkinter Labelでは本物の縁取りが
        # できないため、Canvas上に文字を
        # 複数回描画して縁取りを表現する
        # =================================

        if hasattr(
            self,
            "sample_canvas"
        ):

            try:

                self.sample_canvas.destroy()

            except Exception:

                pass

        self.sample_canvas = tk.Canvas(

            self.sample_frame,

            bg="#333333",

            highlightthickness=0,

            bd=0

        )

        self.sample_canvas.pack(

            fill="both",

            expand=True

        )

        self.sample_frame.update_idletasks()

        width = (
            self.sample_frame.winfo_width()
        )

        height = (
            self.sample_frame.winfo_height()
        )

        center_x = width // 2
        center_y = height // 2

        # ---------------------------------
        # フォントサイズ
        # ---------------------------------

        font_size = 18

        # ---------------------------------
        # 縁
        # ---------------------------------

        if outline_width > 0:

            positions = []

            for dx in range(
                -outline_width,
                outline_width + 1
            ):

                for dy in range(
                    -outline_width,
                    outline_width + 1
                ):

                    if dx == 0 and dy == 0:

                        continue

                    if (
                        dx * dx
                        +
                        dy * dy
                        <=
                        outline_width
                        *
                        outline_width
                    ):

                        positions.append(
                            (dx, dy)
                        )

            for dx, dy in positions:

                self.sample_canvas.create_text(

                    center_x + dx,

                    center_y + dy,

                    text="【サンプル字幕】",

                    font=(
                        font_name,
                        font_size,
                        "bold"
                    ),

                    fill=outline_color,

                    anchor="center"

                )

        # ---------------------------------
        # 文字
        # ---------------------------------

        self.sample_canvas.create_text(

            center_x,

            center_y,

            text="【サンプル字幕】",

            font=(
                font_name,
                font_size,
                "bold"
            ),

            fill=text_color,

            anchor="center"

        )

    # =================================
    # 決定
    # =================================

    def ok(self):

        font_name = (
            self.font_var.get().strip()
        )

        if not font_name:

            messagebox.showwarning(

                "入力確認",

                "フォントを選択してください。",

                parent=self.root

            )

            return

        text_color = (
            self.text_color_selector.get()
        )

        outline_color = (
            self.outline_color_selector.get()
        )

        outline_width = (
            self.get_outline_width()
        )

        # ---------------------------------
        # 現在の設定を返す
        # ---------------------------------

        self.result = {

            "preset":
                self.preset_var.get(),

            "font":
                font_name,

            "text_color":
                text_color,

            "outline_color":
                outline_color,

            "outline_width":
                outline_width,

        }

        self.close()

    # =================================
    # キャンセル
    # =================================

    def cancel(self):

        self.result = None

        self.close()

    # =================================
    # 閉じる
    # =================================

    def close(self):

        try:

            self.root.grab_release()

        except Exception:

            pass

        try:

            self.root.destroy()

        except Exception:

            pass

    # =================================
    # 中央配置
    # =================================

    def center_window(self):

        self.root.update_idletasks()

        width = (
            self.root.winfo_width()
        )

        height = (
            self.root.winfo_height()
        )

        if self.parent:

            parent_x = (
                self.parent.winfo_rootx()
            )

            parent_y = (
                self.parent.winfo_rooty()
            )

            parent_width = (
                self.parent.winfo_width()
            )

            parent_height = (
                self.parent.winfo_height()
            )

            x = (
                parent_x
                +
                (parent_width - width) // 2
            )

            y = (
                parent_y
                +
                (parent_height - height) // 2
            )

        else:

            screen_width = (
                self.root.winfo_screenwidth()
            )

            screen_height = (
                self.root.winfo_screenheight()
            )

            x = (
                screen_width - width
            ) // 2

            y = (
                screen_height - height
            ) // 2

        self.root.geometry(

            f"{width}x{height}"
            f"+{x}+{y}"

        )


# =====================================
# 外部向け関数
#
# subtitle_routes.py等から使用
# =====================================

def select_subtitle_font(
    parent=None,
    initial_settings=None
):

    dialog = SubtitleFontDialog(

        parent=parent,

        initial_settings=initial_settings

    )

    if parent:

        parent.wait_window(
            dialog.root
        )

    else:

        dialog.root.mainloop()

    return dialog.result


# =====================================
# 現在設定を取得するための
# 簡易関数
# =====================================

def get_default_subtitle_font_settings():

    preset = SUBTITLE_FONT_PRESETS.get(

        DEFAULT_PRESET,

        {}

    )

    return {

        "preset":
            DEFAULT_PRESET,

        "font":
            preset.get(
                "font",
                "Noto Sans CJK JP"
            ),

        "text_color":
            preset.get(
                "text_color",
                "白"
            ),

        "outline_color":
            preset.get(
                "outline_color",
                "黒"
            ),

        "outline_width":
            preset.get(
                "outline_width",
                2
            ),

    }


# =====================================
# 単体テスト用
#
# python subtitle_font.py
# =====================================

def main():

    settings = select_subtitle_font()

    print()

    print(
        "====================================="
    )

    if settings:

        print(
            "字幕フォント設定"
        )

        print(
            "====================================="
        )

        for key, value in settings.items():

            print(
                f"{key}: {value}"
            )

    else:

        print(
            "キャンセルされました。"
        )

    print(
        "====================================="
    )

    print()


# =====================================
# 実行
# =====================================

if __name__ == "__main__":

    main()
