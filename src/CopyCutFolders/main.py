import sys
from pathlib import Path
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                              QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                              QSpinBox, QCheckBox, QFileDialog, QTextEdit,
                              QDialog, QScrollArea)
from PySide6.QtCore import QSettings, Qt
from CopyCutFolders.src.CopyCutFolders.rename_and_copy_files import rename_and_copy_files
from common.src.template_manager import TemplateManagerWidget

class GuideDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowModality(Qt.NonModal)
        self.setWindowTitle("使用方法ガイド")
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)

        layout = QVBoxLayout(self)
        
        # スクロール可能なエリアを作成
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)

        # ガイドテキストを追加
        guide_text = """
# カットフォルダコピーツール 使用方法

## 概要
このツールは、アニメーション制作などで使用される、カット単位でのファイルやフォルダのコピーを効率化するためのユーティリティです。
複数のカット番号に対して、指定されたテンプレートに従ってファイル名を生成し、一括でコピーを行うことができます。

## 基本設定
1. **ソースフォルダ**
   - 「参照...」ボタンをクリックして、コピー元のフォルダを選択します

2. **出力フォルダ**
   - 「参照...」ボタンをクリックして、コピー先のフォルダを選択します

## ファイル名設定
1. **テンプレート**
   - ファイル名のテンプレートを選択します
   - 以下の変数が使用可能です：
     - {TITLE}: タイトル
     - {SCENE}: シーン番号
     - {CUT}: カット番号
   - 数字の桁数指定も可能（例：{CUT:3} で3桁のゼロ埋め）

2. **タイトルとシーン番号**
   - タイトル: プロジェクトの識別子（デフォルト: "al"）
   - シーン番号: シーンの番号（デフォルト: "10"）

3. **カット番号範囲**
   - 開始カット: 最初のカット番号（デフォルト: 2）
   - 終了カット: 最後のカット番号（デフォルト: 167）

## オプション設定
- **上書きを許可**: チェックすると、既存のファイルを上書きします
- **既存をスキップ**: チェックすると、既存のファイルをスキップします（デフォルトでオン）

## 実行手順
1. **プレビュー**
   - 「プレビュー」ボタンをクリックすると、作成予定のファイルパスが表示されます
   - 設定が正しいか確認できます

2. **実行**
   - 「実行」ボタンをクリックすると、実際のファイルコピーが開始されます
   - 実行ログが表示されます
"""
        guide_label = QLabel(guide_text)
        guide_label.setTextFormat(Qt.TextFormat.MarkdownText)
        guide_label.setWordWrap(True)
        scroll_layout.addWidget(guide_label)
        
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)

        # 閉じるボタン
        close_button = QPushButton("閉じる")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)

class CopyCutFilesApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = QSettings('AliceTools', 'CopyCutFolders')
        self.setWindowTitle("カットフォルダコピーツール")
        self.setMinimumWidth(600)
        self.guide_dialog = None

        # メインウィジェットとレイアウトの設定
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # 概要セクションのコンテナを作成
        overview_container = QWidget()
        # overview_container.setStyleSheet("""
        #     QWidget {
        #         background-color: #f5f5f5;
        #         border: 1px solid #dcdcdc;
        #         border-radius: 5px;
        #     }
        # """)
        overview_layout = QVBoxLayout(overview_container)
        overview_layout.setContentsMargins(15, 15, 15, 15)

        # タイトルラベル
        title_label = QLabel("カットフォルダコピーツール")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #333333;
                background-color: transparent;
            }
        """)
        overview_layout.addWidget(title_label)

        # 概要テキスト
        overview_text = """
