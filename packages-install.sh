#!/bin/bash
cd functions
go install
cd ../server
go install
cd ../client
go install
cd ../storage
go install
cd ../hypervisor
go install
cd ..
