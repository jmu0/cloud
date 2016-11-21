package storage

import (
	"cloud/functions"
	// "fmt"
	"strings"
)

//returns list of datasets.
//filter: filter string for datasets
//dsType: filesystem, snapshot, snap, volume, bookmark, or all.
func List(filter string, dsType string) ([]Dataset, error) {
	var ret []Dataset = []Dataset{}
	retstr, err := functions.ExecShell(
		"zfs",
		"list",
		"-t",
		dsType,
		"-H",
		"-o",
		"name",
	)
	if err != nil {
		return []Dataset{}, err
	}
	lines := strings.Split(retstr, "\n")
	for _, line := range lines {
		if len(line) > 0 {
			if len(filter) > 0 {
				if strings.Contains(line, filter) {
					ret = append(ret, Dataset{Name: line})
				}
			} else {
				ret = append(ret, Dataset{Name: line})
			}
		}
	}
	return ret, nil
}

type Dataset struct {
	Name string
}
