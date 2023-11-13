"""
作者：星隅（xing-yv）

版权所有（C）2023 星隅（xing-yv）

本软件根据GNU通用公共许可证第三版（GPLv3）发布；
你可以在以下位置找到该许可证的副本：
https://www.gnu.org/licenses/gpl-3.0.html

根据GPLv3的规定，您有权在遵循许可证的前提下自由使用、修改和分发本软件。
请注意，根据许可证的要求，任何对本软件的修改和分发都必须包括原始的版权声明和GPLv3的完整文本。

本软件提供的是按"原样"提供的，没有任何明示或暗示的保证，包括但不限于适销性和特定用途的适用性。作者不对任何直接或间接损害或其他责任承担任何责任。在适用法律允许的最大范围内，作者明确放弃了所有明示或暗示的担保和条件。

免责声明：
该程序仅用于学习和研究Python网络爬虫和网页处理技术，不得用于任何非法活动或侵犯他人权益的行为。使用本程序所产生的一切法律责任和风险，均由用户自行承担，与作者和项目协作者、贡献者无关。作者不对因使用该程序而导致的任何损失或损害承担任何责任。

请在使用本程序之前确保遵守相关法律法规和网站的使用政策，如有疑问，请咨询法律顾问。

无论您对程序进行了任何操作，请始终保留此信息。
"""

# 导入必要的模块

import asyncio
import re
import os
import time
import datetime
from tqdm import tqdm
import hashlib
import public as p
from colorama import Fore, Style, init
from get_bookinfo import get_book_info

init(autoreset=True)


def qimao_b(encoding, user_agent, path_choice, data_folder):

    if not os.path.exists("urls.txt"):
        print("url.txt文件不存在")
        return "file does not exist"

    try:
        # 打开url.txt文件
        with open("urls.txt", "r") as file:
            lines = file.readlines()

        # 检查文件是否为空
        if not lines or all(not line.strip() for line in lines):
            print("urls.txt文件为空")
            return
        else:
            # 检查每行是否包含"/page/"，并且不是空行
            for line in lines:
                line = line.strip()
                if line and "/page/" not in line:
                    print(f"语法错误：第{line}行")
                    return "file syntax is incorrect"

        print("urls.txt文件内容符合要求")

        # 定义文件夹路径
        folder_path = None
        # 如果用户选择自定义路径
        if path_choice == 1:
            import tkinter as tk
            from tkinter import filedialog
            # 创建一个Tkinter窗口，但不显示它
            root = tk.Tk()
            root.withdraw()

            print("您选择了自定义保存路径，请您在弹出窗口中选择保存文件夹。")

            while True:

                # 弹出文件对话框以选择保存位置和文件名
                folder_path = filedialog.askdirectory()

                # 检查用户是否取消了对话框
                if not folder_path:
                    # 用户取消了对话框，提示重新选择
                    print("您没有选择保存文件夹，请重新选择！")
                    continue
                else:
                    print("已选择保存文件夹")
                    break

        # 对于文件中的每个url，执行函数
        for url in lines:
            url = url.strip()  # 移除行尾的换行符
            if url:  # 如果url不为空（即，跳过空行）
                download_novels(url, encoding, user_agent, path_choice, folder_path, data_folder)
                time.sleep(1)

    except Exception as e:
        print(f"发生错误：{str(e)}")
        return f"发生错误：{str(e)}"


