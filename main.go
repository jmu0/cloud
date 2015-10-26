package main

import (
	f "cloud/functions"
	h "cloud/hypervisor"
	s "cloud/server"
	"fmt"
	"log"
	"os"
)

func main() {
	route(os.Args[1:])
}

//Route command from args
func route(args []string) {
	//Routing command
	if len(args) > 0 {
		if args[0] == "run" {
			//run server
			s.Serve()
		} else if args[0] == "ishypervisor" {
			fmt.Println(h.IsHypervisor())
		} else if args[0] == "test" {
			test()
		} else {
			printHelp()
		}
	} else {
		// test()
		printHelp()
	}
}

func printHelp() {
	help, err := f.ReadFile("help.txt")
	if err != nil {
		log.Fatal(err)
	}
	fmt.Println(help)
}

func test() {
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
	go s.Serve()
	val, err := f.GetStringFromServer("nuc", "Server.Hostname", "")
	if err != nil {
		log.Fatal(err)
	}
	log.Println("data from server:", val)
}
