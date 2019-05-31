# WoW @ Prologin Finals

This repo explains how to setup World of Warcraft during the Prologin finals.

## WoW 3.3.5a

You'll need to find a way to retrieve the WoW 3.3.5a client, and put it both on
misc (to extract maps/vmaps/...) and on rhfs01 (to deploy it to the clients).

## Server

### MDB

Add the alias "wow" to the misc machine on MDB.

### Prepare the base system

On the Misc machine, with the user "root":

    pacman -Sy mariadb cmake boost
    mysql_install_db --user=mysql --basedir=/usr --datadir=/var/lib/mysql
    systemctl enable --now mariadb
    mysql_secure_installation

    useradd -m mangos
    usermod -G udbsync_public mangos

### CMangos compilation and installation

Change to the mangos user:

    su mangos

Then follow the instructions here:
https://github.com/cmangos/issues/wiki/Installation-Instructions

### Systemd services

Copy and start the systemd services from this server:

    for s in wow-mangosd wow-realmd udbsync_mangos; do
        cp $s.service /etc/systemd/system
        systemctl enable --now $s
    done

### Realmlist setup

    mysql -u mangos -p wotlkrealmd
    UPDATE realmlist SET name = 'Prologin', address = 'wow.prolo' WHERE id = 1;


## Client

First, on rhfs01, copy the WoW wotlk 3.3.5a client in
`/export/nfsroot_staging/opt/wotlk3.3.5a/`.

Copy the WTF/Realmlist configuration files, and the wrapper script:

    cp realmlist.wtf /export/nfsroot_staging/opt/wotlk3.3.5a/Data/enUS
    mkdir -p /export/nfsroot_staging/opt/wotlk3.3.5a/WTF
    cp Config.wtf /export/nfsroot_staging/opt/wotlk3.3.5a/WTF
    cp wow /export/nfsroot_staging/usr/bin

Then, install the dependencies (you might need to enable multilib in
pacman.conf):

    pacman --root /export/nfsroot_staging -S wine

You can then sync the rhfs and you should be good to go. Launch "wow" and
connect yourself with your UDB stuff.
