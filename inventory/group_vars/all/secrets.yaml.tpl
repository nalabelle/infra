---
nextdns_id: op://Applications/NextDNS/ID
wireguard:
  hosts:
    twain:
      PrivateKey: op://Applications/WIREGUARD_TWAIN/password
      PublicKey: op://Applications/WIREGUARD_TWAIN/username
      Endpoint: op://Applications/WIREGUARD_TWAIN/Endpoint
      Address: op://Applications/WIREGUARD_TWAIN/Address
      peers:
        euclid:
          PublicKey: op://Applications/WIREGUARD_EUCLID/username
          PresharedKey: op://Applications/WIREGUARD_EUCLID/PRESHAREDKEY/TWAIN
          AllowedIPs: op://Applications/WIREGUARD_EUCLID/AllowedIPs
        mobile_p6an:
          PublicKey: op://Applications/WIREGUARD_MOBILE_P6AN/username
          PresharedKey: op://Applications/WIREGUARD_MOBILE_P6AN/PRESHAREDKEY/TWAIN
          AllowedIPs: op://Applications/WIREGUARD_MOBILE_P6AN/AllowedIPs
        travel:
          PublicKey: op://Applications/WIREGUARD_TRAVEL/username
          PresharedKey: op://Applications/WIREGUARD_TRAVEL/PRESHAREDKEY/TWAIN
          AllowedIPs: op://Applications/WIREGUARD_TRAVEL/AllowedIPs
bulk_storage:
  username: op://Applications/BULK_STORAGE/username
  password: op://Applications/BULK_STORAGE/password
  local_path: op://Applications/BULK_STORAGE/local_path
  remote_path: op://Applications/BULK_STORAGE/remote_path
  type: op://Applications/BULK_STORAGE/type
  options: op://Applications/BULK_STORAGE/options
email:
  mta: op://Applications/MAILX/password
  domain: op://Applications/MAILX/domain
unattended_mail: "unattended-upgrades@{{ op://Applications/MAILX/domain }}"
