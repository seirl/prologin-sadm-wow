# WoW @ Prologin Finals

This repo explains how to setup World of Warcraft during the Prologin finals.

## WoW 3.3.5a

You'll need to find a way to retrieve the WoW 3.3.5a client, and put it both on
misc (to extract maps/vmaps/...) and on rhfs01 (to deploy it to the clients).

The preferred location is `/opt/wow-3.3.5a`.

## CMangos Archlinux package

In the `pkg` folder, run:

    makepkg

Then upload the resulting package on the prologin repo (or `misc` directly).

## Server

### MDB

Add the alias "wow" to the misc machine on MDB.

### MySQL

On the misc machine, install mysql:

    pacman -Sy mariadb
    mysql_install_db --user=mysql --basedir=/usr --datadir=/var/lib/mysql
    systemctl enable --now mariadb
    mysql_secure_installation

### CMangos installation

Install the cmangos-wotlk-git package:

    pacman -S cmangos-wotlk-git

Extract the maps/vmaps/...:

    mangos-extract-resources /opt/wow-3.3.5a

### Database setup

Install the database schema:

    mysql -uroot -p < /usr/share/mangos/sql/create/db_create_mysql.sql
    cat /usr/share/mangos/sql/base/mangos.sql \
        /usr/share/mangos/sql/base/dbc/original_data/*.sql \
        /usr/share/mangos/sql/base/dbc/cmangos_fixes/*.sql |
            mysql -uroot -p --database=wotlkmangos
    mysql -uroot -p wotlkcharacters < /usr/share/mangos/sql/base/characters.sql
    mysql -uroot -p wotlkrealmd < /usr/share/mangos/sql/base/realmd.sql

Populate the database:

    git clone git://github.com/cmangos/wotlk-db.git
    pushd wotlk-db
    ./InstallFullDB.sh
    sed -i 's:CORE_PATH.\+$:CORE_PATH="/usr/share/mangos":' InstallFullDB.config
    ./InstallFullDB.sh
    popd

You also need to update the realm address and name:

    echo "UPDATE realmlist SET name = 'Prologin', address = 'wow.prolo' WHERE id = 1;" |
        mysql -u mangos -p wotlkrealmd

### Start the services

You can now enable and start the mangosd and realmd servers:

    systemctl enable --now realmd
    systemctl enable --now mangosd

### UDBSync

Setup udbsync for mangos:

    cp udbsync_mangos.py /usr/share/mangos
    cp udbsync_mangos.service /etc/systemd/system
    systemctl enable --now udbsync_mangos

## Client

First, on rhfs01, copy the WoW wotlk 3.3.5a client in
`/export/nfsroot_staging/opt/wow-3.3.5a/`.

Copy the WTF/Realmlist configuration files, and the wrapper script:

    cp realmlist.wtf /export/nfsroot_staging/opt/wow-3.3.5a/Data/enUS
    mkdir -p /export/nfsroot_staging/opt/wow-3.3.5a/WTF
    cp Config.wtf /export/nfsroot_staging/opt/wow-3.3.5a/WTF
    cp wow /export/nfsroot_staging/usr/bin

Then, install the dependencies (you might need to enable multilib in
pacman.conf):

    pacman --root /export/nfsroot_staging -S wine

You can then sync the rhfs and you should be good to go. Launch "wow" and
connect yourself with your UDB stuff.
