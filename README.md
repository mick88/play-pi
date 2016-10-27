#play-pi

A frontend for a [Google Play Music](http://play.google.com/music/) Pi Jukebox. Play-pi will provide a web-frontend that can be used to browse and play your Google Music library.

![Screenshot: Now Playing](http://i.imgur.com/XbGadJU.png)

###Setup/Installation:

* Not covered in this guide: Setting up ssh/wireless/sound card. These topics are covered in this [lifehacker guide](http://lifehacker.com/5978594/turn-a-raspberry-pi-into-an-airplay-receiver-for-streaming-music-in-your-living-room).
* Assuming you've got the Pi set up as you want, you'll need to install the required tools:
`sudo apt-get install mpd mpc python-pip screen python-dev libssl-dev`
* Test that `mpc` is working by entering the command `sudo mpc`. You should see output like
*volume: 80%   repeat: off   random: off   single: off   consume: off*
There are [futher instructions for setting up/testing mpc](http://www.gmpa.it/it9xxs/?p=727) if you want them.
* Now clone this repository:
`git clone git://github.com/mick88/play-pi.git`
`cd play-pi`
* First, you'll need to update `pip`'s setuptools: `sudo pip install -U setuptools`
* Next you'll need to use it to install the required python packages:
`sudo pip install -r requirements.txt -c constraints.txt`
* Create admin account with `./manage.py createsuperuser`
* run `./manage.py setup` to setup access to your Google account
To get your device ID, dial `*#*#8255#*#*` on your Android phone, or have a look on the App Store - there are many apps that will display it for you. iOS users can use their device's uuid prepended by `ios:`.
It's highly recommended you use an [application specific password](https://support.google.com/accounts/answer/185833?hl=en) for this.
* Now set up the Django app with the following commands. This will create the database:
`./manage.py migrate`
* Now sync your Google Music library. This can take a very long time, just let it run:
`./manage.py init_gplay`
* You're now ready to roll! Start up a screen by typing `screen`. Running the server in the screen means that it will keep running after `ssh` is disconnected. You need to use `sudo` for this command if you want to use port 80 (recommended).
`sudo ./manage.py runserver 0.0.0.0:80`
* You should now be able to access play-pi from your web browser, point it at the IP of your Pi. You can go to `http://192.168.pi.ip/admin` and log in with your credentials to access the admin.

### Install as apache site
These instructions assume that the project is located in `/home/pi/src/play-pi` and you have user `pi`. If your setting is different, you will have to edit `play-pi.conf` and adjust the steps accordingly.

Follow steps listed in **Setup/Installation** first to install dependencies and setup the database.

* install apache2 and mod_wsgi: `sudo apt-get install apache2 libapache2-mod-wsgi`
* Symlink `play-pi.conf` to your sites available and enable:

    ```bash
    sudo ln -s /home/pi/src/play-pi/apache2/play-pi.conf /etc/apache2/sites-available/play-pi.conf
    sudo a2ensite play-pi
    ```
* Collect static files so they can be served by apache `./manage.py collectstatic --noinput`
* Restart apache `sudo apache2ctl graceful`
* If there are any errors you will find them in the apache error log: `/var/log/apache2/error.log`


### API
The project exposes REST API using Django Rest Framework. The API is located at `/api/`. 
All endpoints are open for GET requests without authentication. To make POST and DELETE requests, you need to [authenticate](http://www.django-rest-framework.org/tutorial/4-authentication-and-permissions/#authenticating-with-the-api). 
Available Endpoints:
- `/api/tracks/` - list of songs stored in Google Play Music 
- `/api/albums/` - list of albums stored in Google Play Music 
- `/api/playlists/` - list of playlists stored in Google Play Music 
- `/api/radio_stations/` - list of radio stations
- `/api/status/` - media player status. 
    - POST to this url to control playback, volume etc
- `/api/queue/` - playback queue, returns list of both tracks and radio stations in the queue. 
Available methods
    - POST - Add item to queue (insert at specific position with url `/api/queue/{id}`)
    - DELETE - clear queue (or delete item with specific mpd_id with url `/api/queue/{id}`)
- `/api/queue/current` - Currently played item in the queue 
- `/api/play/tracks` - play list of tracks POSTed to this url
- `/api/play/radios` - play list of radio stations POSTed to this url
- `/api/jump/{track|radio|next|previous}` - jump to item in playlist
    - POST `radio` or `track` instance to jump to the specific item.
    - POST `previous` or `next` without body to jump to the next/previous item relative to current one
- `/api/auth/login/` - login endpoint for token authentication

### Setup hardware interface
The project is capable of taking input from buttons connected to GPIO pins. You can configure connected buttons and assign them to actions in the admin backend:

* Connect buttons to GPIO pins and ground. If you don't know how to, refer to a [tutorial](http://razzpisampler.oreilly.com/ch07.html).
* Update button configuration in the admin back-end `/admin/hardware/gpiobutton/`
    * update BCM channels to the ones where each button is actually connected
    * enable the buttons you are using and leave others disabled
* Add button handler script to `init.d` on your raspberry pi: `sudo ln -s /home/pi/src/play-pi/radio_buttons.sh /etc/init.d/radio_buttons.sh` - if your project path is different, adjust the command
* Reboot your Raspberry Pi and your buttons should work
* **Advanced**: You can add more actions by implementing `on_X_press()` methods in `hardware.management.commands.gpio_buttons.Command`. 