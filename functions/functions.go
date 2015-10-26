package functions

import (
	"bytes"
	// "fmt"
	"io/ioutil"
	// "log"
	"encoding/json"
	"errors"
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

type MacAddress struct {
	Hostname string
	Mac      string
}

//Wake server
//Get mac addresses from mac.json file
func Wake(hostname string) (string, error) {
	//find out which command
	cmd, err := ExecShell("which", []string{"wol"})
	if err != nil {
		return "", err
	}
	if len(cmd) > 0 {
		cmd = "wol"
	} else {
		cmd, err := ExecShell("which", []string{"wakeonlan"})
		if err != nil {
			return "", err
		}
		if len(cmd) > 0 {
			cmd = "wakeonlan"
		} else {
			return "", errors.New("No wake-on-lan package installed")
		}
	}
	//find mac address
	str, err := ReadFile("mac.json")
	if err != nil {
		return "", err
	}
	lst := []MacAddress{}
	err = json.Unmarshal([]byte(str), &lst)
	if err != nil {
		return "", err
	}
	for _, a := range lst {
		if a.Hostname == hostname {
			str, err = ExecShell(cmd, []string{a.Mac})
			if err != nil {
				return "", err
			}
			return str, nil
		}
	}
	return "", errors.New("No mac address found for hostname: " + hostname)
}
