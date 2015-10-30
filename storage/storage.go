package storage

import (
	"cloud/functions"
	// "fmt"
	"strings"
)

type Storage struct{}

//get shares, use with rpc
func (s *Storage) GetShares(opt string, shares *[]Share) error {
	var err error
	*shares, err = GetShares()
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
func (s *Share) ToLine() string {
	var line string
	line = s.Path
	line += " " + s.Network
	line += "(" + s.Options + ")"
	return line
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
