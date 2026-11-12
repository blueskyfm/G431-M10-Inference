#!/usr/bin/env bash
# Reads system state; writes only a new, private local diagnostics directory.
# No flashing, PCI configuration writes, GPU resets or setting changes.
set -u
umask 077
out=$(mktemp -d "${TMPDIR:-/tmp}/g431-m10-diagnostics.XXXXXXXX") || exit 1
capture() {
  local file="$1"
  shift
  if command -v "$1" >/dev/null 2>&1; then
    "$@" > "$out/$file" 2>&1
    local status=$?
    printf '%s exit=%s
' "$file" "$status" >> "$out/status.txt"
  else
    printf 'Unavailable command: %s
' "$1" > "$out/$file"
  fi
}
capture kernel.txt uname -r
capture os.txt cat /etc/os-release
capture pci-tree.txt lspci -Dtv
capture pci-devices.txt lspci -Dnn
capture pci-resources.txt lspci -Dvvnn
capture gpu-list.txt nvidia-smi -L
capture gpu-summary.txt nvidia-smi --query-gpu=pci.bus_id,name,driver_version,memory.total --format=csv
for field in system-product-name baseboard-product-name bios-version bios-release-date; do
  capture "dmi-$field.txt" dmidecode -s "$field"
done
# Permission failures are recorded. Run with sudo only if you want kernel/DMI logs.
capture kernel-log.txt dmesg --color=never
printf 'Saved: %s
Review files before sharing: kernel logs and GPU listings may contain identifiers or system details. Nothing was uploaded.
' "$out"
