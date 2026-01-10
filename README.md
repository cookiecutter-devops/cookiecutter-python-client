# cookiecutter-python-client

使用 argparse 的一个命令行工具，用于快速访问 api，类似 OpenStack 命令行工具和 CLI 项目的实现。


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


## 测试

```sh
# 列出所有镜像及其标签
$ python-regsitryclient registry-image-tags
+----------+--------------+
|  Image   |     Tags     |
+----------+--------------+
| registry |      2       |
|  ubuntu  | 18.04, 14.04 |



# 查看单个镜像的所有标签
$ python-regsitryclient registry-image-tags ubuntu
+-------+
|  tag  |
+-------+
| 14.04 |
| 18.04 |
+-------+


# 查看单个镜像指定tag的大小
$ python-regsitryclient registry-image-tags ubuntu --tag=18.04 --size
+--------------+--------+
|    Image     |  Size  |
+--------------+--------+
| ubuntu:18.04 | 25.5MB |
+--------------+--------+



# 查看单个镜像指定tag的更新时间
$ python-regsitryclient registry-image-tags ubuntu --tag=18.04 --update
+--------------+--------------------------------+
|    Image     |          Last Updated          |
+--------------+--------------------------------+
| ubuntu:18.04 | 2023-05-30T09:32:09.432301537Z |
+--------------+--------------------------------+


# 同时查看大小和更新时间
$ python-regsitryclient registry-image-tags ubuntu --tag=18.04 --size --update
+--------------+--------------------------------+
|    Image     |             Value              |
+--------------+--------------------------------+
| Last Updated | 2023-05-30T09:32:09.432301537Z |
| ubuntu:18.04 |             25.5MB             |
+--------------+--------------------------------+
```


## 添加子命令

```python
@args('-m', '--meter', metavar='<METER>', help="Meter name to find samples for")
@args('-l', '--limit', metavar='<NUMBER>', type=int, help='Number of samples to limit')
def do_sample_list(args):
    """List samples for a specific meter."""
    url = f'http://localhost:8777/v2/meters/{args.meter}?limit={args.limit}'
    try:
        response = requests.get(url)
        response.raise_for_status()  # 检查HTTP错误
        samples = response.json()
```
