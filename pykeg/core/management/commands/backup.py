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

from django.core.management.base import NoArgsCommand
from pykeg.core import backup

class Command(NoArgsCommand):
    help = u'Perform backup/restore functions.'

    """Creates a zip file in /media/backups w/ following parameters:
    All date values are in UTC/GMT.
    All values in brackets are dependent on Kegbot Site Settings

    Title: [KegbotSiteTitle]_YYYYMMDDHHMMSS.zip
    Contents:
        /[KegbotSiteTitle]_YYYYMMDDHHMMSS
            /metadata.json
                archive_name : [KegbotSiteTitle]_YYYYMMDDHHMMSS
                datetime : YYYY-MM-DDTHH:MM:SSZ
                db_table_count : [number of json files corresponding to data tables in dB]
                picture_count : [number of photos in /media/pics]
                server_name : [KegbotSiteTitle]
                server_version : [version of Kegbot Server]
            /database (w/ some unnecessary tables blacklisted)
                [table_name].json <= One for each table in the database
            /media (w/ required folders whitelisted)
                /pics
                    [filename.jpg/png/etc] < 1:1 photo dump from /media/pics
    """

    def handle(self, **options):
        print 'Backup in progress'
        location = backup.backup()
        print 'Backup complete! Zip file saved to:'
        print location
