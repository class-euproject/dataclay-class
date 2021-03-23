#!/bin/bash

file_name="20937-stream.in"
# docker logs dataclay-cloud_dspython_1 | grep "^LOG FILE:" > tp.in
docker logs dataclay-cloud_dspython_1 | grep "^WF LOG FILE:" > ${file_name} 
sed -i 's/WF LOG FILE: //g' ${file_name}
sed -i 's/\[//g' ${file_name}
sed -i 's/\]//g' ${file_name}
sed -i 's/, /,/g' ${file_name}
