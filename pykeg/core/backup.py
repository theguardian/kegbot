# Copyright 2014 Bevbot LLC, All Rights Reserved
#
# This file is part of the Pykeg package of the Kegbot project.
# For more information on Pykeg or Kegbot, see http://kegbot.org/
#
# Pykeg is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# Pykeg is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pykeg.  If not, see <http://www.gnu.org/licenses/>.

import os
import datetime
import isodate
import tempfile
import shutil
import json
import zipfile

from pykeg.core import models
from pykeg.core.util import get_version

from django.core.files.storage import get_storage_class
from django.core import serializers
from django.db.models import Q, get_app, get_models
from django.utils import timezone
from django.utils.text import slugify

from StringIO import StringIO


def backup():
    SKIPPED_TABLE_NAMES = [
        'django_session',
        'django_content_type',
        'auth_group',
        'auth_permission'
    ]

    MEDIA_WHITELIST = [
        'pics'
    ]

    storage = get_storage_class()()

    tempdir = tempfile.mkdtemp()
    fd, path = tempfile.mkstemp()
    
    site_slug = slugify(models.KegbotSite.get().title)
    date_str = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    backup_name = '{site_slug}_{date_str}'.format(**vars())
    zip_file = backup_name + '.zip'

    zip_top_dir = os.path.join(tempdir, backup_name)
    os.makedirs(zip_top_dir)
    database_file_dir = os.path.join(zip_top_dir, 'database')
    os.makedirs(database_file_dir)
    meta_filename = os.path.join(zip_top_dir, 'metadata.json')
    

    num_tables = 0
    for model in get_models():
        db_table = os.path.join(database_file_dir, model._meta.db_table + '.json')
        if model._meta.db_table not in SKIPPED_TABLE_NAMES:
            with open(db_table, 'w') as out:
                serializers.serialize('json', model.objects.all(), indent=2, stream=out)
            num_tables += 1

    zip_fd = os.fdopen(fd, 'w+b')
    zf = zipfile.ZipFile(zip_fd, 'w')

    num_pictures = 0
    #JUSTIN'S "LOCAL" METHOD
    # for dirname, subdirs, files in os.walk(storage.location):
    #     for filename in files:
    #         full_path = os.path.join(dirname, filename)
    #         full_subdir = full_path.replace(storage.location, '').replace(filename, '')
    #         if full_subdir in MEDIA_WHITELIST:
    #             zip_structure = backup_name + '/media' + full_subdir + filename
    #             zf.write(os.path.join(dirname, filename), zip_structure)
    #             num_pictures += 1

    srcfile = StringIO()
    for subdir in MEDIA_WHITELIST:
        subdirs, files = storage.listdir(subdir)
        for filename in files:
            zip_structure = backup_name + '/media/' + subdir + '/' + filename
            with storage.open(subdir + '/' + filename, mode='rb') as srcfile:
                zf.writestr(zip_structure, srcfile)
                #zf.write(dstfile, zip_structure)
                num_pictures += 1

    # MIKE'S "HINT" METHOD
    # def add_files(storage, dirname, destdir):
    #     """Recursively copies all files in `dirname` to `destdir`."""
    #     subdirs, files = storage.listdir(dirname)
    #     for filename in files:
    #         full_filename = os.path.join(dirname, filename)
    #         output_filename = os.path.join((destdir, full_filename))
    #         with storage.open(full_filename, 'r') as srcfile:
    #             with open(output_filename, 'w') as dstfile:
    #                 shutil.copyfileobj(srcfile, dstfile)
    #     for subdir in subdirs:
    #         add_files(storage, os.path.join((dirname, subdir)), destdir)

    metadata = {'server_name':models.KegbotSite.get().title,
        'server_version':get_version(),
        'datetime':isodate.datetime_isoformat(timezone.now()),
        'db_table_count':num_tables,
        'picture_count':num_pictures,
        'archive_name':zip_file}

    with open(meta_filename, 'w') as outfile:
        json.dump(metadata, outfile, sort_keys=True, indent=2)

    for dirname, subdirs, files in os.walk(tempdir):
        for filename in files:
            if filename == "metadata.json":
                zf.write(os.path.join(dirname, filename), backup_name + '/' + filename)
            else:
                zf.write(os.path.join(dirname, filename), backup_name + '/database/' + filename)

    zf.close()
    requested_filename = storage.get_available_name('backups/' + zip_file)
    actual_backup = storage.save(requested_filename, zip_fd)
    zip_fd.close()

    shutil.rmtree(tempdir)
    os.remove(path)

    return actual_backup
