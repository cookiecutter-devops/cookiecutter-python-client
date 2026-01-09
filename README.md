# cookiecutter-python-client

使用 argparse 的一个命令行工具，用于快速访问 api，类似 OpenStack 命令行工具和 CLI 项目的实现。


## 使用模版

```sh
pip install cookiecutter

cookiecutter gh:cookiecutter-devops/cookiecutter-python-client
```


## 添加子命令

```python
@args('-f', '--file', metavar='<FILE>', required=True, help="Excel file name")
@args('-sn', '--sheetname', metavar='<SHEETNAME>', required=True, help="Excel file sheet name")
def do_create_excel(args):
    """create a excel file"""
    cc = Client(args.file, args.sheetname)
    cc.save(args.file)
```
