import maya.cmds as cmds


# =========================================
# 01. Phong Material Detection
# =========================================

def get_phong_materials():

    """
    シーン内のPhongマテリアルを検索する。
    """

    phong_materials = cmds.ls(
        type="phong"
    ) or []

    return phong_materials


# =========================================
# 02. Phong Material Information
# =========================================

def get_phong_material_info():

    """
    PhongマテリアルのShading Groupと
    割り当て先の情報を取得する。
    """

    material_infos = []

    phong_materials = get_phong_materials()

    for material in phong_materials:

        # ---------------------------------
        # Shading Groupを取得
        # ---------------------------------

        shading_engines = cmds.listConnections(
            material,
            type="shadingEngine"
        ) or []

        # ---------------------------------
        # Shading Groupがない場合
        # ---------------------------------

        if not shading_engines:

            material_infos.append({

                "material": material,

                "shading_engine": None,

                "members": []

            })

            continue

        # ---------------------------------
        # Shading Groupごとに情報を取得
        # ---------------------------------

        for shading_engine in shading_engines:

            members = cmds.sets(
                shading_engine,
                query=True
            ) or []

            material_infos.append({

                "material": material,

                "shading_engine": shading_engine,

                "members": members

            })

    return material_infos


# =========================================
# 03. Converted Arnold Material Detection
# =========================================

def find_converted_arnold_material(phong_material):

    """
    指定されたPhongマテリアルに対応する
    Arnoldマテリアルを検索する。

    見つかった場合:
        Arnoldマテリアル名を返す

    見つからなかった場合:
        Noneを返す
    """

    # シーン内のArnoldマテリアルを取得
    arnold_materials = cmds.ls(
        type="aiStandardSurface"
    ) or []

    # Arnoldマテリアルを1つずつ確認
    for material in arnold_materials:

        # ---------------------------------
        # 変換元情報を持っているか確認
        # ---------------------------------

        has_source_info = cmds.attributeQuery(

            "sourcePhongMaterial",

            node=material,

            exists=True

        )

        if not has_source_info:

            continue

        # ---------------------------------
        # 変換元Phongの名前を取得
        # ---------------------------------

        source_name = cmds.getAttr(

            material + ".sourcePhongMaterial"

        )

        # ---------------------------------
        # 検索対象と一致するか確認
        # ---------------------------------

        if source_name == phong_material:

            return material

    # 最後まで見つからなかった場合
    return None


# =========================================
# 04. Phong → Arnold Conversion
# =========================================

