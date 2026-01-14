#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from {{cookiecutter.project_slug}}.common import cliutils
from {{cookiecutter.project_slug}} import base


class ListExtManager(base.Manager):
    """Manager for listing tags of a relevant repository."""

    def get_digest(self, image_name, tag):
        """Get digest for an image tag."""
        url = "/v2/%s/manifests/%s" % (image_name, tag)
        response = self._get(url, return_response=True)
        return response.headers.get("Docker-Content-Digest")


@cliutils.arg('image', metavar='<image>', help='Image name to show details for')
@cliutils.arg('--tag', dest='tag_name', action='store', default=None,
              help='Tag name to get digest for')
@cliutils.arg('--digest', dest='get_digest', action='store_true', default=False,
              help='Get digest for the specified tag')
def do_image_digest(cs, args):
    """
    Show details for a specific image.
    Use --tag to get digest for a specific tag.
    Use --digest to get digest for the specified tag.
    """
    if not getattr(args, 'image', None):
        print("Usage: image-digest <image>")
        print("See '{{cookiecutter.command_name}} help image-digest' for help on this command.")
        return

    if getattr(args, 'tag_name', None) and getattr(args, 'get_digest', False):
        digest = cs.list_extensions.get_digest(args.image, args.tag_name)
        if digest:
            cliutils.print_dict({'digest': digest})
        else:
            print("Digest not found for image %s tag %s" % (args.image, args.tag_name))
