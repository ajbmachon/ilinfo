; <?php exit; ?>
[server]
start = "./login.php"

[client]
name = "CLIENT_NAME"
description = ""
access = "1"

[db]
type = "innodb"
host = "localhost"
user = "generic_user_123"
pass = "generic_password_123"
name = "generic_db_name_123"
port = ""
structure_reload = "0"

[auth]
table = "usr_data"
usercol = "login"
passcol = "passwd"
password_encoder = "bcrypt"

[language]
default = "de"
path = "./lang"

[layout]
skin = "default"
style = "delos"

[session]
expire = "7200"

[system]
ROOT_FOLDER_ID = "1"
SYSTEM_FOLDER_ID = "9"
ROLE_FOLDER_ID = "8"
MAIL_SETTINGS_ID = "12"
MAXLENGTH_OBJ_TITLE = "65"
MAXLENGTH_OBJ_DESC = "123"
DEBUG = "0"
DEVMODE = "1"

[cache]
activate_global_cache = "0"
global_cache_service_type = "-1"
log_level = ""

[cache_activated_components]
clng = "0"
obj_def = "0"
ilctrl = "0"
comp = "0"
tpl = "0"
tpl_blocks = "0"
tpl_variables = "0"
events = "0"
global_screen = "0"
