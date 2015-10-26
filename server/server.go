package server

import (
	"cloud/functions"
	"cloud/hypervisor"
	"cloud/storage"
	// "fmt"
	"log"
	"net"
	"net/rpc"
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

//start rpc server
func Serve() error {
	rpc.Register(new(Server))
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
}

//get load average from /proc/loadavg
func getLoad() (string, error) {
	ld, err := functions.ReadFile("/proc/loadavg")
	if err != nil {
		return "", err
	}
	return ld, nil
}

//respond to ping
func (srv *Server) Ping(par string, reply *string) error {
	*reply = "pong"
	return nil
}

func (srv *Server) Properties(par string, reply *Server) error {
	// log.Println("Server.Properties")
	var err error
	srv.Hostname, err = functions.GetLocalhostName()
	if err != nil {
		return err
	}
	srv.IP, err = functions.GetIP(srv.Hostname)
	if err != nil {
		return err
	}
	srv.IsHypervisor, err = hypervisor.IsHypervisor()
	if err != nil {
		return err
	}
	srv.IsNfsServer, err = storage.IsNfsServer()
	if err != nil {
		return err
	}
	srv.Load, err = getLoad()
	if err != nil {
		return err
	}
	log.Println(srv)
	reply = srv
	/*
		repl := Server{
			Hostname:     lh,
			IP:           ip,
			IsHypervisor: ishv,
			IsNfsServer:  isnfs,
			Load:         ld,
		}
		reply = &repl
	*/
	return nil
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
	// log.Println("GetPropertiesFromServer")
	c, err := rpc.Dial("tcp", Host+GetServerPort())
	if err != nil {
		// log.Println("rpc connection error")
		return Server{}, err
	}
	result := Server{}
	err = c.Call("Server.Properties", "", &result)
	// log.Printf("result type: %T", result)
	// log.Println("result:", result)
	if err != nil {
		// log.Println("rpc call error")
		return Server{}, err
	}
	return result, nil
}
