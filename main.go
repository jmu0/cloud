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
		} else if args[0] == "vmlist" {
			printVmList()
		} else if args[0] == "wake" {
			if len(args) == 2 {
				wake(args[1])
			} else {
				log.Fatal("Invalid arguments")
			}
		} else if args[0] == "migrate" {
			if len(args) == 3 {
				migrate(args[1], args[2])
			} else if len(args) == 4 && args[1] == "all" {
				migrateAll(args[2], args[3])
			} else {
				log.Fatal("Invalid arguments")
			}
		} else if args[0] == "shutdown" {
			if len(args) == 2 {
				shutdown(args[1])
			} else {
				log.Fatal("Invalid arguments")
			}
		} else if args[0] == "destroy" {
			if len(args) == 2 {
				destroy(args[1])
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

func migrate(vmName string, toServer string) {
	log.Println("migrating", vmName, "to", toServer)
	str, err := server.MigrateVm(vmName, toServer)
	if err != nil {
		log.Fatal(err)
	}
	log.Println(str)
}

func migrateAll(fromServer string, toServer string) {
	log.Println("migrating all vm's from", fromServer, "to", toServer)
	err := server.MigrateAll(fromServer, toServer)
	if err != nil {
		log.Fatal(err)
	}
}

func shutdown(vmName string) {
	log.Println("shutting down ", vmName)
	str, err := server.ShutdownVm(vmName)
	if err != nil {
		log.Fatal(err)
	}
	log.Println(str)
}
func destroy(vmName string) {
	log.Println("destroying", vmName)
	str, err := server.DestroyVm(vmName)
	if err != nil {
		log.Fatal(err)
	}
	log.Println(str)
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
		fmt.Println("migrate test")
		migrate("zoneminder", "server2")
	*/

	/*
		fmt.Println("list vms on nuc")
		lst, err := server.GetVmListFromServer("nuc")
		if err != nil {
			fmt.Println(err)
		}
		fmt.Println(lst)
	*/

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

//print help from help.txt file
func printHelp() {
	//TODO path to helpfile in settings
	help, err := functions.ReadFile("help.txt")
	if err != nil {
		log.Fatal(err)
	}
	fmt.Println(help)
}

//Prints list of servers
func printServerList() error {
	//get servers
	lst, err := server.GetCloudServers()
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

//Print list of vms in cloud
func printVmList() error {
	lst, err := server.GetCloudVmList()
	if err != nil {
		fmt.Println(err)
	}
	//Get field lengths
	fields := map[string]int{
		"Name":      0,
		"Host":      0,
		"State":     0,
		"ImagePath": 0,
	}
	for _, vm := range lst {
		if fields["Name"] < len(vm.Name) {
			fields["Name"] = len(vm.Name)
		}
		if fields["Host"] < len(vm.Host) {
			fields["Host"] = len(vm.Host)
		}
		if fields["State"] < len(vm.State) {
			fields["State"] = len(vm.State)
		}
		if fields["ImatePath"] < len(vm.ImagePath) {
			fields["ImagePath"] = len(vm.ImagePath)
		}
	}
	//headers
	var line string = ""
	var tmp string = ""
	fmt.Println("")
	tmp = "Name"
	makeLength(&tmp, fields["Name"])
	line += tmp + " "
	tmp = "Host"
	makeLength(&tmp, fields["Host"])
	line += tmp + " "
	tmp = "State"
	makeLength(&tmp, fields["State"])
	line += tmp + " "
	tmp = "ImagePath"
	makeLength(&tmp, fields["ImagePath"])
	line += tmp
	fmt.Println(line)
	//underline
	for i := 0; i < len(line); i++ {
		fmt.Printf("-")

	}
	fmt.Printf("\n")
	for _, vm := range lst {
		line = ""
		makeLength(&vm.Name, fields["Name"])
		makeLength(&vm.Host, fields["Host"])
		makeLength(&vm.State, fields["State"])
		makeLength(&vm.ImagePath, fields["ImagePath"])
		line += vm.Name + " "
		line += vm.Host + " "
		line += vm.State + " "
		line += vm.ImagePath + " "
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
