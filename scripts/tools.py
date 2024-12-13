# %%
import re

def extract_and_replace_tables(latex_string):
    # 定义正则表达式，匹配 \begin{tabular} 到 \end{tabular} 的内容
    pattern = r"\\begin\{tabular\}.*?\\end\{tabular\}"
    
    # 使用 re.findall 提取所有匹配的表格
    tables = re.findall(pattern, latex_string, re.DOTALL)
    
    # 遍历每个表格并替换为 HTML
    for table in tables:
        html_table = latex_to_html(table)  # 调用已定义的函数
        latex_string = latex_string.replace(table, html_table)
    
    return latex_string

def latex_to_html(latex_table):
    # 去掉 \\begin 和 \\end 行
    latex_table = re.sub(r"\\begin\{tabular\}\{.*?\}", "", latex_table)
    latex_table = re.sub(r"\\end\{tabular\}", "", latex_table)
    latex_table = re.sub(r"\\\\", "", latex_table)

    # 按行分割
    rows = re.split(r"\\hline", latex_table)

    # 构建 HTML 表格
    html_table = "<table border='1'>\n"

    for row in rows:
        row = row.strip()
        if not row:
            continue

        # 移除 \\hline
        row = row.replace("\\hline", "")

        # 按列分割
        columns = row.split("&")
        html_table += "  <tr>\n"

        for col in columns:
            html_table += f"    <td>{col.strip()}</td>\n"

        html_table += "  </tr>\n"

    html_table += "</table>"
    return html_table

def replace_display_math(latex_string):
    """
    将 \[...\] 替换为 $$...$$
    """
    pattern_1 = r"\\\[.*?\\\]"  # 匹配 \[...\] 的内容
    pattern_2 = r"\\\(.*?\\\)"  # 匹配 \(...\) 的内容
    pattern_3 = r"(?<!\n)\$\$(.+?)\$\$(?!\n)" # 匹配 $$...$$ 不换行公式的内容
    # 使用 re.sub 替换为 $$...$$
    latex_string = re.sub(pattern_1, lambda m: f"$$ {m.group(0)[2:-2].strip()} $$", latex_string, flags=re.DOTALL)
    latex_string = re.sub(pattern_2, lambda m: f"$$ {m.group(0)[2:-2].strip()} $$", latex_string, flags=re.DOTALL)
    latex_string = re.sub(pattern_3, r"$\1$", latex_string)
    # print(latex_string
    return latex_string

def replace_math_newline(latex_string):
    """
    将公式中的\n替换为\\
    """
    pattern_1 = r"(\$\$.*?\$\$|\$.*?\$)"  # 匹配公式中的内容
    # 使用 re.sub 替换为 $$...$$
    latex_string = re.sub(pattern_1, lambda m: m.group(0).replace('\n', '\\\\'), latex_string, flags=re.DOTALL)
    # print(latex_string
    return latex_string

def replace_table_newline(html_string):
    """
    查找所有 <table>...</table> 的内容，并将其中的 \n 替换为 #@n#。

    :param html_string: 包含 HTML 内容的字符串
    :return: 处理后的 HTML 字符串
    """
    pattern = r"<table.*?>.*?<\/table>"  # 匹配 <table>...</table>

    def replace_newline_in_table(match):
        table_content = match.group(0)
        return table_content.replace('\n', '#@n#')

    return re.sub(pattern, replace_newline_in_table, html_string, flags=re.DOTALL)

def replace_uns_newline(latex_string):
    """
    替换括号内不必要的换行
    """
    pattern_1 = r"（ *\n"  # 匹配 \[...\] 的内容
    pattern_2 = r"\n *）"  # 匹配 \[...\] 的内容
    # 使用 re.sub 替换为 $$...$$
    latex_string = re.sub(pattern_1, "", latex_string)
    latex_string = re.sub(pattern_2, "", latex_string)
    return latex_string

# 示例输入
# latex_table = '''这里是一些内容\\begin{tabular}{|c|c|c|}
# \\hline 性别 & 男 & 女 \\\\
# \\hline 是否需要志愿者 & & \\\\
# \\hline 需要 & 40 & 30 \\\\
# \\hline 不需要 & 160 & 270 \\\\
# \\hline
# \\end{tabular}
# 结束后还有一些内容'''

# # 转换为 HTML
# html_table = extract_and_replace_tables(latex_table)
# print(html_table)

# %%
