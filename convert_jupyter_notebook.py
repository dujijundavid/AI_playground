#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import nbformat
from nbconvert import PythonExporter

def clean_code_cell(source):
    """深度清理代码单元格内容"""
    patterns = [
        r'^#\s*In\[[\s\S]*?]:?[\s]*',  # Jupyter行号注释
        r'^get_ipython\(\)[\s\S]*?\n',   # IPython调用
        r'^%+\s*\w+.*?\n',              # 魔术命令
        r'^!.*?\n',                    # Shell命令
        r'^/\s*Warning:.*?\n',          # 常见警告注释
        r'<[^>]+>'                     # 去除HTML标签
    ]
    for pattern in patterns:
        source = re.sub(pattern, '', source, flags=re.MULTILINE)
    return source.strip()

def clean_markdown_cell(source):
    """清理Markdown单元格中的HTML标签"""
    # 去除所有HTML标签
    cleaned = re.sub(r'<[^>]+>', '', source)
    return cleaned.strip()

def process_cells(cells):
    """处理所有单元格，返回有效代码"""
    processed = []
    for cell in cells:
        if cell.cell_type == 'code':
            cleaned = clean_code_cell(cell.source)
            if cleaned:
                # 重建代码单元格避免元数据污染
                processed.append(nbformat.v4.new_code_cell(cleaned))
        elif cell.cell_type == 'markdown':
            # 先清除 Markdown 中的 HTML 标签，再转换为注释
            cleaned_markdown = clean_markdown_cell(cell.source)
            if cleaned_markdown:
                commented = '\n'.join(f'# {line}' if line else '#' 
                                      for line in cleaned_markdown.split('\n'))
                processed.append(nbformat.v4.new_code_cell(commented))
    return processed

def convert_notebook(notebook_path, output_path):
    """执行高质量转换的核心方法"""
    with open(notebook_path, 'r', encoding='utf-8') as f:
        nb = nbformat.read(f, as_version=4)
    
    # 分步处理单元格
    nb.cells = process_cells(nb.cells)
    
    # 生成Python代码
    exporter = PythonExporter()
    exporter.exclude_input_prompt = True
    code, _ = exporter.from_notebook_node(nb)
    
    # 最终清理：压缩多余空行
    code = re.sub(r'\n{3,}', '\n\n', code)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(code.strip())

def batch_convert(folder):
    """批量转换文件夹内所有ipynb文件"""
    py_folder = f"{folder}_py"
    os.makedirs(py_folder, exist_ok=True)
    
    for root, _, files in os.walk(folder):
        for file in files:
            if not file.endswith('.ipynb'):
                continue
            
            ipynb_path = os.path.join(root, file)
            py_path = os.path.join(py_folder, file.replace('.ipynb', '.py'))
            convert_notebook(ipynb_path, py_path)
            print(f"Converted: {file}")

if __name__ == '__main__':
    # 配置示例（请根据实际路径修改）
    NOTEBOOKS_FOLDER = r"/Users/David/Desktop/github_repos/AI_playground/Deep_learning_AI_Courses/crew_ai_course1/crewAI_course2"
    batch_convert(NOTEBOOKS_FOLDER)
