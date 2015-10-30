package client

import (
	"cloud/functions"
	"cloud/hypervisor"
	"cloud/server"
	"cloud/storage"
	"encoding/json"
	"errors"
	"log"
	"net"
	"net/rpc"
	"strconv"
	"time"
)

//get string value from socket
func GetStringFromServer(Host, Command, Parameters string) (string, error) {
	c, err := rpc.Dial("tcp", Host+functions.GetServerPort())
	if err != nil {
		return "", err
	}
	var result *string = new(string)
	err = c.Call(Command, Parameters, result)
	if err != nil {
		return "", err
	}
	return *result, nil
}

//get server struct from socket
func GetPropertiesFromServer(Host string) (server.Server, error) {
	c, err := rpc.Dial("tcp", Host+functions.GetServerPort())
	if err != nil {
		return server.Server{}, err
	}
	result := new(server.Server)
	err = c.Call("Server.Properties", "", result)
	if err != nil {
		return server.Server{}, err
	}
	return *result, nil
}

//get vm list from socket
func GetVmListFromServer(Host string) ([]hypervisor.Vm, error) {
	// log.Println("GetVmListFromServer")
	c, err := rpc.Dial("tcp", Host+functions.GetServerPort())
	if err != nil {
		// log.Println("rpc connection error")
		return []hypervisor.Vm{}, err
	}
	result := new([]hypervisor.Vm)
	err = c.Call("Hypervisor.VmList", "", result)
	if err != nil {
		// log.Println("rpc call error")
		return []hypervisor.Vm{}, err
	}
	// log.Printf("result type: %T", result)
	// log.Println("result:", result)
	return *result, nil
}

//get share list from socket
func GetShareListFromServer(Host string) ([]storage.Share, error) {
	// log.Println("GetShareListFromServer")
	c, err := rpc.Dial("tcp", Host+functions.GetServerPort())
	if err != nil {
		// log.Println("rpc connection error")
		return []storage.Share{}, err
	}
	result := new([]storage.Share)
	err = c.Call("Storage.GetShares", "", result)
	if err != nil {
		// log.Println("rpc call error")
		return []storage.Share{}, err
	}
	// log.Printf("result type: %T", result)
	// log.Println("result:", result)
	return *result, nil
}

//get mount list from socket
func GetMountListFromServer(Host string) ([]storage.Mount, error) {
	// log.Println("GetMountListFromServer")
	c, err := rpc.Dial("tcp", Host+functions.GetServerPort())
	if err != nil {
		// log.Println("rpc connection error")
		return []storage.Mount{}, err
	}
	result := new([]storage.Mount)
	err = c.Call("Storage.GetMounts", "", result)
	if err != nil {
		// log.Println("rpc call error")
		return []storage.Mount{}, err
	}
	// log.Printf("result type: %T", result)
	// log.Println("result:", result)
	return *result, nil
}

//Returns ip addresses of servers
func ScanNetwork() ([]string, error) {
	timeout := time.Microsecond * 500
	lst := []string{}
	for i := 1; i < 255; i++ {
		ip := "10.0.0." + strconv.Itoa(i)
		_, err := net.DialTimeout("tcp", ip+":7777", timeout)
		if err == nil {
			lst = append(lst, ip)
		}
	}
	return lst, nil
}

//get list of vms from cloud servers
func GetCloudVmList() ([]hypervisor.Vm, error) {
	lst := []hypervisor.Vm{}
	ips, err := ScanNetwork()
	if err != nil {
		// log.Println("error during network scan", err)
		return []hypervisor.Vm{}, err
	}
	for _, ip := range ips {
		vml, err := GetVmListFromServer(ip)
		if err != nil {
			log.Println("error while getting vmlist for", ip, err)
			return []hypervisor.Vm{}, err
		}
		lst = append(lst, vml...)
	}
	return lst, nil
}

//get list of shares from cloud servers
func GetCloudShareList() ([]storage.Share, error) {
	lst := []storage.Share{}
	ips, err := ScanNetwork()
	if err != nil {
		// log.Println("error during network scan", err)
		return []storage.Share{}, err
	}
	for _, ip := range ips {
		vml, err := GetShareListFromServer(ip)
		if err != nil {
			// log.Println("error while getting share list for", ip, err)
			return []storage.Share{}, err
		}
		lst = append(lst, vml...)
	}
	return lst, nil
}

