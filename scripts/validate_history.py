from unittest import result

import maya.cmds as cmds 

# 1つのオブジェクトの履歴を調べる
def validate_history(obj):
    name = obj.split("|")[-1]

    history_nodes = cmds.listHistory(obj,pruneDagObjects=True) or []

    # 検証結果を決定する
    if history_nodes:
        status = "NG"
        message = "構築履歴が残っています"
        print(name, "-> 構築履歴あり")
        print("履歴ノード:",history_nodes)
    else:
        status = "OK"
        message = "構築履歴がありません"
        print(name, "->構築履歴なし")

    # 検証結果を辞書として返す
    result = {
        "object": name,
        "check": "Construction History",
        "status": status,
        "message": message,
        "details": history_nodes
    }

    return result


#選択オブジェクトを取得し、1つずつ検証する
def validate_selected_history():
    selected = cmds.ls(selection=True, long=True, type="transform") or []

    if not selected:
        print("オブジェクトを選択してください")
        return[]

    results = []

    for obj in selected:
        result = validate_history(obj)
        results.append(result)

    return results



if __name__ == "__main__":
    results = validate_selected_history()
    print("検証データ:", results)