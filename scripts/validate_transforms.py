import maya.cmds as cmds

#浮動小数点数の誤差を考慮するための許容値
TOLERANCE = 0.001

def validate_transform(obj):
    name = obj.split("|")[-1]

    # Transformの値を取得する
    translate = cmds.getAttr(obj + ".translate")[0]
    rotate = cmds.getAttr(obj + ".rotate")[0]
    scale = cmds.getAttr(obj + ".scale")[0]

    problems = []

    # Translateが基準値（0）から外れているか
    if any(abs(value) > TOLERANCE for value in translate):
        problems.append("Translate")

     # Rotateが基準値（0）から外れているか
    if any(abs(value) > TOLERANCE for value in rotate):
        problems.append("Rotate")

     # Scaleが基準値（1）から外れているか
    if any(abs(value - 1.0) > TOLERANCE for value in scale):
        problems.append("Scale")


    if problems:
        print(name, "-> Transform要確認:",",".join(problems))
    else:
        print(name,"-> Transform OK")


def validate_selected_transforms():
    selected = cmds.ls(selection=True,long=True,type="transform") or []

    if not selected:
        print("オブジェクトを選択してください")
        return

    for obj in selected:
        validate_transform(obj)



if __name__ == "__main__":
    validate_selected_transforms()