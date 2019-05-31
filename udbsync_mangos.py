# -*- encoding: utf-8 -*-
# Copyright (c) 2019 Antoine Pietri <antoine.pietri@prologin.org>
# Copyright (c) 2019 Association Prologin <info@prologin.org>
#
# Prologin-SADM is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Prologin-SADM is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Prologin-SADM.  If not, see <http://www.gnu.org/licenses/>.

import functools
import hashlib
import logging
import os
import sqlalchemy
import sqlalchemy.orm.session
import sqlalchemy.ext.declarative
import sys
import prologin.config
import prologin.log
import prologin.udbsync.client


def callback(users, updates_metadata):
    # Reconnect everytime
    engine = sqlalchemy.create_engine('mysql://mangos:mangos@localhost/wotlkrealmd')
    Session = sqlalchemy.orm.session.sessionmaker(bind=engine)
    Base = sqlalchemy.ext.declarative.declarative_base()
    s = Session()

    class Account(Base):
        __table__ = sqlalchemy.Table(
                'account', Base.metadata, autoload=True,
                autoload_with=engine)

    logging.info("Got events: %r", updates_metadata)
    try:
        for login, status in updates_metadata.items():
            found_users = s.query(Account).filter(Account.username == login)
            username = login.upper()
            pwstring = '{}:{}'.format(login.upper(), users[login]['password'].upper())
            password = hashlib.sha1(pwstring.encode()).hexdigest().upper()
            gmlevel = {'root': 3, 'orga': 1, 'user': 0}[users[login]['group']]
            expansion = 2

            if status in ('created', 'updated'):
                user = found_users.first()
                if user:
                    user.username = username
                    user.sha_pass_hash = password
                    user.gmlevel = gmlevel
                    user.expansion = 2
                else:
                    user = Account(username=username, sha_pass_hash=password, gmlevel=gmlevel, expansion=expansion)
                s.merge(user)

            if status == 'deleted':
                found_users.delete(synchronize_session=False)

        s.commit()
    except Exception:
        logging.exception('Exception: ')
        s.rollback()
    finally:
        s.close()


if __name__ == '__main__':
    prologin.log.setup_logging('udbsync_mangos')
    prologin.udbsync.client.connect().poll_updates(callback)
