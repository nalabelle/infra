kopia_client__backup_schedule: "{{ op://Applications/KOPIA_$HOSTNAME/OnCalendar }}"
kopia_client__backup_destination: "{{ op://Applications/KOPIA_$HOSTNAME/destination }}"
kopia_client__hostname: "{{ op://Applications/KOPIA_$HOSTNAME/hostname }}"
{{ op://Applications/KOPIA_$HOSTNAME/snapshot-command }}
kopia_client__password: "{{ op://Applications/KOPIA_$HOSTNAME/password }}"