def auto_convert_phong_to_arnold(target_materials):

    """
    指定されたPhongマテリアルを
    Arnold Standard Surfaceへ変換する。

    変換済みマテリアルは再変換しない。

    変換元情報をArnoldマテリアルの
    カスタム属性に保存する。

    変換結果を辞書形式で返す。
    """

    # =====================================
    # 04-01. 変換対象の確認
    # =====================================

    # 引数がリストまたはタプルか確認
    if not isinstance(target_materials, (list, tuple)):

        raise TypeError(
            "変換対象はリストまたはタプルで指定してください。"
        )

    # 結果を格納するリスト
    conversion_results = []

    # -------------------------------------
    # 変換対象が空の場合
    # -------------------------------------

    if not target_materials:

        return {

            "status": "SKIP",

            "message": "変換対象がありません。",

            "results": [],

            "summary": {
                "success": 0,
                "skipped": 0,
                "errors": 0
            }

        }

    # =====================================
    # 04-02. 変換対象の検証
    # =====================================

    phong_shaders = []

    for material in target_materials:

        # ---------------------------------
        # 文字列か確認
        # ---------------------------------

        if not isinstance(material, str) or not material.strip():

            conversion_results.append({

                "material": str(material),

                "status": "SKIP",

                "message": "有効なマテリアル名ではありません。"

            })

            continue

        # ---------------------------------
        # Mayaシーンに存在するか確認
        # ---------------------------------

        if not cmds.objExists(material):

            conversion_results.append({

                "material": material,

                "status": "SKIP",

                "message": "マテリアルが存在しません。"

            })

            continue

        # ---------------------------------
        # ノードタイプを確認
        # ---------------------------------

        if cmds.nodeType(material) != "phong":

            conversion_results.append({

                "material": material,

                "status": "SKIP",

                "message": "Phongマテリアルではありません。"

            })

            continue

        # ---------------------------------
        # 重複登録を防止
        # ---------------------------------

        if material not in phong_shaders:

            phong_shaders.append(material)

    # =====================================
    # 04-03. 有効な変換対象がない場合
    # =====================================

    if not phong_shaders:

        skipped_count = len(conversion_results)

        return {

            "status": "SKIP",

            "message": "有効なPhongマテリアルがありません。",

            "results": conversion_results,

            "summary": {
                "success": 0,
                "skipped": skipped_count,
                "errors": 0
            }

        }

    print(
        "{}個のPhongマテリアルを確認します。".format(
            len(phong_shaders)
        )
    )

    # =====================================
    # 04-04. Phongマテリアルごとの処理
    # =====================================

    for phong in phong_shaders:

        # Undo Chunkの状態
        chunk_open = False

        # Mayaの変更処理が始まったか
        modifications_started = False

        try:

            # =================================
            # 04-05. 変換済みか確認
            # =================================

            existing_arnold = find_converted_arnold_material(
                phong
            )

            # ---------------------------------
            # すでに変換済みの場合
            # ---------------------------------

            if existing_arnold:

                conversion_results.append({

                    "material": phong,

                    "status": "SKIP",

                    "arnold_material": existing_arnold,

                    "message": (
                        "すでに変換済みのためスキップしました。"
                    )

                })

                print(
                    "変換済みのためスキップ: {} → {}".format(
                        phong,
                        existing_arnold
                    )
                )

                continue

            # =================================
            # 04-06. Shading Groupの取得
            # =================================

            sgs = cmds.listConnections(

                phong,

                type="shadingEngine"

            ) or []

            # Shading Groupがなければスキップ
            if not sgs:

                conversion_results.append({

                    "material": phong,

                    "status": "SKIP",

                    "message": "Shading Groupがありません。"

                })

                continue

            # =================================
            # 04-07. Color入力元の取得
            # =================================

            color_source_plugs = cmds.listConnections(

                phong + ".color",

                source=True,

                destination=False,

                plugs=True

            ) or []

            # ---------------------------------
            # 複数の入力元がある場合
            # ---------------------------------

            if len(color_source_plugs) > 1:

                conversion_results.append({

                    "material": phong,

                    "status": "SKIP",

                    "message": "Colorに複数の入力接続があります。"

                })

                continue

            # ---------------------------------
            # 入力元プラグを取得
            # ---------------------------------

            color_source_plug = None

            file_node = None

            if color_source_plugs:

                color_source_plug = color_source_plugs[0]

                source_node = color_source_plug.split(".", 1)[0]

                if cmds.nodeType(source_node) == "file":

                    file_node = source_node

            # =================================
            # 04-08. Undo Chunk開始
            # =================================

            cmds.undoInfo(

                openChunk=True,

                chunkName="PhongToArnold_{}".format(phong)

            )

            chunk_open = True

            # =================================
            # 04-09. Arnoldマテリアル生成
            # =================================

            new_shader_name = (
                phong + "_aiStandardSurface"
            )

            ai_shader = cmds.shadingNode(

                "aiStandardSurface",

                asShader=True,

                name=new_shader_name

            )

            # ノード生成が成功したため変更開始と判断
            modifications_started = True

            # =================================
            # 04-10. 変換元情報の保存
            # =================================

            attribute_name = "sourcePhongMaterial"

            # ---------------------------------
            # カスタム属性が存在するか確認
            # ---------------------------------

            has_source_attribute = cmds.attributeQuery(

                attribute_name,

                node=ai_shader,

                exists=True

            )

            # ---------------------------------
            # 存在しなければ属性を追加
            # ---------------------------------

            if not has_source_attribute:

                cmds.addAttr(

                    ai_shader,

                    longName=attribute_name,

                    dataType="string"

                )

            # ---------------------------------
            # 変換元Phongの名前を保存
            # ---------------------------------

            cmds.setAttr(

                ai_shader + "." + attribute_name,

                phong,

                type="string"

            )

            print(
                "変換元情報を保存しました: {} → {}".format(
                    phong,
                    ai_shader
                )
            )

            # =================================
            # 04-11. テクスチャ・カラーの接続
            # =================================

            if color_source_plug:

                # ---------------------------------
                # 接続元をArnoldのBase Colorへ接続
                # ---------------------------------

                cmds.connectAttr(

                    color_source_plug,

                    ai_shader + ".baseColor",

                    force=True

                )

                print(
                    "Color接続を引き継ぎました: {}".format(
                        color_source_plug
                    )
                )

                # ---------------------------------
                # 直接File接続の場合
                # AlphaをOpacityへ接続
                # ---------------------------------

                if file_node:

                    cmds.connectAttr(

                        file_node + ".outAlpha",

                        ai_shader + ".opacityR",

                        force=True

                    )

                    cmds.connectAttr(

                        file_node + ".outAlpha",

                        ai_shader + ".opacityG",

                        force=True

                    )

                    cmds.connectAttr(

                        file_node + ".outAlpha",

                        ai_shader + ".opacityB",

                        force=True

                    )

            else:

                # ---------------------------------
                # 接続がない場合
                # 元のPhongの色をコピー
                # ---------------------------------

                orig_color = cmds.getAttr(

                    phong + ".color"

                )[0]

                cmds.setAttr(

                    ai_shader + ".baseColor",

                    orig_color[0],

                    orig_color[1],

                    orig_color[2],

                    type="double3"

                )

            # =================================
            # 04-12. Shading Groupを更新
            # =================================

            for sg in sgs:

                # ---------------------------------
                # Arnoldマテリアルを接続
                # ---------------------------------

                cmds.connectAttr(

                    ai_shader + ".outColor",

                    sg + ".surfaceShader",

                    force=True

                )

                # =================================
                # 04-13. 割り当て先のOpaque設定
                # =================================

                members = cmds.sets(

                    sg,

                    query=True

                ) or []

                for member in members:

                    # コンポーネント指定を除去
                    obj_name = member.split(".", 1)[0]

                    # Shapeノードが直接指定されている場合
                    if (

                        cmds.objExists(obj_name)

                        and cmds.nodeType(obj_name) == "mesh"

                    ):

                        shapes = [obj_name]

                    else:

                        # TransformからShapeを取得
                        shapes = cmds.listRelatives(

                            obj_name,

                            shapes=True,

                            noIntermediate=True,

                            fullPath=True

                        ) or []

                    for shape in shapes:

                        # ArnoldのOpaque属性があるか確認
                        if cmds.attributeQuery(

                            "aiOpaque",

                            node=shape,

                            exists=True

                        ):

                            cmds.setAttr(

                                shape + ".aiOpaque",

                                0

                            )

            # =================================
            # 04-14. Undo Chunk終了
            # =================================

            cmds.undoInfo(
                closeChunk=True
            )

            chunk_open = False

            # =================================
            # 04-15. 成功結果を記録
            # =================================

            conversion_results.append({

                "material": phong,

                "status": "OK",

                "arnold_material": ai_shader,

                "shading_groups": sgs,

                "message": "変換に成功しました。"

            })

        except Exception as error:

            error_message = str(error)

            # =================================
            # 04-16. エラー時のUndo
            # =================================

            # Undo Chunkが開いている場合は閉じる
            if chunk_open:

                try:

                    cmds.undoInfo(
                        closeChunk=True
                    )

                    chunk_open = False

                except Exception as close_error:

                    error_message += (

                        "\nUndo Chunkの終了に失敗しました: {}".format(
                            close_error
                        )

                    )

            # ---------------------------------
            # 変更処理が始まっていた場合はUndo
            # ---------------------------------

            if modifications_started and not chunk_open:

                try:

                    cmds.undo()

                    error_message += (
                        "\n失敗した変換処理をUndoしました。"
                    )

                except Exception as rollback_error:

                    error_message += (

                        "\nUndoによる復元にも失敗しました: {}".format(
                            rollback_error
                        )

                    )

            # =================================
            # 04-17. エラー結果を記録
            # =================================

            conversion_results.append({

                "material": phong,

                "status": "ERROR",

                "message": error_message

            })

            print(
                "変換エラー: {} : {}".format(
                    phong,
                    error_message
                )
            )

    # =====================================
    # 05. 変換結果の集計
    # =====================================

    success_count = sum(

        1

        for result in conversion_results

        if result.get("status") == "OK"

    )

    skipped_count = sum(

        1

        for result in conversion_results

        if result.get("status") == "SKIP"

    )

    error_count = sum(

        1

        for result in conversion_results

        if result.get("status") == "ERROR"

    )

    # =====================================
    # 06. 全体ステータスの決定
    # =====================================

    if success_count > 0:

        if skipped_count > 0 or error_count > 0:

            overall_status = "PARTIAL"

            message = (
                "一部のマテリアルのみ変換に成功しました。"
            )

        else:

            overall_status = "OK"

            message = (
                "すべての変換が完了しました。"
            )

    elif error_count > 0:

        overall_status = "ERROR"

        message = (
            "変換に失敗しました。"
        )

    else:

        overall_status = "SKIP"

        message = (
            "変換対象がありませんでした。"
        )

    # =====================================
    # 07. 変換結果を返す
    # =====================================

    return {

        "status": overall_status,

        "message": message,

        "results": conversion_results,

        "summary": {

            "success": success_count,

            "skipped": skipped_count,

            "errors": error_count

        }

    }