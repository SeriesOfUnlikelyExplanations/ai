Content-Type: multipart/mixed; boundary="//"
MIME-Version: 1.0

--//
Content-Type: text/cloud-config; charset="us-ascii"
MIME-Version: 1.0
Content-Transfer-Encoding: 7bit
Content-Disposition: attachment; filename="cloud-config.txt"

#cloud-config
cloud_final_modules:
- [scripts-user, always]

--//
Content-Type: text/x-shellscript; charset="us-ascii"
MIME-Version: 1.0
Content-Transfer-Encoding: 7bit
Content-Disposition: attachment; filename="userdata.txt"

#!/bin/bash
<<<<<<< HEAD
=======
/bin/echo "Hello World" >> /tmp/userdata-test.txt
sudo apt install git nvidia-cuda-toolkit
CMAKE_ARGS="-DLLAMA_CUBLAS=on" 
FORCE_CMAKE=1
>>>>>>> efaf5df074da42ad701811f1cc91c1f5cc199e04

--//