//get list of mounts from cloud servers
func GetCloudMountList() ([]storage.Mount, error) {
	lst := []storage.Mount{}
	ips, err := ScanNetwork()
	if err != nil {
		// log.Println("error during network scan", err)
		return []storage.Mount{}, err
	}
	for _, ip := range ips {
		vml, err := GetMountListFromServer(ip)
		if err != nil {
			// log.Println("error while getting share list for", ip, err)
			return []storage.Mount{}, err
		}
		lst = append(lst, vml...)
	}
	return lst, nil
}

//find vm in cloud
func FindVm(vmName string) (hypervisor.Vm, error) {
	lst, err := GetCloudVmList()
	if err != nil {
		return hypervisor.Vm{}, err
	}
	for _, v := range lst {
		if v.Name == vmName {
			return v, nil
		}
	}
	return hypervisor.Vm{}, errors.New("Vm " + vmName + " not found.")
}

//find server in cloud
func FindServer(serverName string) (server.Server, error) {
	lst, err := GetCloudServers()
	if err != nil {
		return server.Server{}, err
	}
	for _, v := range lst {
		if v.Hostname == serverName {
			return v, nil
		}
	}
	return server.Server{}, errors.New("Server " + serverName + " not found.")
}

//get list of servers/properties
func GetCloudServers() ([]server.Server, error) {
	lst := []server.Server{}
	ips, err := ScanNetwork()
	if err != nil {
		log.Println("error during network scan", err)
		return []server.Server{}, err
	}
	for _, ip := range ips {
		srv, err := GetPropertiesFromServer(ip)
		if err != nil {
			log.Println("error while getting properties for", ip, err)
			// return []Server{}, err
		}
		lst = append(lst, srv)
	}
	return lst, nil
}

//send migrate job to server where vm is running
func MigrateVm(vmName string, toServer string) (string, error) {
	//check if vm exists
	vm, err := FindVm(vmName)
	if err != nil {
		return "", err
	}
	if vm.Host == toServer {
		return "", errors.New(vmName + " is already running on " + toServer)
	}
	to, err := FindServer(toServer)
	if err != nil {
		return "", err
	}
	if !to.IsHypervisor {
		return "", errors.New(toServer + " is not a hypervisor")
	}
	return GetStringFromServer(vm.Host, "Hypervisor.MigrateVm", vmName+" "+toServer)
}

//find vm and shut down
func ShutdownVm(vmName string) (string, error) {
	//check if vm exists
	vm, err := FindVm(vmName)
	if err != nil {
		return "", err
	}
	return GetStringFromServer(vm.Host, "Hypervisor.ShutdownVm", vmName)
}

//find vm and shut down
func DestroyVm(vmName string) (string, error) {
	//check if vm exists
	vm, err := FindVm(vmName)
	if err != nil {
		return "", err
	}
	return GetStringFromServer(vm.Host, "Hypervisor.DestroyVm", vmName)
}

//migreate all vm's from server to server
func MigrateAll(fromServer string, toServer string) error {
	lst, err := GetCloudVmList()
	if err != nil {
		return err
	}
	for _, vm := range lst {
		if vm.Host == fromServer {
			log.Println("migrating", vm.Name, "from", fromServer, "to", toServer)
			str, err := GetStringFromServer(fromServer, "Hypervisor.MigrateVm", vm.Name+" "+toServer)
			if err != nil {
				log.Println(err, str)
			}
		}
	}
	return nil
}

type MacAddress struct {
	Hostname string
	Mac      string
}

//Wake server
//Get mac addresses from mac.json file
func Wake(hostname string) (string, error) {
	//find out which command
	cmd, err := functions.ExecShell("which", []string{"wol"})
	if err != nil {
		return "", err
	}
	if len(cmd) > 0 {
		cmd = "wol"
	} else {
		cmd, err := functions.ExecShell("which", []string{"wakeonlan"})
		if err != nil {
			return "", err
		}
		if len(cmd) > 0 {
			cmd = "wakeonlan"
		} else {
			return "", errors.New("No wake-on-lan package installed")
		}
	}
	//find mac address
	settings, err := functions.GetSettings()
	if err != nil {
		return "", err
	}
	var path string
	var ok bool
	if path, ok = settings["macfile"]; !ok {
		return "", errors.New("no  macfile in settings")
	}
	str, err := functions.ReadFile(path)
	if err != nil {
		return "", err
	}
	lst := []MacAddress{}
	err = json.Unmarshal([]byte(str), &lst)
	if err != nil {
		return "", err
	}
	for _, a := range lst {
		if a.Hostname == hostname {
			str, err = functions.ExecShell(cmd, []string{a.Mac})
			if err != nil {
				return "", err
			}
			return str, nil
		}
	}
	return "", errors.New("No mac address found for hostname: " + hostname)
}