このツールは、アニメーション制作などで使用される、カット単位でのファイルやフォルダのコピーを効率化するためのユーティリティです。
複数のカット番号に対して��指定されたテンプレートに従ってファイル名を生成し、一括でコピーを行うことができます。
"""
        overview_label = QLabel(overview_text.strip())
        overview_label.setWordWrap(True)
        overview_label.setStyleSheet("""
            QLabel {
                color: #666666;
                background-color: transparent;
                line-height: 150%;
            }
        """)
        overview_layout.addWidget(overview_label)

        # 概要コンテナをメインレイアウトに追加
        layout.addWidget(overview_container)

        # 余白を追加
        layout.addSpacing(10)

        # ガイドボタンを配置
        guide_layout = QHBoxLayout()
        guide_btn = QPushButton("ガイド")
        guide_btn.setStyleSheet("""
            QPushButton {
                padding: 5px 15px;
                background-color: #4a90e2;
                color: white;
                border: none;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #357abd;
            }
        """)
        guide_btn.clicked.connect(self.show_guide)
        guide_layout.addWidget(guide_btn)
        guide_layout.addStretch()
        layout.addLayout(guide_layout)

        # ソースフ��ルダ選択
        source_layout = QHBoxLayout()
        self.source_edit = QLineEdit()
        source_btn = QPushButton("参照...")
        source_btn.clicked.connect(lambda: self.browse_folder(self.source_edit))
        source_open_btn = QPushButton("フォルダを開く")
        source_open_btn.clicked.connect(lambda: self.open_folder(self.source_edit.text()))
        source_layout.addWidget(QLabel("ソースフォルダ:"))
        source_layout.addWidget(self.source_edit)
        source_layout.addWidget(source_btn)
        source_layout.addWidget(source_open_btn)
        layout.addLayout(source_layout)

        # 出力フォルダ選択
        dest_layout = QHBoxLayout()
        self.dest_edit = QLineEdit()
        dest_btn = QPushButton("参照...")
        dest_btn.clicked.connect(lambda: self.browse_folder(self.dest_edit))
        dest_open_btn = QPushButton("フォルダを開く")
        dest_open_btn.clicked.connect(lambda: self.open_folder(self.dest_edit.text()))
        dest_layout.addWidget(QLabel("出力フォルダ:"))
        dest_layout.addWidget(self.dest_edit)
        dest_layout.addWidget(dest_btn)
        dest_layout.addWidget(dest_open_btn)
        layout.addLayout(dest_layout)

        # テンプレートウィジェットを追加
        self.template_widget = TemplateManagerWidget(allow_reserved_word_edit=False)
        layout.addWidget(self.template_widget)

        # タイトルとシーン番号を横並びに配置
        title_scene_layout = QHBoxLayout()
        self.title_edit = QLineEdit()
        self.title_edit.setText("tl")
        self.scene_edit = QLineEdit()  # QSpinBoxからQLineEditに変更
        self.scene_edit.setText("1")  # デフォルト値を設定
        
        title_scene_layout.addWidget(QLabel("タイトル:"))
        title_scene_layout.addWidget(self.title_edit)
        title_scene_layout.addWidget(QLabel("シーン番号:"))
        title_scene_layout.addWidget(self.scene_edit)
        layout.addLayout(title_scene_layout)

        # カット番号範囲
        cut_layout = QHBoxLayout()
        self.start_spin = QSpinBox()
        self.start_spin.setRange(1, 999)
        self.start_spin.setValue(1)
        self.last_spin = QSpinBox()
        self.last_spin.setRange(1, 999)
        self.last_spin.setValue(1)
        cut_layout.addWidget(QLabel("開始カット:"))
        cut_layout.addWidget(self.start_spin)
        cut_layout.addWidget(QLabel("終了カット:"))
        cut_layout.addWidget(self.last_spin)
        layout.addLayout(cut_layout)

        # オプション
        option_layout = QHBoxLayout()
        self.exist_ok_check = QCheckBox("上書きを許可")
        self.skip_exist_check = QCheckBox("既存をスキップ")
        self.skip_exist_check.setChecked(True)
        option_layout.addWidget(self.exist_ok_check)
        option_layout.addWidget(self.skip_exist_check)
        layout.addLayout(option_layout)

        # プレビュー用テキストエリア
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setMinimumHeight(100)
        layout.addWidget(self.preview_text)

        # ボタンレイアウト（ガイドボタンを除去）
        buttons_layout = QHBoxLayout()
        preview_btn = QPushButton("プレビュー")
        preview_btn.clicked.connect(self.preview_paths)
        execute_btn = QPushButton("実行")
        execute_btn.clicked.connect(self.execute_copy)
        buttons_layout.addWidget(preview_btn)
        buttons_layout.addWidget(execute_btn)
        layout.addLayout(buttons_layout)

        # UIの値を読み込む
        self.load_settings()

        # シグナルを接続してpreview_textをクリアする
        self.source_edit.textChanged.connect(self.clear_preview)
        self.dest_edit.textChanged.connect(self.clear_preview)
        self.title_edit.textChanged.connect(self.clear_preview)
        self.scene_edit.textChanged.connect(self.clear_preview)
        self.start_spin.valueChanged.connect(self.clear_preview)
        self.last_spin.valueChanged.connect(self.clear_preview)
        self.exist_ok_check.stateChanged.connect(self.clear_preview)
        self.skip_exist_check.stateChanged.connect(self.clear_preview)
        self.template_widget.template_changed.connect(self.clear_preview)

    def browse_folder(self, line_edit:QLineEdit):
        folder = QFileDialog.getExistingDirectory(self, "フォルダを選択")
        if folder:
            line_edit.setText(folder)

    def _get_common_params(self):
        """共通パラメータを取得するヘルパーメソッド"""
        return {
            'source_folder': self.source_edit.text(),
            'destination_folder': self.dest_edit.text(),
            'title': self.title_edit.text(),
            'scene': self.scene_edit.text(),
            'start': self.start_spin.value(),
            'last': self.last_spin.value(),
            'template': self.template_widget.get_selected_template()
        }

    def _parse_template_value(self, key: str, value: str | int, digits: int | None = None) -> str:
        """テンプレートの値を指定された形式に変換する"""
        if digits is None:
            return str(value)
        
        # 数値に変換可能な場合はゼロ埋めを行う
        try:
            if isinstance(value, str) and not value.isdigit():
                return value
            return f"{int(value):0{digits}d}"
        except ValueError:
            return str(value)

    def _validate_inputs(self) -> tuple[bool, str]:
        """入力値を検証するヘルパーメソッド"""
        # 必須フィールドの確認
        if not self.source_edit.text().strip():
            return False, "ソースフォルダを指定してください。"
        if not self.dest_edit.text().strip():
            return False, "出力フォルダを指定してください。"
        if not self.title_edit.text().strip():
            return False, "タイトルを入力してください。"
        if not self.scene_edit.text().strip():
            return False, "シーン番号を入力してください。"
        if not self.template_widget.get_selected_template():
            return False, "テンプレートを選択してください。"

        # フォルダの存在確認
        source_path = Path(self.source_edit.text())
        dest_path = Path(self.dest_edit.text())
        
        if not source_path.exists():
            return False, f"ソースフォルダが存在しません: {source_path}"
        if not source_path.is_dir():
            return False, f"ソースフォルダがディレクトリではありません: {source_path}"
        
        if not dest_path.exists():
            return False, f"出力フォルダが存在しません: {dest_path}"
        if not dest_path.is_dir():
            return False, f"出力フォルダがディレクトリではありません: {dest_path}"

        # ソースフォルダと出力フォルダが同じでないことを確認
        if source_path.resolve() == dest_path.resolve():
            return False, "ソースフォルダと出力フォルダが同じです。異なるフォルダを指定してください。"

        # ソースフォルダ名に'{template}'が含まれることを確認
        if '{template}' not in source_path.name:
            return False, "ソースフォルダ名に'{template}'が含まれていません。\nフォルダ名に'{template}'を含めてください"

        # カット番号の範囲確認
        if self.start_spin.value() > self.last_spin.value():
            return False, f"開始カット（{self.start_spin.value()}）が終了カット（{self.last_spin.value()}）より大きくなっています。"

        return True, ""

    def _process_cuts(self, preview:bool=False):
        """カット処理の共通ロジック"""
        try:
            # 入力値の検証
            is_valid, error_message = self._validate_inputs()
            if not is_valid:
                self.preview_text.setText(f"エラー：\n{error_message}")
                return

            params = self._get_common_params()
            cut_list = range(params['start'], params['last'] + 1)
            
            if preview:
                preview_text = "作成予定のファイルパス:\n\n"
            else:
                preview_text = "実行ログ:\n\n"
            
            import re
            template_pattern = re.compile(r'\{([A-Z]+)(?::(\d+))?\}')
            
            for cut_number in cut_list:
                scene = params['scene']
                template = params['template']
                
                def replace_match(match: re.Match[str]):
                    key = match.group(1)
                    digits = int(match.group(2)) if match.group(2) else None
                    
                    value_map = {
                        'TITLE': params['title'],
                        'SCENE': scene,
                        'CUT': cut_number
                    }
                    
                    if key in value_map:
                        return self._parse_template_value(key, value_map[key], digits)
                    return match.group(0)  # マッチしない場合は元の字列を返す
                
                cut_name = template_pattern.sub(replace_match, template)
                
                destination_files = rename_and_copy_files(
                    params['source_folder'],
                    params['destination_folder'],
                    cut_name,
                    '{template}',
                    exist_ok=self.exist_ok_check.isChecked() if not preview else True,
                    skip_exist=self.skip_exist_check.isChecked() if not preview else False,
                    preview=preview
                )
                
                if preview and destination_files:
                    for dest_file in destination_files:
                        preview_text += f"コピー予定: {dest_file}\n"
                    preview_text += "-" * 50 + "\n"
                elif not preview and destination_files:
                    for dest_file in destination_files:
                        preview_text += f"コピー完了: {dest_file}\n"
                    preview_text += "-" * 50 + "\n"
            
            self.preview_text.setText(preview_text)

        except Exception as e:
            error_message = f"エラーが発生しました：\n{str(e)}"
            self.preview_text.setText(error_message)
            return

    def execute_copy(self):
        self._process_cuts(preview=False)

    def preview_paths(self):
        self._process_cuts(preview=True)

    def load_settings(self):
        self.source_edit.setText(self.settings.value('source_folder', ''))
        self.dest_edit.setText(self.settings.value('dest_folder', ''))
        self.title_edit.setText(self.settings.value('title', 'al'))
        self.scene_edit.setText(str(self.settings.value('scene', '10')))
        self.start_spin.setValue(int(self.settings.value('start_cut', 2)))
        self.last_spin.setValue(int(self.settings.value('last_cut', 167)))
        self.exist_ok_check.setChecked(self.settings.value('exist_ok', False, type=bool))
        self.skip_exist_check.setChecked(self.settings.value('skip_exist', True, type=bool))
        
        # テンプレートと予約語の復元
        saved_templates = self.settings.value('templates', [], type=list)
        saved_reserved_words = self.settings.value('reserved_words', [], type=list)
        selected_template = self.settings.value('selected_template', '')
        
        if saved_templates:
            self.template_widget.template_manager._templates = saved_templates
        if saved_reserved_words:
            self.template_widget.template_manager._reserved_words = set(saved_reserved_words)
        
        # コンボボックスを更新し、保存された選択を復元
        self.template_widget._update_template_combo()
        if selected_template and selected_template in saved_templates:
            index = self.template_widget.template_combo.findText(selected_template)
            if index >= 0:
                self.template_widget.template_combo.setCurrentIndex(index)

    def save_settings(self):
        self.settings.setValue('source_folder', self.source_edit.text())
        self.settings.setValue('dest_folder', self.dest_edit.text())
        self.settings.setValue('title', self.title_edit.text())
        self.settings.setValue('scene', self.scene_edit.text())
        self.settings.setValue('start_cut', self.start_spin.value())
        self.settings.setValue('last_cut', self.last_spin.value())
        self.settings.setValue('exist_ok', self.exist_ok_check.isChecked())
        self.settings.setValue('skip_exist', self.skip_exist_check.isChecked())
        
        # テンプレートと予約語の保存
        self.settings.setValue('templates', self.template_widget.template_manager.templates)
        self.settings.setValue('reserved_words', list(self.template_widget.template_manager.reserved_words))
        self.settings.setValue('selected_template', self.template_widget.get_selected_template())

    def closeEvent(self, event):
        self.save_settings()
        super().closeEvent(event)

    def clear_preview(self):
        """プレビューテキストをクリアする"""
        self.preview_text.clear()

    def show_guide(self):
        """ガイドダイアログを表示する"""
        if self.guide_dialog is None:
            self.guide_dialog = GuideDialog(self)
            self.guide_dialog.finished.connect(self.on_guide_closed)
        self.guide_dialog.show()

    def on_guide_closed(self):
        """ガイドダイアログが閉じられたときの処理"""
        self.guide_dialog = None

    def open_folder(self, path: str):
        """指定されたパスをOSのデフォルトアプリで開く"""
        if not path:
            return
            
        import os
        import platform
        
        try:
            if platform.system() == "Windows":
                os.startfile(path)
            elif platform.system() == "Darwin":  # macOS
                os.system(f"open '{path}'")
            else:  # Linux
                os.system(f"xdg-open '{path}'")
        except Exception as e:
            self.preview_text.setText(f"フォルダを開けませんでした：\n{str(e)}")

def main():
    app = QApplication(sys.argv)
    window = CopyCutFilesApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
