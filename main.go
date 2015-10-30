package main

import (
	"cloud/client"
	"cloud/functions"
	"cloud/hypervisor"
	"cloud/server"
	// "cloud/storage"
	"fmt"
	"log"
	"os"
)

func main() {
	routeCommand(os.Args[1:])
}

//Route command from args
func routeCommand(args []string) {
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
		} else if args[0] == "shares" {
			printShareList()
		} else if args[0] == "mounts" {
			printMountList()
		} else if args[0] == "wake" {
			if len(args) == 2 {
				hostname := args[1]
				str, err := client.Wake(hostname)
				if err != nil {
					log.Fatal(err)
				} else {
					fmt.Println(str)
				}
			} else {
				log.Fatal("Invalid arguments")
			}
		} else if args[0] == "migrate" {
			if len(args) == 3 {
				vmName := args[1]
				toServer := args[2]
				log.Println("migrating", vmName, "to", toServer)
				str, err := client.MigrateVm(vmName, toServer)
				if err != nil {
					log.Fatal(err)
				}
				log.Println(str)
			} else if len(args) == 4 && args[1] == "all" {
				fromServer := args[2]
				toServer := args[3]
				log.Println("migrating all vm's from", fromServer, "to", toServer)
				err := client.MigrateAll(fromServer, toServer)
				if err != nil {
					log.Fatal(err)
				}
			} else {
				log.Fatal("Invalid arguments")
			}
		} else if args[0] == "shutdown" {
			if len(args) == 2 {
				vmName := args[1]
				log.Println("shutting down ", vmName)
				str, err := client.ShutdownVm(vmName)
				if err != nil {
					log.Fatal(err)
				}
				log.Println(str)
			} else {
				log.Fatal("Invalid arguments")
			}
		} else if args[0] == "destroy" {
			if len(args) == 2 {
				vmName := args[1]
				log.Println("destroying", vmName)
				str, err := client.DestroyVm(vmName)
				if err != nil {
					log.Fatal(err)
				}
				log.Println(str)
			} else {
				log.Fatal("Invalid arguments")
			}
		} else if args[0] == "settings" {
			s, err := functions.GetSettings()
			if err != nil {
				log.Fatal(err)
			}
			fmt.Println("Settings in /etc/cloud.conf:")
			for k, v := range s {
				fmt.Println(k, "=", v)
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

func test() {
	fmt.Println("Test")
	printMountList()
	/*
		sh, err := storage.GetShares()

		if err != nil {
			log.Fatal(err)
		}
		fmt.Println(sh)
		fmt.Println(sh[1].ToLine())
	*/
	/*
		sh, err := client.GetCloudShareList()
		if err != nil {
			log.Fatal(err)
		}
		fmt.Println(sh)
	*/
}

//print help from help.txt file
func printHelp() {
	//find path
	settings, err := functions.GetSettings()
	if err != nil {
		log.Println(err)
	}
	var path string
	var ok bool
	if path, ok = settings["helpfile"]; !ok {
		log.Println("no path to helpfile in settings")
		path = "help.txt"
	}
	help, err := functions.ReadFile(path)
	if err != nil {
		log.Fatal(err)
	}
	fmt.Println(help)
}

//Prints list of servers
func printServerList() error {
	//get servers
	lst, err := client.GetCloudServers()
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
	lst, err := client.GetCloudVmList()
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
	//table
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

//Print list of shares in cloud
func printShareList() error {
	lst, err := client.GetCloudShareList()
	if err != nil {
		fmt.Println(err)
	}
	//Get field lengths
	fields := map[string]int{
		"Name": 0,
		"Path": 0,
		"Host": 0,
	}
	for _, s := range lst {
		if fields["Name"] < len(s.Name) {
			fields["Name"] = len(s.Name)
		}
		if fields["Path"] < len(s.Path) {
			fields["Path"] = len(s.Path)
		}
		if fields["Host"] < len(s.Host) {
			fields["Host"] = len(s.Host)
		}
	}
	//headers
	var line string = ""
	var tmp string = ""
	fmt.Println("")
	tmp = "Name"
	makeLength(&tmp, fields["Name"])
	line += tmp + " "
	tmp = "Path"
	makeLength(&tmp, fields["Path"])
	line += tmp + " "
	tmp = "Host"
	makeLength(&tmp, fields["Host"])
	line += tmp
	fmt.Println(line)
	//underline
	for i := 0; i < len(line); i++ {
		fmt.Printf("-")

	}
	fmt.Printf("\n")
	//table
	for _, s := range lst {
		line = ""
		makeLength(&s.Name, fields["Name"])
		makeLength(&s.Path, fields["Path"])
		makeLength(&s.Host, fields["Host"])
		line += s.Name + " "
		line += s.Path + " "
		line += s.Host + " "
		fmt.Println(line)
	}
	fmt.Println("")
	return nil
}
func printMountList() error {
	lst, err := client.GetCloudMountList()
	if err != nil {
		fmt.Println(err)
	}
	//Get field lengths
	fields := map[string]int{
		"Name":  4,
		"Share": 5,
		// "SharePath":  9,
		// "ShareHost":  9,
		"MountHost":  9,
		"MountPoint": 10,
	}
	for _, s := range lst {
		if fields["Name"] < len(s.Name) {
			fields["Name"] = len(s.Name)
		}
		if fields["Share"] < len(s.Share) {
			fields["Share"] = len(s.Share)
		}
		// if fields["SharePath"] < len(s.SharePath) {
		// 	fields["SharePath"] = len(s.SharePath)
		// }
		// if fields["ShareHost"] < len(s.ShareHost) {
		// 	fields["ShareHost"] = len(s.ShareHost)
		// }
		if fields["MountPoint"] < len(s.MountPoint) {
			fields["MountPoint"] = len(s.MountPoint)
		}
		if fields["MountHost"] < len(s.MountHost) {
			fields["MountHost"] = len(s.MountHost)
		}
	}
	//headers
	var line string = ""
	var tmp string = ""
	fmt.Println("")
	tmp = "Name"
	makeLength(&tmp, fields["Name"])
	line += tmp + " "
	tmp = "Share"
	makeLength(&tmp, fields["Share"])
	line += tmp + " "
	// tmp = "SharePath"
	// makeLength(&tmp, fields["SharePath"])
	// line += tmp + " "
	// tmp = "ShareHost"
	// makeLength(&tmp, fields["ShareHost"])
	// line += tmp + " "
	tmp = "MountHost"
	makeLength(&tmp, fields["MountHost"])
	line += tmp + " "
	tmp = "MountPoint"
	makeLength(&tmp, fields["MountPoint"])
	line += tmp
	fmt.Println(line)

	//underline
	for i := 0; i < len(line); i++ {
		fmt.Printf("-")

	}
	fmt.Printf("\n")
	//table
	for _, s := range lst {
		line = ""
		makeLength(&s.Name, fields["Name"])
		makeLength(&s.Share, fields["Share"])
		// makeLength(&s.SharePath, fields["SharePath"])
		// makeLength(&s.ShareHost, fields["ShareHost"])
		makeLength(&s.MountHost, fields["MountHost"])
		makeLength(&s.MountPoint, fields["MountPoint"])

		line += s.Name + " "
		line += s.Share + " "
		// line += s.SharePath + " "
		// line += s.ShareHost + " "
		line += s.MountHost
		line += s.MountPoint + " "
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
