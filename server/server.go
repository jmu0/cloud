package server

import (
	"cloud/functions"
	"cloud/hypervisor"
	"cloud/storage"
	// "fmt"
	// "errors"
	"log"
	"net"
	"net/rpc"
	// "strconv"
	// "time"
)

//structure for server properties and methods
type Server struct {
	IP           string
	Hostname     string
	Load         string
	IsHypervisor bool
	IsNfsServer  bool
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
	port := functions.GetServerPort()
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
