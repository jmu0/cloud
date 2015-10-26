package server

import (
	f "cloud/functions"
	// "cloud/hypervisor"
	// "cloud/storage"
	// "fmt"
	"log"
	"net"
	"net/rpc"
)

type Server struct{}

func Serve() error {
	rpc.Register(new(Server))
	port := f.GetServerPort()
	ln, err := net.Listen("tcp", port)
	log.Println("listening on port", port)
	if err != nil {
		log.Fatal(err)
	}
	for {
		c, err := ln.Accept()
		log.Println("conection accepted")
		if err != nil {
			log.Output(1, err.Error())
			continue
		}
		go rpc.ServeConn(c)
	}
}

//respond to ping
func (s *Server) Ping(_, reply *string) error {
	*reply = "pong"
	return nil
}

func (s *Server) Hostname(_, reply *string) error {
	r, err := f.GetLocalhostName()
	if err != nil {
		return err
	}
	*reply = r
	return nil
}
