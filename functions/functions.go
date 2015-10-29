package functions

import (
	"bytes"
	// "fmt"
	"io/ioutil"
	// "log"
	// "cloud/server"
	"encoding/json"
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
	var cmderr bytes.Buffer
	sh.Stdout = &out
	sh.Stderr = &cmderr
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
	settings, err := GetSettings()
	if err != nil {
		return "", err
	}
	var path string
	var ok bool
	if path, ok = settings["macfile"]; !ok {
		return "", errors.New("no  macfile in settings")
	}
	str, err := ReadFile(path)
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

//Get settings from json file
func GetSettings() (map[string]string, error) {
	str, err := ReadFile("/etc/cloud.conf")
	if err != nil {
		// log.Fatal(err)
		return make(map[string]string), errors.New("no settings file /etc/cloud.conf")
	}
	settings := map[string]string{}
	lines := strings.Split(str, "\n")
	// log.Println("lines:", lines)
	if len(lines) > 0 {
		for _, line := range lines {
			fields := strings.Fields(line)
			// log.Println("fields:", fields)
			if len(fields) > 1 {
				settings[fields[0]] = strings.Join(fields[1:], " ")
			}
		}
	}
	// log.Println("settings:", settings)
	return settings, nil
}
