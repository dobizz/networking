# Networking
networking tools and scripts

## SSH
Install SSH on Ubuntu 20.04 LTS
```
sudo apt-get install ssh
sudo systemctl enable --now ssh
sudo systemctl status ssh
```

Generate RSA public-private keys
```
ssh-keygen -t rsa -b 4096 -C "name@domain.com"
```

This will generate id_rsa and id_rsa.pub, you can add/copy the public key on ~/.ss/authorized_keys file of the target machine for public key based authentication
