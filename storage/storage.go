package storage

import (
	f "cloud/functions"
)

func IsNfsServer() (bool, error) {
	res, err := f.ExecShell("pgrep", []string{"nfsd"})
	if err != nil {
		return false, nil
	} else {
		if len(res) > 0 {
			return true, nil
		}
	}
	return false, nil
}
