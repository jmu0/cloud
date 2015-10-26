package main

import (
	"cloud/server"
	"fmt"
	"os"
)

func main() {
	fmt.Println(os.Args)
	//Routing command
	name, _ := server.GetLocalhostName()
	fmt.Println("hostname:", name)
	ip, err := server.GetIP(name)
	if err != nil {
		fmt.Println(err)
	}
	fmt.Println("ip address:", ip)
}
