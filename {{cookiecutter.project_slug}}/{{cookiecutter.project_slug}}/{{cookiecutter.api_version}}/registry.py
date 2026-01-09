#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import json
import requests
from datetime import datetime
from {{cookiecutter.package_name}}.util import args, print_list

REGISTRY_URL = 'http://localhost:5000'


def _get_image_update_time(image_name, tag):
    """
    通过解析manifest中的历史记录来获取镜像的创建时间
    """
    manifest_url = f'{REGISTRY_URL}/v2/{image_name}/manifests/{tag}'
    headers = {'Accept': 'application/vnd.docker.distribution.manifest.v1+json'}
    try:
        response = requests.get(manifest_url, headers=headers)
        if response.status_code == 200:  # 检查响应状态码
            manifest_data = response.json()  # 将响应转换为JSON
            if "history" in manifest_data and len(manifest_data["history"]) > 0:
                compatibility = manifest_data["history"][0]["v1Compatibility"]
                return json.loads(compatibility)["created"]
    except requests.RequestException as e:
        print(f"Warning: Error fetching manifest for {image_name}: {e}")
    except (KeyError, IndexError, json.JSONDecodeError) as e:
        print(f"Warning: Error parsing manifest for {image_name}: {e}")
    return "Unknown"


def _registry_image_tags_list(args):
    """List all images with their tags in docker registry."""
    # 获取所有仓库
    catalog_url = f'{REGISTRY_URL}/v2/_catalog'
    catalog_response = requests.get(catalog_url)
    catalog_data = catalog_response.json()

    if 'repositories' not in catalog_data or not catalog_data['repositories']:
        print("No repositories found in the registry.")
        return

    # 为每个仓库获取标签并按仓库分组
    for repo in catalog_data['repositories']:
        tags_url = f'{REGISTRY_URL}/v2/{repo}/tags/list'
        tags_response = requests.get(tags_url)
        tags_data = tags_response.json()

        if 'tags' in tags_data and tags_data['tags']:
            # 使用print_dict显示镜像和其所有标签
            tags_str = ', '.join(tags_data['tags'])
            image_info = {
                repo: tags_str
            }
            print_dict(image_info, headers=['Image', 'Tags'], property='Image')
        else:
            print(f"No tags found for image '{repo}'.")


@args('image', nargs='?', metavar='<IMAGE>', help='Image name to list tags for (optional, omit to list all images)')
@args('--size', action='store_true', help='Show image size for the tag')
@args('--update', action='store_true', help='Show last update time for the tag')
@args('--tag', metavar='<TAG>', help='Specific tag to inspect (required for --size and --update)')
def do_registry_image_tags(args):
    """List tags for a specific image or show details for a specific tag"""
    # 验证参数
    if (args.size or args.update) and not args.tag:
        print("Error: --tag is required when using --size or --update")
        return

    if (args.size or args.update or args.tag) and not args.image:
        print("Error: <IMAGE> is required when using --size, --update, or --tag")
        return

    # 如果没有提供 image 参数，则列出所有镜像的标签
    if not args.image:
        return _registry_image_tags_list(args)

    # 获取标签列表
    url = f'{REGISTRY_URL}/v2/{args.image}/tags/list'
    response = requests.get(url)
    data = response.json()

    # 如果指定了标签且需要详细信息
    if args.tag:
        if 'tags' not in data or args.tag not in data['tags']:
            print(f"No tag '{args.tag}' found for image '{args.image}'.")
            return

        # 获取镜像清单
        manifest_url = f'{REGISTRY_URL}/v2/{args.image}/manifests/{args.tag}'
        headers = {'Accept': 'application/vnd.docker.distribution.manifest.v2+json'}
        manifest_response = requests.get(manifest_url, headers=headers)

        if manifest_response.status_code != 200:
            print(f"Failed to retrieve manifest for {args.image}:{args.tag}")
            return

        manifest_data = manifest_response.json()

        # 计算总大小
        total_size = sum(layer['size'] for layer in manifest_data.get('layers', []))

        # 获取更新时间
        update_time = _get_image_update_time(args.image, args.tag)
        # 打印结果 - 使用print_dict美化输出
        if args.size and args.update:
            image_info = {
                f"{args.image}:{args.tag}": f"{total_size} bytes ({total_size / (1024 * 1024):.2f} MB)",
                "Last Updated": update_time or "Unknown"
            }
            print_dict(image_info, headers=['Image', 'Value'], property='Image')
        elif args.size:
            image_info = {
                f"{args.image}:{args.tag}": f"{total_size} bytes ({total_size / (1024 * 1024):.2f} MB)"
            }
            print_dict(image_info, headers=['Image', 'Size'], property='Image')
        elif args.update:
            image_info = {
                f"{args.image}:{args.tag}": update_time or "Unknown"
            }
            print_dict(image_info, headers=['Image', 'Last Updated'], property='Image')
        else:
            # 只显示镜像名
            image_info = {
                f"{args.image}:{args.tag}": ""
            }
            print_dict(image_info, headers=['Image', 'Info'], property='Image')

        return

    # 使用print_list打印标签列表
    if 'tags' in data and data['tags']:
        # 创建一个简单的对象列表，每个对象有一个tag属性
        class Tag:
            def __init__(self, tag):
                self.tag = tag

        tags = [Tag(tag) for tag in data['tags']]
        print_list(tags, ['tag'])
    else:
        print(f"No tags found for image '{args.image}'.")
