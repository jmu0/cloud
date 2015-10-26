package main

import (
	f "cloud/functions"
	"cloud/server"
	// "fmt"
	"log"
	"os"
)

func main() {
	route(os.Args[1:])
}

//Route command from args
func route(args []string) {
	//print args
	log.Println("args:", args)
	//Routing command

	/*
		name, _ := f.GetLocalhostName()
		fmt.Println("hostname:", name)
		ip, err := f.GetIP(name)
		if err != nil {
			fmt.Println(err)
		}
		fmt.Println("ip address:", ip)
	*/

	// res, err := f.ExecShell("ls", []string{"/home/jos"})
	// if err != nil {
	// 	log.Fatal(err)
	// }
	// fmt.Println(res)

	go server.Serve()
	val, err := f.GetStringFromServer("nuc", "Server.Hostname", "")
	if err != nil {
		log.Fatal(err)
	}
	log.Println("data from server:", val)
}