# 定义批量模式用来下载7猫小说的函数
def download_novels(url, encoding, user_agent, path_choice, folder_path, data_folder):

    book_id = re.search(r"/(\d+)/", url).group(1)

    # 调用异步函数获取7猫信息（模拟浏览器）
    book_info = asyncio.run(get_book_info(url))
    title = book_info['title']
    info = book_info['info']
    intro = book_info['intro']
    chapters = book_info['chapters']

    print(f"\n开始《{title}》的下载")

    # 拼接小说内容字符串
    content = f"""如果需要小说更新，请勿修改文件名
    使用 @星隅(xing-yv) 所作开源工具下载
    开源仓库地址:https://github.com/xing-yv/7mao-novel-downloader
    Gitee:https://gitee.com/xingyv1024/7mao-novel-downloader/
    任何人无权限制您访问本工具，如果有向您提供代下载服务者未事先告知您工具的获取方式，请向作者举报:xing_yv@outlook.com

    {title}
    {info}
    {intro}
    """

    chapter_id = None

    # 遍历每个章节链接
    for chapter in tqdm(chapters):
        time.sleep(1)
        # 获取章节标题
        chapter_title = chapter.find("span", {"class": "txt"}).get_text().strip()

        # 获取章节网址
        chapter_url = chapter.find("a")["href"]

        # 获取章节 id
        chapter_id = re.search(r"/(\d+)-(\d+)/", chapter_url).group(2)

        # 尝试获取章节内容
        chapter_content = None
        retry_count = 1
        while retry_count < 4:  # 设置最大重试次数
            try:
                param_string = f"chapterId={chapter_id}id={book_id}{p.sign_key}"
                sign = hashlib.md5(param_string.encode()).hexdigest()
                encrypted_content = p.get_qimao(book_id, chapter_id, sign)
            except Exception as e:

                tqdm.write(Fore.RED + Style.BRIGHT + f"发生异常: {e}")
                if retry_count == 1:
                    tqdm.write(f"{chapter_title} 获取失败，正在尝试重试...")
                tqdm.write(f"第 ({retry_count}/3) 次重试获取章节内容")
                retry_count += 1  # 否则重试
                continue

            if "data" in encrypted_content and "content" in encrypted_content["data"]:
                encrypted_content = encrypted_content['data']['content']
                chapter_content = p.decrypt_qimao(encrypted_content)
                chapter_content = re.sub('<br>', '\n', chapter_content)
                break  # 如果成功获取章节内容，跳出重试循环
            else:
                if retry_count == 1:
                    tqdm.write(f"{chapter_title} 获取失败，正在尝试重试...")
                tqdm.write(f"第 ({retry_count}/3) 次重试获取章节内容")
                retry_count += 1  # 否则重试

        if retry_count == 4:
            tqdm.write(f"无法获取章节内容: {chapter_title}，跳过。")
            continue  # 重试次数过多后，跳过当前章节

        # 去除其他 html 标签
        # chapter_text = re.sub(r"</?\w+>", "", chapter_text)
        #
        # chapter_text = p.fix_publisher(chapter_text)

        # 在小说内容字符串中添加章节标题和内容
        content += f"\n\n\n{chapter_title}\n\n{chapter_content}"

        # 打印进度信息
        tqdm.write(f"已获取 {chapter_title}")

    # 根据main.py中用户选择的路径方式，选择自定义路径或者默认

    file_path = None

    if path_choice == 1:

        # 使用用户选择的文件夹路径和默认文件名来生成完整的文件路径

        file_path = os.path.join(folder_path, f"{title}.txt")

    elif path_choice == 0:

        # 在程序文件夹下新建output文件夹，并把文件放入

        output_folder = "output"

        os.makedirs(output_folder, exist_ok=True)

        file_path = os.path.join(output_folder, f"{title}.txt")

    # 根据编码转换小说内容字符串为二进制数据
    data = content.encode(encoding, errors='ignore')

    # 保存文件
    with open(file_path, "wb") as f:
        f.write(data)

    # 打印完成信息
    print(f"已保存{title}.txt")

    # 计算文件 sha256 值
    hash_sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    sha256_hash = hash_sha256.hexdigest()

    # 保存小说更新源文件
    upd_file_path = os.path.join(data_folder, f"{title}.upd")
    # 获取当前系统时间
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # 创建要写入元信息文件的内容
    meta_content = f"{current_time}\n{url}\n{chapter_id}\n{encoding}\n{sha256_hash}"
    # 打开文件并完全覆盖内容
    with open(upd_file_path, "w") as file:
        file.write(meta_content)

    print("已完成")