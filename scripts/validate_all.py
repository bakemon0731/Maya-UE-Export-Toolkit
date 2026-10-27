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

def run_check(label, check_function):
    """1つの検証を実行し、例外を記録する。"""

    print(f"\n===== {label} =====")

    #検証を実行
    try:
        check_function()

    #exceptでエラーを受け取る
    except Exception as error:
        print("[処理エラー]", label)
        print("エラーの種類:", type(error).__name__)
        print("エラーの詳細:", error)
        return False

    print("[処理完了]", label)
    return True


def validate_all():
    # 検証名と、実行する関数を組み合わせる
    checks = [
        ("1. 命名規則チェック",
         validate_names.validate_selected_names),

        ("2. Transformチェック",
         validate_transforms.validate_selected_transforms),


        ("3. 構築履歴チェック",
         validate_history.validate_selected_history),

        ("4. N-gonチェック",
         validate_ngons.validate_selected_ngons),

        ("5. UVチェック",
         validate_uvs.validate_selected_uvs),
    ]

    results = []

    # 検証を順番に実行する
    for label, check_function in checks:
        succeeded = run_check(label, check_function)
        results.append((label, succeeded))

    # 最後に実行結果をまとめて表示する
    print("\n===== 実行サマリー =====")

    for label, succeeded in results:
        if succeeded:
            status = "例外なし"
        else:
            status = "エラー発生"

        print(f"{label}: {status}")

    error_count = sum(1 for label, succeeded in results if not succeeded)

    print("実行したチェック数:", len(results))
    print("例外が発生した数:", error_count)

    if error_count == 0:
        print("すべての検証処理がエラーなく終了しました")
    else:
        print("エラーが発生した検証処理があります。詳細を確認してください")


if __name__ == "__main__":
    validate_all()