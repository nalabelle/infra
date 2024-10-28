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
