//Wrapper for zfs command
package storage

import (
	"bytes"
	"cloud/functions"
	"errors"
	"fmt"
	"io"
	"os/exec"
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

//find dataset
func Find(name string) (Dataset, error) {
	lst, err := List(name, "all")
	if err != nil {
		return Dataset{}, err
	}
	for _, ds := range lst {
		if ds.Name == name {
			return ds, nil
		}
	}
	return Dataset{}, errors.New("Dataset " + name + " not found")
}

//Receive snapshot
// func Receive(stream io.Reader, name string) error {
func Receive(stream DatasetStream) error {
	sh := exec.Command("zfs", "receive", stream.Name)
	var out, errstr bytes.Buffer
	sh.Stdout = &out
	_, err := io.Copy(stream.Stream, sh.Stdin)
	if err != nil {
		return err
	}
	sh.Stderr = &errstr
	err = sh.Run()
	if err != nil || len(errstr.String()) > 0 {
		return errors.New(err.Error() + ", " + errstr.String())
	}
	return nil
}

type DatasetStream struct {
	Stream io.Writer
	Name   string
}
type Dataset struct {
	Name string
}

func (ds *Dataset) Snapshot(name string) error {
	res, err := functions.ExecShell(
		"zfs",
		"snapshot",
		ds.Name+"@"+name,
	)
	if err != nil {
		return err
	}
	//DEBUG:
	fmt.Println("snapshot result:", res)
	return nil
}

func (ds *Dataset) Destroy() error {
	res, err := functions.ExecShell(
		"zfs",
		"destroy",
		ds.Name,
	)
	if err != nil {
		return err
	}
	//DEBUG:
	fmt.Println("snapshot result:", res)
	return nil
}
func (ds *Dataset) IsSnapshot() bool {
	return strings.Contains(ds.Name, "@")
}

func (ds *Dataset) Send() (DatasetStream, error) {
	if ds.IsSnapshot() == false {
		return DatasetStream{}, errors.New("Dataset " + ds.Name + " is not a snapshot")
	}
	sh := exec.Command("zfs", "send", ds.Name)
	var errstr bytes.Buffer
	sh.Stderr = &errstr
	err := sh.Run()
	if err != nil || len(errstr.String()) > 0 {
		return DatasetStream{}, errors.New(err.Error() + ", " + errstr.String())
	}
	return DatasetStream{Stream: sh.Stdout, Name: ds.Name}, nil
}
