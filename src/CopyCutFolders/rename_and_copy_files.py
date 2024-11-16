"""
作画用のテンプレートファイルをカットナンバーにリネームしつつコピーする
"""
from pathlib import Path
import shutil

def rename_and_copy_files(source_folder:str, destination_folder:str, cut_name:str, replace_word:str, exist_ok:bool=False, skip_exist:bool=True, preview:bool=False):
    source_path = Path(source_folder)

    if not source_path.exists() or not source_path.is_dir():
        print("Error: Source folder does not exist or is not a directory.")
        return

    if not replace_word:
        raise Exception('置換文字列が指定されていません')

    if not replace_word in source_path.name:
        raise Exception('置換文字列がファイル名に含まれていません')
    
    destination_path = Path(destination_folder) / source_path.name.replace(replace_word, cut_name)
    if not preview:
        if not destination_path.exists():
            destination_path.mkdir(parents=True)
        elif not exist_ok:
            if not skip_exist:
                raise Exception('既にフォルダが存在していて、上書き設定がオフです')
            else:
                print(f'{destination_path.name}は存在するフォルダはスキップします')
                return 

    destination_files: list[Path] = []
    for source_file in source_path.iterdir():
        if source_file.is_file():
            new_name = source_file.name.replace(replace_word, cut_name)
            destination_file = destination_path / new_name

            if not preview:
                shutil.copy2(source_file, destination_file)

            destination_files.append(destination_file)
            
    return destination_files

if __name__ == "__main__":
    pass
