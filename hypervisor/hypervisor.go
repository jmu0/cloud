package hypervisor

import (
	f "cloud/functions"
)

func IsHypervisor() (bool, error) {
	res, err := f.ExecShell("which", []string{"virsh"})
	if err != nil {
		return false, err
	} else {
		if len(res) > 0 {
			return true, nil
		} else {
			return false, nil
		}
	}
}
