import maya.cmds as cmds 

# 1つのオブジェクトの履歴を調べる
def validate_history(obj):
    name = obj.split("|")[-1]

    history_nodes = cmds.listHistory(obj,pruneDagObjects=True) or []

    if history_nodes:
        print(name, "-> 構築履歴あり")
        print("履歴ノード:",history_nodes)
    else:
        print(name, "->構築履歴なし")


#選択オブジェクトを取得し、1つずつ検証する
def validate_selected_history():
    selected = cmds.ls(selection=True, long=True, type="transform") or []

    if not selected:
        print("オブジェクトを選択してください")
        return

    for obj in selected:
        validate_history(obj)



if __name__ == "__main__":
    validate_selected_history()