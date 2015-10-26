package storage

import (
	f "cloud/functions"
)

func IsNfsServer() (bool, error) {
	res, err := f.ExecShell("pgrep", []string{"nfsd"})
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
