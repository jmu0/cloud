package functions

import (
	"bytes"
	// "fmt"
	"io/ioutil"
	// "log"
	// "cloud/server"
	// "encoding/json"
	"errors"
	"net"
	"os"
	"os/exec"
	// "reflect"
	"strings"
)

//get output from shell command
func ExecShell(cmd string, args []string) (string, error) {
	sh := exec.Command(cmd, args...)
	var out bytes.Buffer
	var errString bytes.Buffer
	sh.Stdout = &out
	sh.Stderr = &errString
	err := sh.Run()
	if err != nil || len(errString.String()) > 0 {
		errStr := "Error in command: " + errString.String()
		errStr += "(command: " + cmd + " " + strings.Join(args, " ") + ")"
		return "", errors.New(errStr)
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
	/*
		check /etc/hosts on server
		change this line if necessary:
		127.0.0.1 <servername>
		to:
		<ip> <servername>
		or this function will return 127.0.0.1
	*/

	ip, err := net.LookupHost(hostName)
	if err != nil {
		return "", err
	}
	return ip[0], nil
}

//lookup hostname for ip
func GetHostname(ip string) (string, error) {
	names, err := net.LookupAddr(ip)
	if err != nil {
		return "", err
	}
	return names[0], nil
}

//read file into string
func ReadFile(path string) (string, error) {
	cont, err := ioutil.ReadFile(path)
	if err != nil {
		return "", err
	}
	return string(cont), nil
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
		}
	}
	return nil
}

//append to file
func AppendToFile(path string, content string) error {
	f, err := os.OpenFile(path, os.O_RDWR|os.O_APPEND, 0660)
	defer f.Close()
	if err != nil {
		return err
	}
	_, err = f.WriteString(content)
	if err != nil {
		return err
	}
	return nil
}

//Get settings from json file
func GetSettings() (map[string]string, error) {
	//TODO use settings package
	str, err := ReadFile("/etc/cloud.conf")
	if err != nil {
		return make(map[string]string), errors.New("no settings file /etc/cloud.conf")
	}
	settings := map[string]string{}
	lines := strings.Split(str, "\n")
	if len(lines) > 0 {
		for _, line := range lines {
			if len(line) > 0 && line[:1] != "#" {
				fields := strings.Fields(line)
				if len(fields) > 1 {
					settings[fields[0]] = strings.Join(fields[1:], " ")
				}
			}
		}
	}
	return settings, nil
}

//get default port for rpc server
//get from settings file or return default
func GetServerPort() string {
	var def string = ":7777"
	settings, err := GetSettings()
	if err != nil {
		return def
	}
	if port, ok := settings["port"]; !ok {
		return def
	} else {
		return port
	}
	return def
}

//check if path exists
func PathExists(path string) bool {
	if _, err := os.Stat(path); os.IsNotExist(err) {
		return false
	}
	return true
}
