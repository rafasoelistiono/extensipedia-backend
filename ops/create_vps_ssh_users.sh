#!/usr/bin/env bash
set -euo pipefail

# Run as root on the VPS.
# This provisions SSH users that mirror the dashboard roles defined in the app:
# - superadmin
# - akademik
# - kompetensi
# - advokasi
# Plus one deployment user:
# - extensipedia
#
# Important:
# - Do not hardcode passwords in this file.
# - Prefer SSH keys.
# - Replace each *_PUBKEY value before running.

declare -A PUBKEYS=(
  [extensipedia]="REPLACE_WITH_DEPLOY_PUBLIC_KEY"
  [superadmin]="REPLACE_WITH_SUPERADMIN_PUBLIC_KEY"
  [akademik]="REPLACE_WITH_AKADEMIK_PUBLIC_KEY"
  [kompetensi]="REPLACE_WITH_KOMPETENSI_PUBLIC_KEY"
  [advokasi]="REPLACE_WITH_ADVOKASI_PUBLIC_KEY"
)

create_user() {
  local username="$1"
  local pubkey="$2"

  if id "$username" >/dev/null 2>&1; then
    echo "User '$username' already exists; ensuring SSH config is present."
  else
    adduser --disabled-password --gecos "" "$username"
  fi

  install -d -m 700 -o "$username" -g "$username" "/home/$username/.ssh"
  touch "/home/$username/.ssh/authorized_keys"
  chown "$username:$username" "/home/$username/.ssh/authorized_keys"
  chmod 600 "/home/$username/.ssh/authorized_keys"

  if [[ "$pubkey" == REPLACE_WITH_* ]]; then
    echo "Skipping key install for '$username' because the public key placeholder was not replaced."
    return
  fi

  if ! grep -qxF "$pubkey" "/home/$username/.ssh/authorized_keys"; then
    printf '%s\n' "$pubkey" >>"/home/$username/.ssh/authorized_keys"
  fi
}

for username in "${!PUBKEYS[@]}"; do
  create_user "$username" "${PUBKEYS[$username]}"
done

# Allow only the deployment user to use sudo by default.
usermod -aG sudo extensipedia

echo
echo "Provisioning finished."
echo "Next steps:"
echo "1. Replace SSH key placeholders and re-run if needed."
echo "2. Test each account with SSH keys."
echo "3. After verification, consider disabling PasswordAuthentication in sshd_config."
