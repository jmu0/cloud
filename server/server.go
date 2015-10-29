package server

import (
	"cloud/functions"
	"cloud/hypervisor"
	"cloud/storage"
	// "fmt"
	"errors"
	"log"
	"net"
	"net/rpc"
	"strconv"
	"time"
)

//structure for server properties and methods
type Server struct {
	IP           string
	Hostname     string
	Load         string
	IsHypervisor bool
	IsNfsServer  bool
}

//get default port for rpc server
func GetServerPort() string {
	return ":7777"
}

//respond to ping
func (srv *Server) Ping(par string, reply *string) error {
	*reply = "pong"
	return nil
}

//return server properties
func (srv *Server) Properties(par string, reply *Server) error {
	// log.Println("Server.Properties")
	var err error
	reply.Hostname, err = functions.GetLocalhostName()
	if err != nil {
		log.Println(err)
		return err
	}
	reply.IP, err = functions.GetIP(reply.Hostname)
	if err != nil {
		log.Println(err)
		return err
	}
	reply.IsHypervisor, err = hypervisor.IsHypervisor()
	if err != nil {
		log.Println(err)
		return err
	}
	reply.IsNfsServer, err = storage.IsNfsServer()
	if err != nil {
		log.Println(err)
		return err
	}
	reply.Load, err = getLoad()
	if err != nil {
		log.Println(err)
		return err
	}
	// log.Println(reply)
	return nil
}

//start rpc server
func Serve() error {
	rpc.Register(new(Server))
	rpc.Register(new(hypervisor.Hypervisor))
	port := GetServerPort()
	ln, err := net.Listen("tcp", port)
	log.Println("listening on port", port)
	if err != nil {
		log.Fatal(err)
	}
	for {
		c, err := ln.Accept()
		log.Println("conection accepted")
		if err != nil {
			log.Println(err)
			continue
		}
		go rpc.ServeConn(c)
	}
	return nil
}

//get load average from /proc/loadavg
func getLoad() (string, error) {
	ld, err := functions.ReadFile("/proc/loadavg")
	if err != nil {
		return "", err
	}
	return ld, nil
}

//get string value from socket
func GetStringFromServer(Host, Command, Parameters string) (string, error) {
	c, err := rpc.Dial("tcp", Host+GetServerPort())
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
func GetPropertiesFromServer(Host string) (Server, error) {
	c, err := rpc.Dial("tcp", Host+GetServerPort())
	if err != nil {
		return Server{}, err
	}
	result := new(Server)
	err = c.Call("Server.Properties", "", result)
	if err != nil {
		return Server{}, err
	}
	return *result, nil
}

//get vm list from socket
func GetVmListFromServer(Host string) ([]hypervisor.Vm, error) {
	// log.Println("GetVmListFromServer")
	c, err := rpc.Dial("tcp", Host+GetServerPort())
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
			// log.Println("error while getting vmlist for", ip, err)
			// return []Server{}, err
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

//get list of servers/properties
func GetCloudServers() ([]Server, error) {
	lst := []Server{}
	ips, err := ScanNetwork()
	if err != nil {
		log.Println("error during network scan", err)
		return []Server{}, err
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
