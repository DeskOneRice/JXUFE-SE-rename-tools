# encoding: utf-8
# @author: 花辞树
# @file: func_rename.py
# @time: 2024/10/15 20:48
# @desc: 班会文件批量重命名的核心逻辑模块
#        包含两个主要功能：
#          1. 预览重命名效果 —— 安全无副作用
#          2. 执行实际重命名 —— 会修改文件系统
import os
import json


# === 配置文件路径 ===
_CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

# === 默认配置（config.json 不存在时自动生成） ===
_DEFAULT_CONFIG = {
    "干扰词": ["软件与物联网工程学院", ".7z"],
    "专业配置": {
        "低空应用技术": [
            "低空应用技术", "低空应用", "低空技术", "应用技术",
            "低空经济", "低空", "经济", "物联网低空"
        ],
        "物联网工程": [
            "物联网工程专业", "物联网工程", "物联网专业", "物联网"
        ],
        "软件工程（中外合办）": [
            "软件工程（中外合办）", "软件工程(中外合办)",
            "软件（中外合办）", "软件(中外合办)",
            "软件（中外）", "软件(中外)",
            "软件工程中外", "软件中外"
        ],
        "软件工程": [
            "软件工程专业", "软件工程", "软件专业", "软件"
        ]
    }
}


def _load_config():
    """加载配置文件，不存在时自动创建默认配置"""
    if not os.path.exists(_CONFIG_PATH):
        with open(_CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(_DEFAULT_CONFIG, f, ensure_ascii=False, indent=4)
        return _DEFAULT_CONFIG
    with open(_CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _get_majors_and_noise():
    """从配置中提取专业列表和干扰词"""
    config = _load_config()
    noise_words = config.get("干扰词", [])
    majors_config = config.get("专业配置", {})
    # 字典的键是专业标准名称，值是关键词列表
    standard_names = list(majors_config.keys())
    keyword_lists = list(majors_config.values())
    return standard_names, keyword_lists, noise_words


def get_major_class(filename_str):
    """
    从原始文件名中提取"专业+班级"信息（如"软件229"）

    设计逻辑：
      - 支持多个专业关键词（物联网、软件工程等）
      - 优先匹配更具体的关键词（如"软件工程（中外合办）"）
      - 专业关键词后紧跟的连续数字视为班级号（如"229"）
      - 若无法识别专业或班级，则返回 None

    示例：
      输入："软件与物联网工程学院_软件工程229班材料.zip"
      输出："软件229 "

    注意：返回值末尾带一个空格，用于后续拼接（如"软件229 班会主题..."）
    """
    # 从配置文件加载专业关键词和干扰词
    standard_names, keyword_lists, words_to_remove = _get_majors_and_noise()

    # 初始化返回值
    major_class = ""  # 最终返回的"专业+班级"字符串
    found_major = False  # 是否成功识别出专业

    # 清除干扰词
    cleaned_str = filename_str
    for word in words_to_remove:
        idx = cleaned_str.find(word)
        if idx != -1:
            cleaned_str = cleaned_str.replace(word, "")

    # 尝试匹配专业关键词（在清理后的文件名中查找）
    keyword_end_pos = -1
    for i, keywords in enumerate(keyword_lists):
        for keyword in keywords:
            idx = cleaned_str.find(keyword)
            if idx != -1:
                # 找到匹配的专业关键词，使用该专业的标准名称
                major_class = standard_names[i]
                found_major = True
                # 记录关键词在字符串中的结束位置，用于后续找班级号
                keyword_end_pos = idx + len(keyword)
                break
        if found_major:
            break

    # 如果没找到任何专业关键词，直接返回 None（表示无法处理）
    if not found_major:
        return None

    # 从专业关键词之后开始，提取连续的数字作为班级号
    class_num = ""
    # 从关键词结束位置开始往后扫描
    for i in range(keyword_end_pos, len(cleaned_str)):
        char = cleaned_str[i]
        if '0' <= char <= '9':  # 是数字
            class_num += char
        elif class_num != "":  # 遇到非数字且已有数字 → 停止
            break
        # 如果还没开始收集数字，遇到非数字就继续

    # 如果没提取到班级号，也视为无效
    if not class_num:
        return None

    # 拼接"专业+班级"
    result = major_class + class_num
    return result


def _build_new_filename(original_name, topic):
    """根据原始文件名和主题，生成新文件名"""
    # 提取扩展名（如 ".zip"）
    dot_index = original_name.rfind(".")
    ext = original_name[dot_index:] if dot_index != -1 else ""

    # 提取专业班级
    major_class_str = get_major_class(original_name)
    if major_class_str is None:
        return None

    return f"{major_class_str} {topic} 班会材料{ext}"


def rename_files(path, topic, mode="preview"):
    """
    统一处理班会文件重命名：支持预览和执行两种模式

    Args:
        path (str): 目标文件夹路径
        topic (str): 班会主题
        mode (str): "preview"（仅预览）或 "work"（实际重命名）

    Returns:
        - mode="preview": str，预览文本
        - mode="work": dict，包含:
            {
                "success": bool,
                "message": str,      # 成功或错误信息
                "error_file": str,   # 出错的文件名（可选）
            }
    """
    assert mode in ("preview", "work"), "mode must be 'preview' or 'work'"

    # 获取该目录下所有文件和文件夹的名称列表
    try:
        file_list = os.listdir(path)
    except Exception as e:
        if mode == "preview":
            return f"【错误】无法访问目录：{path}\n原因：{e}"
        return {"success": False, "message": f"无法访问目录：{path}\n{e}"}

    if mode == "preview":
        return _preview_rename(file_list, topic)
    return _execute_rename(file_list, path, topic)


def _preview_rename(file_list, topic):
    """生成重命名预览文本（不修改实际文件）"""
    text_res = "【提示】批量规范命名（预览）已开始！！！\n"

    for cur_file in file_list:
        text_res += "=" * 70 + "\n"

        new_filename = _build_new_filename(cur_file, topic)

        if new_filename is None:
            text_res += "专业班级命名不规范！\n"
            text_res += "来源于：" + cur_file + "\n"
            continue

        text_res += f"old_filename: {cur_file}\n"
        text_res += f"new_filename: {new_filename}\n"

    text_res += "=" * 70 + "\n"
    text_res += "【提示】批量规范命名（预览）已完成！！！\n"
    return text_res


def _execute_rename(file_list, path, topic):
    """执行实际的批量重命名操作"""
    renamed_pairs = []  # 记录每次重命名的 (旧路径, 新路径)，用于撤回

    for cur_file in file_list:
        # 构造绝对路径（避免 os.chdir）
        old_path = os.path.join(path, cur_file)

        new_filename = _build_new_filename(cur_file, topic)

        if new_filename is None:
            # 标记异常文件
            new_bad_name = "【!】" + cur_file
            new_bad_path = os.path.join(path, new_bad_name)
            try:
                os.rename(old_path, new_bad_path)
                renamed_pairs.append((old_path, new_bad_path))
            except Exception as e:
                return {
                    "success": False,
                    "message": f"标记异常文件失败：{cur_file}\n{e}",
                    "error_file": cur_file
                }
            continue

        new_path = os.path.join(path, new_filename)

        # 执行重命名
        try:
            os.rename(old_path, new_path)
            renamed_pairs.append((old_path, new_path))
        except Exception as e:
            if isinstance(e, FileExistsError):
                msg = f"存在重复的专业班级，请检查!\n来源于：{cur_file}"
            else:  # Exception
                msg = f"重命名失败：{cur_file}\n{e}"
            return {"success": False, "message": msg, "error_file": cur_file}

    # 全部成功
    return {"success": True, "message": "批量重命名成功！", "renamed_pairs": renamed_pairs}
