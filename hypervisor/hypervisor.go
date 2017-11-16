package hypervisor

import (
	"errors"
	"log"
	"strings"

	"github.com/jmu0/cloud/functions"
)

func IsHypervisor() (bool, error) {
	// res, err := functions.ExecShell("which", []string{"virsh"})
	res, err := functions.ExecShell("which", "virsh")
	if err != nil {
		return false, nil
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

//migrate guest
func (vm *Vm) Migrate(toHost string) {
	log.Println("Migrating", vm.Name, "to", toHost, "...")
	/*
		in /etc/libvirt/libvirtd.conf:
			uncomment listen_tcp = 1
			tcp_port = "16509"
	*/
	// var cmd []string = []string{"migrate --live --unsafe " + vm.Name + " qemu+tcp://" + toHost + "/system"}
	// str, err := functions.ExecShell("virsh", cmd)
	str, err := functions.ExecShell("virsh", "migrate", "--live", "--unsafe", vm.Name, "qemu+tcp://"+toHost+"/system")
	if err != nil {
		log.Println("migrate error:", str, err)
	} else {
		log.Println("Migrated", vm.Name, "to", toHost)
	}
}

//shutdown guest
func (vm *Vm) Shutdown() {
	log.Println("Shutting down", vm.Name, "on", vm.Host, "...")
	// var cmd []string = []string{"shutdown " + vm.Name}
	// str, err := functions.ExecShell("virsh", cmd)
	str, err := functions.ExecShell("virsh", "shutdown", vm.Name)

	if err != nil {
		log.Println("Shutdown error:", str, err)
	} else {
		log.Println("Shut down", vm.Name, "on", vm.Host)
	}
}

//destroy guest
func (vm *Vm) Destroy() {
	log.Println("Destroying ", vm.Name, "on", vm.Host, "...")
	// var cmd []string = []string{"destroy " + vm.Name}
	// str, err := functions.ExecShell("virsh", cmd)
	str, err := functions.ExecShell("virsh", "destroy", vm.Name)
	if err != nil {
		log.Println("Destroy error:", str, err)
	} else {
		log.Println(vm.Name, "destroyed")
	}
}

type Hypervisor struct{}

//rpc method
func (h *Hypervisor) VmList(par string, reply *[]Vm) error {
	err := VmList(reply)
	if err != nil {
		return err
	}
	return nil
}

//migrate vm from this to dest.server
func (h *Hypervisor) MigrateVm(par string, reply *string) error {
	var pars []string = strings.Fields(par)
	if len(pars) != 2 {
		return errors.New("invalid parameters")
	}
	var vmName = pars[0]
	var toHost = pars[1]
	vm, err := FindVm(vmName)
	if err != nil {
		return err
	}
	go vm.Migrate(toHost)
	*reply = "migrate job started"
	return nil
}

//shutting down vm on this server
func (h *Hypervisor) ShutdownVm(vmName string, reply *string) error {
	vm, err := FindVm(vmName)
	if err != nil {
		return err
	}
	go vm.Shutdown()
	*reply = "shutdown job started"
	return nil
}

//destroying vm on this server
func (h *Hypervisor) DestroyVm(vmName string, reply *string) error {
	vm, err := FindVm(vmName)
	if err != nil {
		return err
	}
	go vm.Destroy()
	*reply = "destroy job started"
	return nil
}

//List vms on this server
func VmList(vms *[]Vm) error {
	if hyp, _ := IsHypervisor(); hyp {
		// str, err := functions.ExecShell("virsh", []string{"list"})
		str, err := functions.ExecShell("virsh", "list")
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
	}
	return nil
}

//Get image path from running vm
func GetImagePath(vmName string) (string, error) {
	// str, err := functions.ExecShell("virsh", []string{"domblklist", vmName})
	str, err := functions.ExecShell("virsh", "domblklist", vmName)
	if err != nil {
		return "", err
	}
	lines := strings.Split(str, "\n")
	fields := strings.Fields(lines[2])
	return fields[1], nil
}

//Find vm on this server
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
