# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.ssh.forward_x11 = true # useful since some audio testing programs use x11
  config.ssh.forward_agent = true
  config.vm.box = "ubuntu/trusty64"
  config.vm.network "forwarded_port", guest: 8000, host: 8000
  config.vm.provider "virtualbox" do |vb|
    vb.memory = "512"
    vb.customize ["modifyvm", :id, '--audio', 'dsound', '--audiocontroller', 'ac97']
  end
  config.vm.provision "shell", inline: <<-SHELL
    apt-get update
    apt-get install -y mpd mpc python-pip screen python-dev python-setuptools libffi-dev postgresql-server-dev-9.3 postgresql-9.3
    echo "snd-bcm2835" >> /etc/modules
    cd /vagrant
    pip install -U setuptools
    pip install -r requirements.txt
  SHELL
  config.vm.provision :shell, :inline => $BOOTSTRAP_SCRIPT
end

$BOOTSTRAP_SCRIPT = <<EOF
  sudo apt-get update
  sudo apt-get install -y dkms

  wget http://ppa.launchpad.net/ubuntu-audio-dev/alsa-daily/ubuntu/pool/main/o/oem-audio-hda-daily-dkms/oem-audio-hda-daily-dkms_0.201509251532~ubuntu14.04.1_all.deb
  sudo dpkg -i oem-audio-hda-daily-dkms_0.201509251532~ubuntu14.04.1_all.deb
  rm oem-audio-hda-daily-dkms_0.201509251532~ubuntu14.04.1_all.deb
  sudo apt-get -y install python-dev ipython python-numpy python-matplotlib python-scipy cython alsa-utils paman
  sudo usermod -a -G audio vagrant
  reboot
EOF