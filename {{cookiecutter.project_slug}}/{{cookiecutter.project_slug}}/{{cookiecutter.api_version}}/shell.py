#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
from {{cookiecutter.project_slug}}.common import cliutils
from {{cookiecutter.project_slug}}.common import exceptions as exp


@cliutils.arg('--detail', '-d', dest="detail", action="store_true",
              help='show detail info.List every image together with all of its tags')
def do_image_list(cs, args):
    """
    List all images in the registry.
    Use --details to list every image together with all of its tags.
    """
    images = cs.images.list()
    image_names = images.get('repositories', [])

    if args.detail:
        images_tags_list = []
        images_tags_dict = {}
        for img in image_names:
            tag_data = cs.images.list_tags(img)
            tags = ', '.join(tag_data.get('tags', []))
            images_tags_dict[img] = tags
            images_tags_list.append({'image': img, 'tags': tags})
        cliutils.print_list(images_tags_list, fields=['image', 'tags'])

    else:
        images_dict = {
            "images": image_names
        }
        # print(images_dict)
        cliutils.print_dict(images_dict)


@cliutils.arg('repository', metavar='<repository>', help='Name of repository.')
def do_tags_list(cs, args):
    """Get tags of a relevant repository."""
    image_tags_list = []
    tags = cs.images.list_tags(args.repository)
    image_tags_list.append(tags)
    # print(tags)
    fields = ["name", 'tags']
    cliutils.print_list(image_tags_list, fields, order_by="name")


@cliutils.arg('image', metavar='<image>', help='Image name to show details for')
@cliutils.arg('--tag', dest='tag_name', action='store', default=None,
              help='Tag name to get digest for')
def do_image_show(cs, args):
    """
    Show details for a specific image.
    Use --tag to get digest for a specific tag.
    """
    if not getattr(args, 'image', None):
        print("Usage: image-show <image>")
        print("See '{{cookiecutter.project_slug}} help image-show' for help on this command.")
        return

    try:
        # Get tag data for the specified image
        tag_data = cs.images.list_tags(args.image)
        tags = tag_data.get('tags', [])
        image_info = {
            "image": args.image,
            "tags": tags
        }
        cliutils.print_list([image_info], fields=['image', 'tags'])
    except Exception as e:
        print(f"Error retrieving image details: {e}")
