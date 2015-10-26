package main

import (
	"cloud/functions"
	"cloud/hypervisor"
	"cloud/server"
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
			server.Serve()
		} else if args[0] == "ishypervisor" {
			fmt.Println(hypervisor.IsHypervisor())
		} else if args[0] == "wake" {
			if len(args) == 2 {
				wake(args[1])
			} else {
				log.Fatal("Invalid arguments")
			}
		} else if args[0] == "test" {
			test()
		} else {
			printHelp()
		}
	} else {
		test()
		// printHelp()
	}
}

func printHelp() {
	help, err := functions.ReadFile("help.txt")
	if err != nil {
		log.Fatal(err)
	}
	fmt.Println(help)
}

func wake(hostname string) {
	str, err := functions.Wake(hostname)
	if err != nil {
		log.Fatal(err)
	} else {
		fmt.Println(str)
	}
}
func test() {
	val, err := server.GetPropertiesFromServer("htpc")
	if err != nil {
		log.Println("value:", val)
		log.Fatal(err)
	}
	log.Println("data from server:", val)

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

	// go server.Serve()
}
