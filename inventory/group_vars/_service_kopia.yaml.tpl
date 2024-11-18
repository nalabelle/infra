kopia_server:
  username: "{{ op://Applications/KOPIA_SERVER/username }}"
  sync:
    bucket: "{{ op://Applications/KOPIA_SERVER/sync/bucket }}"
    key_id: "{{ op://Applications/KOPIA_SERVER/sync/key_id }}"
    key: "{{ op://Applications/KOPIA_SERVER/sync/key }}"
  ssl:
    cert: "{{ op://Applications/KOPIA_SERVER/ssl/cert }}"
    key: "{{ op://Applications/KOPIA_SERVER/ssl/key }}"
