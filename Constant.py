# client send
LOGIN=0 #user pwd
REGISTER=1 #user pwd
SENDMSG=2 #receiver msg_length + msg
LOGOUT=3 
ASKUSERS=4
SENDFILE=5 #receiver file_name file_size + data of file
DOWNFILE=6 #sender file_name 

# server response
LOGIN_WRONG=100 
LOGIN_SUCCESS=101
LOGIN_REPEAT=102
LOGIN_INFO=103 #username (to all)

REGISTER_ERROR=200 
REGISTER_SUCCESS=201

LOGOUT_INFO=300 #username (to all)

SENDMSG_ERROR=200 
SEND_ALL=210 #sender msg_length + msg (to all)
SEND_NONE=211 #receiver
SEND_PER=212 #sender msg_length + msg

ASKUSERS_RET=400 #length of user_list +user_list

SENDFILE_ERROR=500
SENDFILE_NONE=501
SENDFILE_SUCCESS=502
SENDFILE_ALL=510 #sender file_name (to all)
SENDFILE_NONE=511 
SENDFILE_PER=512 #sender file_name

DOWNFILE_SUCCESS=600 #sender file_name file_size +data of file
DOWNFILE_NONE=601


WRONG_MESSAGE=900