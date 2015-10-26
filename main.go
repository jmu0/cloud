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
		} else if args[0] == "servers" {
			printServerList()
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
	fmt.Println("Test")

	/*
		var val server.Server
		var err error
		host, _ := functions.GetLocalhostName()
		val, err = server.GetPropertiesFromServer(host)
		if err == nil {
			log.Println("value:", val)
			log.Fatal(err)
		}
		log.Println("data from server:", val)
	*/

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

//Prints list of servers
func printServerList() error {
	//get servers
	lst, err := server.GetServerList()
	if err != nil {
		log.Fatal(err)
	}
	//Get field lengths
	fields := map[string]int{
		"IP":           0,
		"Hostname":     0,
		"Load":         0,
		"IsHypervisor": 8,
		"IsNfsServer":  8,
	}
	for _, srv := range lst {
		if fields["IP"] < len(srv.IP) {
			fields["IP"] = len(srv.IP)
		}
		if fields["Hostname"] < len(srv.Hostname) {
			fields["Hostname"] = len(srv.Hostname)
		}
		if fields["Load"] < len(srv.Load) {
			fields["Load"] = len(srv.Load)
		}
	}
	//headers
	var line string = ""
	var tmp string = ""
	fmt.Println("")
	tmp = "IP"
	makeLength(&tmp, fields["IP"])
	line += tmp + " "
	tmp = "Hostname"
	makeLength(&tmp, fields["Hostname"])
	line += tmp + " "
	tmp = "Load"
	makeLength(&tmp, fields["Load"])
	line += tmp + " "
	line += "Virsh Nfs  "
	fmt.Println(line)
	//underline
	for i := 0; i < len(line); i++ {
		fmt.Printf("-")

	}
	fmt.Printf("\n")
	//servers
	f := "False "
	t := "True  "
	for _, srv := range lst {
		line = ""
		makeLength(&srv.IP, fields["IP"])
		makeLength(&srv.Hostname, fields["Hostname"])
		srv.Load = srv.Load[:len(srv.Load)-1]
		makeLength(&srv.Load, fields["Load"])
		line += srv.IP + " "
		line += srv.Hostname + " "
		line += srv.Load + " "
		if srv.IsHypervisor {
			line += t
		} else {
			line += f
		}
		if srv.IsNfsServer {
			line += t
		} else {
			line += f
		}
		fmt.Println(line)
	}
	fmt.Println("")
	return nil
}

//makes string a certain length
func makeLength(f *string, l int) {
	for {
		if len(*f) >= l {
			return
		}
		*f += " "
	}
}
