# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/trusty64"
  config.vm.network "forwarded_port", guest: 8000, host: 8000
  config.vm.provider "virtualbox" do |vb|
    vb.memory = "512"
    vb.customize ["modifyvm", :id, '--audio', 'dsound', '--audiocontroller', 'ac97']
  end
  config.vm.provision "shell", inline: <<-SHELL
    apt-get update
    apt-get install -y mpd mpc python-pip screen python-dev
    cd /vagrant
    pip install -U setuptools
    pip install -r requirements.txt
  SHELL
end
