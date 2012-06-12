#!/usr/bin/env python

import os
import logging
import shutil
from liquidluck.options import g, settings
from liquidluck.utils import UnicodeDict, walk_dir
from liquidluck.writers.base import BaseWriter, Pagination, linkmaker
from liquidluck.writers.base import get_post_slug, slug_to_destination


class PostWriter(BaseWriter):
    def destination_of_post(self, post):
        slug = get_post_slug(post, settings.permalink)
        return os.path.join(g.output_directory, slug_to_destination(slug))

    def run(self):
        for post in g.public_posts:
            self.render(
                {'post': post}, 'post.html', self.destination_of_post(post)
            )

        for post in g.secure_posts:
            self.render(
                {'post': post}, 'post.html', self.destination_of_post(post)
            )

        logging.info('PostWriter Finished')


class ArchiveWriter(BaseWriter):
    def __init__(self):
        if 'archive' in settings.writers_variables:
            self._destination = settings.writers_variables['archive']
        else:
            self._destination = 'index.html'

    def run(self):
        pagination = Pagination(g.public_posts, 1, settings.perpage)
        dest = os.path.join(g.output_directory, self._destination)
        self.render({'pagination': pagination}, 'archive.html', dest)

        for page in range(1, pagination.pages + 1):
            pagination = Pagination(g.public_posts, page, settings.perpage)
            dest = os.path.join(g.output_directory, 'page/%s.html' % page)
            self.render({'pagination': pagination}, 'archive.html', dest)

        logging.info('ArchiveWriter Finished')


class ArchiveFeedWriter(BaseWriter):
    def run(self):
        feed = UnicodeDict()
        feed.posts = g.public_posts[:settings.feedcount]
        feed.feedurl = linkmaker('feed.xml')
        feed.url = g.siteurl
        dest = os.path.join(g.output_directory, 'feed.xml')
        self.render({'feed': feed}, 'feed.xml', dest)


class FileWriter(BaseWriter):
    def run(self):
        l = len(g.source_directory) + 1
        for f in g.pure_files:
            path = f[l:]
            dest = os.path.join(g.output_directory, path)
            copy_to(f, dest)

        logging.info('FileWriter Finished')


class StaticWriter(BaseWriter):
    def run(self):
        static_path = os.path.join(g.theme_directory, 'static')
        l = len(static_path) + 1
        for f in walk_dir(static_path):
            path = f[l:]
            dest = os.path.join(g.static_directory, path)
            copy_to(f, dest)

        logging.info('StaticWriter Finished')


def copy_to(source, dest):
    if os.path.exists(dest) and \
       os.stat(source).st_mtime <= os.stat(dest).st_mtime:
        return

    folder = os.path.split(dest)[0]
    # on Mac OSX, `folder` == `FOLDER`
    # then make sure destination is lowercase
    if not os.path.isdir(folder):
        os.makedirs(folder)

    shutil.copy(source, dest)
    return
