import sys

# 検証用スクリプトが保存されているフォルダ
SCRIPT_DIR = r"E:\Maya-UE-Export-Toolkit\scripts"

if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)


# 各検証機能を読み込む
import validate_names
import validate_transforms
import validate_history
import validate_ngons
import validate_uvs


def validate_all():
    print("\n===== 1. 命名規則チェック =====")
    validate_names.validate_selected_names()

    print("\n===== 2. Transformチェック =====")
    validate_transforms.validate_selected_transforms()

    print("\n===== 3. 構築履歴チェック =====")
    validate_history.validate_selected_history()

    print("\n===== 4. N-gonチェック =====")
    validate_ngons.validate_selected_ngons()

    print("\n===== 5. UVチェック =====")
    validate_uvs.validate_selected_uvs()


if __name__ == "__main__":
    validate_all()