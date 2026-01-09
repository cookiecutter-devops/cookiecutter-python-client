#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests

from {{cookiecutter.package_name}}.util import args, print_list

def do_registry_catalog(args):
    """List all images in docker registry."""
    url = 'http://localhost:5000/v2/_catalog'
    response = requests.get(url)
    data = response.json()

    # 使用print_list打印仓库列表
    if 'repositories' in data and data['repositories']:
        # 创建一个简单的对象列表，每个对象有一个name属性
        class Repo:
            def __init__(self, name):
                self.name = name

        repos = [Repo(name) for name in data['repositories']]
        print_list(repos, ['name'])
    else:
        print("No repositories found in the registry.")

@args('image', metavar='<IMAGE>', help='Image name to list tags for')
def do_registry_tags(args):
    """List tags for a specific image in docker registry."""
    url = 'http://localhost:5000/v2/{}/tags/list'.format(args.image)
    response = requests.get(url)
    data = response.json()

    # 使用print_list打印标签列表
    if 'tags' in data and data['tags']:
        # 创建一个简单的对象列表，每个对象有一个tag属性
        class Tag:
            def __init__(self, tag):
                self.tag = tag

        tags = [Tag(tag) for tag in data['tags']]
        print_list(tags, ['tag'])
    else:
        print("No tags found for image '{}'.".format(args.image))
