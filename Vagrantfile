# -*- mode: ruby -*-
# vi: set ft=ruby :

VAGRANTFILE_API_VERSION = "2"
VAGRANTFILE_HOST_ADDRESS = "192.168.36.12"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.box = "precise64"

  # The url from where the 'config.vm.box' box will be fetched if it
  # doesn't already exist on the user's system.
  config.vm.box_url = "http://files.vagrantup.com/precise64.box"

  # Provision
  config.vm.provision :shell, :path => "provision/bootstrap.sh"

  config.vm.hostname = "chat"

  config.vm.network :forwarded_port, host: 80, guest: 80, auto_correct: true
  config.vm.network :forwarded_port, guest: 3306, host: 3306, auto_correct: true
  config.vm.network :private_network, ip: VAGRANTFILE_HOST_ADDRESS

  # config.vm.provider :virtualbox do |vb|
  #     vb.customize ['modifyvm', :id, '--memory', '1024']
  #     vb.customize ["modifyvm", :id, "--cpus", "1"]
  #     vb.customize ["modifyvm", :id, "--nictype1", "virtio"]
  #     vb.customize ["guestproperty", "set", :id, "/VirtualBox/GuestAdd/VBoxService/--timesync-set-threshold", 60000]
  # end

  # Shared folder
  config.vm.synced_folder "vagrant/", "/home/vagrant", create: true

  config.vm.provision :shell, inline: "echo Good job, now enjoy your new vbox: http://192.168.36.12"
  config.vm.provision :shell, inline: "echo Installing pip Requirements"
  config.vm.provision :shell, inline: "sudo pip install -r /vagrant/requirements.txt"
  config.vm.provision :shell, inline: "echo Starting Server"
  config.vm.provision :shell, inline: "python /vagrant/server.py &"
  config.vm.provision :shell, inline: "echo telnet 192.168.36.12 8181"
end