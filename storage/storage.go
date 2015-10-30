package storage

import (
	"cloud/functions"
	// "fmt"
	// "log"
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
	tmp3 := strings.Split(s.Path, "/")
	s.Name = tmp3[len(tmp3)-1]
}

//create line for in /etc/exports
func (s *Share) ToLine() string {
	var line string
	line = s.Path
	line += " " + s.Network
	line += "(" + s.Options + ")"
	return line
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
	res, err := functions.ExecShell("pgrep", []string{"nfsd"})
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

//get mounts on local server
func GetMounts() ([]Mount, error) {
	mounts := []Mount{}
	// txt, err := functions.ExecShell("df", []string{"-h -T -t nfs -t nfs4"})
	txt, err := functions.ExecShell("df", []string{"-h", "-t", "nfs", "-t", "nfs4"})
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
