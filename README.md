# cookiecutter-python-client

仿照 Openstack  CLI 工具的快速落地实现。

## 功能

- 基于 argparse 实现的命令行工具
- 支持 Openstack 命令行工具的所有功能
- 支持自定义命令行工具的扩展



## 使用模版

```sh
$ pip install cookiecutter

$ cookiecutter gh:cookiecutter-devops/cookiecutter-python-client
  [1/13] author_name (Someone): hjl
  [2/13] author_email (someone@somewhere.com): hjl@qq.com
  [3/13] version (0.1):
  [4/13] project_name (python-client): python-regsitryclient
  [5/13] project_slug (python_regsitryclient):
  [6/13] package_name_long (Python CLI Boilerplate): python-regsitryclient
  [7/13] package_name (python_regsitryclient):
  [8/13] git (y): y
  [9/13] dockerfile (y):
  [10/13] Select open_source_license
    1 - MIT license
    2 - BSD license
    3 - ISC license
    4 - Apache Software License 2.0
    5 - GNU General Public License v3
    6 - Not open source
    Choose from [1/2/3/4/5/6] (1): 4
  [11/13] api_version (v2):
  [12/13] command_name (python-regsitryclient):
  [13/13] description (Python client for API):
```
