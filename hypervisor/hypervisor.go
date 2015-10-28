package hypervisor

import (
	"cloud/functions"
	"errors"
	"log"
	"strings"
)

func IsHypervisor() (bool, error) {
	res, err := functions.ExecShell("which", []string{"virsh"})
	if err != nil {
		return false, err
	} else {
		if len(res) > 0 {
			return true, nil
		}
	}
	return false, nil
}

type Vm struct {
	Name      string
	Host      string
	State     string
	ImagePath string
}

func (vm *Vm) Migrate(toHost string) error {
	//TODO check if host is running
	//TODO check if dest. server is up
	str, err := functions.ExecShell("virsh", []string{
		"--live --unsafe", vm.Name, "qemu+tcp://" + toHost + "/system"})
	log.Println(str, err)
	return nil
}

type Hypervisor struct{}

func (h *Hypervisor) VmList(par string, reply *[]Vm) error {
	err := VmList(reply)
	if err != nil {
		return err
	}
	return nil
}

func VmList(vms *[]Vm) error {
	str, err := functions.ExecShell("virsh", []string{"list"})
	if err != nil {
		return err
	}
	localhost, err := functions.GetLocalhostName()
	lines := strings.Split(str, "\n")
	lines = lines[2:]
	for _, l := range lines {
		if len(l) > 0 {
			fields := strings.Fields(l)
			v := Vm{
				Name:  fields[1],
				Host:  localhost,
				State: fields[2],
			}
			v.ImagePath, err = GetImagePath(v.Name)
			*vms = append(*vms, v)
		}
	}
	return nil
}

func GetImagePath(vmName string) (string, error) {
	str, err := functions.ExecShell("virsh", []string{"domblklist", vmName})
	if err != nil {
		return "", err
	}
	lines := strings.Split(str, "\n")
	fields := strings.Fields(lines[2])
	return fields[1], nil
}

func FindVm(vmName string) (Vm, error) {
	lst := []Vm{}
	err := VmList(&lst)
	if err != nil {
		return Vm{}, err
	}
	var ret Vm
	var found bool = false
	for _, v := range lst {
		if v.Name == vmName {
			ret = v
			found = true
		}
	}
	if found {
		return ret, nil
	}
	return Vm{}, errors.New("Vm " + vmName + " not found.")
}
