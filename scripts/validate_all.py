import sys
import importlib

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


# Mayaが保持している古いモジュールではなく、
# ファイルの最新のコードを読み込み直す
importlib.reload(validate_names)
importlib.reload(validate_transforms)
importlib.reload(validate_history)
importlib.reload(validate_ngons)
importlib.reload(validate_uvs)


def run_check(label, check_function):
    """1つの検証を実行し、結果データを返す。"""

    print(f"\n===== {label} =====")

    try:
        check_results = check_function() or []

    except Exception as error:
        print("[処理エラー]", label)
        print("エラーの種類:", type(error).__name__)
        print("エラーの詳細:", error)
        return False, []

    print("[処理完了]", label)

    return True, check_results


def validate_all():
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

    # 検証処理そのものの実行結果を記録する
    execution_results = []

    # 個々の検証が返した辞書をまとめる
    all_validation_results = []

    for label, check_function in checks:
        succeeded, check_results = run_check(
            label,
            check_function
        )

        execution_results.append((label, succeeded))
        all_validation_results.extend(check_results)

    # OKとNGの検証結果を分ける
    ok_results = [
        result
        for result in all_validation_results
        if result.get("status") == "OK"
    ]

    ng_results = [
        result
        for result in all_validation_results
        if result.get("status") == "NG"
    ]

    # 例外が発生した検証処理を数える
    exception_count = sum(
        1
        for label, succeeded in execution_results
        if not succeeded
    )

    # 実行サマリー
    print("\n===== 実行サマリー =====")

    for label, succeeded in execution_results:
        if succeeded:
            print(f"{label}: 例外なし")
        else:
            print(f"{label}: エラー発生")

    print("取得した検証結果数:", len(all_validation_results))
    print("検証OK件数:", len(ok_results))
    print("検証NG件数:", len(ng_results))
    print("例外が発生した数:", exception_count)

    # NGの詳細を一覧表示する
    print("\n===== NGの詳細 =====")

    if ng_results:
        for result in ng_results:
            print(
                "-",
                result.get("object", "不明"),
                "|",
                result.get("check", "不明"),
                "|",
                result.get("message", "")
            )
    else:
        print("検証NGはありません")

    if not all_validation_results:
        print(
            "検証結果データがありません。"
            "オブジェクトが選択されているか確認してください"
        )

    if exception_count == 0:
        print("すべての検証処理が例外なく終了しました")
    else:
        print("一部の検証処理で例外が発生しました")


if __name__ == "__main__":
    validate_all()