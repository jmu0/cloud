package functions

import (
	"bytes"
	// "fmt"
	"io/ioutil"
	// "log"
	"net"
	"net/rpc"
	"os"
	"os/exec"
)

//get default port for rpc server
func GetServerPort() string {
	return ":7777"
}

//get output from shell command
func ExecShell(cmd string, args []string) (string, error) {
	sh := exec.Command(cmd, args...)
	var out bytes.Buffer
	sh.Stdout = &out
	err := sh.Run()
	if err != nil {
		return "", err
	}
	return out.String(), nil
}

//get the name of localhost
func GetLocalhostName() (string, error) {
	name, err := os.Hostname()
	if err != nil {
		return "", err
	}
	return string(name), nil
}

//lookup ip address for hostname
func GetIP(hostName string) (string, error) {
	ip, err := net.LookupHost(hostName)
	if err != nil {
		return "", err
	}
	return ip[0], nil
}

//get value from socket
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

//read file into string
func ReadFile(path string) (string, error) {
	cont, err := ioutil.ReadFile(path)
	if err != nil {
		return "", err
	} else {
		return string(cont), nil
	}
}

//write file
func WriteFile(path string, contents string) error {
	//write file
	file, err := os.Create(path)
	defer file.Close()
	if err != nil {
		return err
	} else {
		_, err := file.WriteString(contents)
		if err != nil {
			return err
		} else {
			return nil
		}
	}
}
