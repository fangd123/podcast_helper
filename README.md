# 播客助手

该项目可以帮助你从中文播客榜导出热门播客的Excel名单，并将该名单转换为OPML订阅格式，方便在播客客户端导入。

## 准备工作

1. 确保你的电脑已安装Python。
2. 安装所需依赖：
   ```bash
   pip install -r requirements.txt
   ```

## 使用步骤

1. 执行以下命令，从中文播客榜导出热门播客的Excel名单：
   ```bash
   python 中文播客榜导出热门播客excel名单.py
   ```
   这会生成两个文件：`output.csv` 和 `output.xlsx`。

2. 打开 `output.xlsx`，按需修改内容并保存。

3. 执行以下命令，将修改后的Excel名单转换为OPML订阅格式：
   ```bash
   python excel名单导出opml订阅格式.py
   ```
   之后，你会得到一个OPML格式的文件。

4. 打开你的播客客户端，导入刚才生成的OPML文件，即可完成订阅导入。

## 反馈

如有任何问题或建议，请在GitHub issues中提出，我会尽快回应！
