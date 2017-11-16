package storage

import (
	// "fmt"
	"errors"

	"github.com/jmu0/cloud/functions"
	// "log"
	// "io"
	"os"
	"strings"
)

//storage struct for use with rpc
type Storage struct{}

//get shares, use with rpc
func (s *Storage) GetShares(opt string, shares *[]Share) error {
	var err error
	*shares, err = GetShares()
	return err
}

//get mounts, use with rpc
func (s *Storage) GetMounts(opt string, mounts *[]Mount) error {
	var err error
	*mounts, err = GetMounts()
	return err
}

//mount share on server
func (s *Storage) MountShare(sharestring string, reply *string) error {
	sh := Share{}
	err := sh.FromShareString(sharestring)
	if err != nil {
		return err
	}
	*reply = sharestring + " mounted"
	return sh.Mount()
}

//receive zfs dataset, use with rpc
func (s *Storage) ReceiveZfsSnapshot(stream DatasetStream, result *string) error {
	*result = "DEBUG: from ReceiveZfsSnapshot"
	return Receive(stream)
}

//structure to store properties for nfs share
type Share struct {
	Name    string
	Path    string
	Host    string
	Network string
	Options string
}

//get share fields from line in /etc/exports
func (s *Share) FromLine(line string) {
	tmp1 := strings.Fields(line)
	s.Path = tmp1[0]
	tmp2 := strings.Split(tmp1[1], "(")
	s.Network = tmp2[0]
	s.Options = tmp2[1][:len(tmp2[1])-1]
	s.Host, _ = functions.GetLocalhostName()
	if s.Path[len(s.Path)-1:] == "/" {
		s.Path = s.Path[:len(s.Path)-1]
	}
	tmp3 := strings.Split(s.Path, "/")
	s.Name = tmp3[len(tmp3)-1]
}

//get share fields from share string (server:path)
func (s *Share) FromShareString(share string) error {
	tmp1 := strings.Split(share, ":")
	if len(tmp1) != 2 {
		return errors.New("invalid share: " + share)
	}
	s.Host = tmp1[0]
	s.Path = tmp1[1]
	if s.Path[len(s.Path)-1:] == "/" {
		s.Path = s.Path[:len(s.Path)-1]
	}
	tmp2 := strings.Split(s.Path, "/")
	s.Name = tmp2[len(tmp2)-1]
	return nil
}

//create line for in /etc/exports
func (s *Share) ToLine() string {
	var line string
	line = s.Path
	if s.Network == "" {
		s.Network = "10.0.0.1/24"
	}
	if s.Options == "" {
		s.Options = "rw,sync,subtree_check,no_root_squash"
	}
	line += " " + s.Network
	line += "(" + s.Options + ")"
	return line
}

//mount share
func (s *Share) Mount() error {
	mountpoint := "/mnt/" + s.Host + "/" + s.Name
	share := s.Host + ":" + s.Path
	if functions.PathExists(mountpoint) == false {
		err := os.MkdirAll(mountpoint, 0770)
		if err != nil {
			return err
		}

	}
	// _, err := functions.ExecShell("mount", []string{share, mountpoint})
	_, err := functions.ExecShell("mount", share, mountpoint)
	if err != nil {
		return err
	}
	return nil
}

//structure to store properties for mounts
type Mount struct {
	Name       string
	Share      string
	SharePath  string
	ShareHost  string
	MountPoint string
	MountHost  string
}

//create mount from line in df
func (m *Mount) FromLine(line string) {
	fields := strings.Fields(line)
	m.Share = fields[0]
	tmp := strings.Split(m.Share, ":")
	m.ShareHost = tmp[0]
	m.SharePath = tmp[1]
	m.MountPoint = fields[5]
	m.MountHost, _ = functions.GetLocalhostName()
	tmp = strings.Split(m.Share, "/")
	m.Name = tmp[len(tmp)-1]
}

//returns if localhost is nfs server
func IsNfsServer() (bool, error) {
	// res, err := functions.ExecShell("pgrep", []string{"nfsd"})
	res, err := functions.ExecShell("pgrep", "nfsd")
	if err != nil {
		return false, nil
	} else {
		if len(res) > 0 {
			return true, nil
		}
	}
	return false, nil
}

//get shares on local server
func GetShares() ([]Share, error) {
	txt, err := functions.ReadFile("/etc/exports")
	if err != nil {
		return []Share{}, err
	}
	lines := strings.Split(txt, "\n")
	shares := []Share{}
	for _, l := range lines {
		if len(l) > 0 && l[:1] != "#" {
			s := Share{}
			s.FromLine(l)
			shares = append(shares, s)
		}
	}
	return shares, nil
}

//check if a path is shared
func IsShared(path string) (bool, error) {
	sh, err := GetShares()
	if err != nil {
		return false, err
	}
	for _, s := range sh {
		if s.Path == path {
			return true, nil
		}
	}
	return false, nil
}

//get mounts on local server
func GetMounts() ([]Mount, error) {
	mounts := []Mount{}
	// txt, err := functions.ExecShell("df", []string{"-h", "-t", "nfs", "-t", "nfs4"})
	txt, err := functions.ExecShell("df", "-h", "-t", "nfs", "-t", "nfs4")
	if err == nil {
		lines := strings.Split(txt, "\n")
		for _, l := range lines[1:] {
			if len(l) > 0 {
				m := Mount{}
				m.FromLine(l)
				mounts = append(mounts, m)
			}
		}
	}
	return mounts, nil
}

//create nfs share from folder
func CreateShare(path string) (Share, error) {
	if path[len(path)-1:] == "/" {
		path = path[:len(path)-1]
	}
	tmp := strings.Split(path, "/")
	host, _ := functions.GetLocalhostName()
	s := Share{
		Host: host,
		Name: tmp[len(tmp)-1],
		Path: path,
	}
	if ok, _ := IsNfsServer(); ok {
		if _, err := os.Stat(path); os.IsNotExist(err) {
			return s, errors.New("Path " + path + " does not exist")
		}
		isshared, err := IsShared(path)
		if err != nil {
			return s, err
		}
		if isshared {
			return s, errors.New(path + " is already shared")
		}
		err = functions.AppendToFile("/etc/exports", s.ToLine()+"\n")
		if err != nil {
			return s, err
		}
		// _, err = functions.ExecShell("exportfs", []string{"-rav"})
		_, err = functions.ExecShell("exportfs", "-rav")
		if err != nil {
			return s, err
		}

	} else {
		return s, errors.New("not a nfs server")
	}
	return s, nil
}
