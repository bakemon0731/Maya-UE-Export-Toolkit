import maya.cmds as cmds

def validate_ngons(obj):

    name = obj.split('|')[-1] 

    shapes = cmds.listRelatives(obj,shapes=True,noIntermediate=True,fullPath=True,type="mesh") or []

    if not shapes:
        print(name,"-> Meshが見つかりません")
        return

    for shape in shapes:
        face_count = cmds.polyEvaluate(shape, face=True)
        ngon_faces = []

        for face_index in range(face_count):
            face = shape + ".f[" + str(face_index) + "]"

            #面ごとの頂点情報を取得
            face_info = cmds.polyInfo(face,faceToVertex=True)or{}

            if not face_info:
                continue

            vertex_text = face_info[0].split(":", 1)[1].strip()
            vertex_indices = vertex_text.split()
            vertex_count = len(vertex_indices)

            #面を構成する頂点の数を数え、5以上ならN-gon候補として表示する仕組み
            if vertex_count > 4:
                ngon_faces.append((face_index, vertex_count))

        if ngon_faces:
            print(name,"-> N-gonあり")

            for face_index,vertex_count in ngon_faces:
                print(" 面番号:", face_index,"頂点数:",vertex_count)
        else:
            print(name,"-> N-gonなし")


def validate_selected_ngons():
    selected = cmds.ls(selection=True, long=True,type="transform") or []

    if not selected:
        print("オブジェクトを選択してください")
        return

    for obj in selected:
        validate_ngons(obj)


validate_selected_ngons()