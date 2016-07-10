# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.ssh.forward_x11 = true # useful since some audio testing programs use x11
  config.vm.box = "precise64"
  config.vm.box_url = "http://files.vagrantup.com/precise64.box"
  config.vm.network "forwarded_port", guest: 8000, host: 8000
  config.vm.provider "virtualbox" do |vb|
    vb.memory = "512"
    vb.customize ["modifyvm", :id, '--audio', 'dsound', '--audiocontroller', 'ac97']
  end
  config.vm.provision "shell", inline: <<-SHELL
    apt-get update
    apt-get install -y mpd mpc python-pip screen python-dev python-setuptools libffi-dev
    cd /vagrant
    pip install -U setuptools
    pip install -r requirements.txt
  SHELL
  config.vm.provision :shell, :inline => $BOOTSTRAP_SCRIPT
end

$BOOTSTRAP_SCRIPT = <<EOF
  set -e # Stop on any error

  # --------------- SETTINGS ----------------
  # Other settings
  export DEBIAN_FRONTEND=noninteractive

  sudo apt-get update

  # ---- OSS AUDIO
  sudo usermod -a -G audio vagrant
  sudo apt-get install -y oss4-base oss4-dkms oss4-source oss4-gtk linux-headers-3.2.0-23 debconf-utils
  sudo ln -s /usr/src/linux-headers-$(uname -r)/ /lib/modules/$(uname -r)/source || echo ALREADY SYMLINKED
  sudo module-assistant prepare
  sudo module-assistant auto-install -i oss4 # this can take 2 minutes
  sudo debconf-set-selections <<< "linux-sound-base linux-sound-base/sound_system select  OSS"
  echo READY.

  # have to reboot for drivers to kick in, but only the first time of course
  if [ ! -f ~/runonce ]
  then
    sudo reboot
    touch ~/runonce
  fi
EOF