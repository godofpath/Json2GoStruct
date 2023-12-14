head = '''package utils  
  
import (
    "os"
    "encoding/json"
)
'''
def all_same_type(lst):  
    return all(type(i) is type(lst[0]) for i in lst)

class Json2GoLangStruct:
    def __init__(self, data: dict) -> None:
        self.data = data
        self.global_config = GlobalConfig()
        self.structures: [str] = []
        self.handle_json()
        
    def gen_value(self, key: str, value) -> str:
        line = ''
        if type(value) is str:
            line = f'    {key.title()} string `json:"{key}"`\n'
        elif type(value) is int:
            line = f'    {key.title()} int `json:"{key}"`\n'
        elif type(value) is float:
            line = f'    {key.title()} float `json:"{key}"`\n'
        elif type(value) is bool:
            line = f'    {key.title()} bool `json:"{key}"`\n'
        else:
            raise("unspported type")
        return line
    
    def gen_value_for_arr(self, key: str, keys:str, value) -> str:
        if len(value) == 0:
            return f'    {keys.title()} []interface{{}} `json:"{keys}.lower()"`\n'
        line = ''
        value = value[0]
        if type(value) is dict:
            line = f'    {keys.title()} []{key.title()}ConfigS `json:"{keys.lower()}"`\n'
        elif type(value) is str:
            line = f'    {keys.title()} []string `json:"{keys}.lower()"`\n'
        elif type(value) is int:
            line = f'    {keys.title()} []int `json:"{keys}.lower()"`\n'
        elif type(value) is float:
            line = f'    {keys.title()} []float `json:"{keys}.lower()"`\n'
        elif type(value) is bool:
            line = f'    {keys.title()} []bool `json:"{keys}.lower()"`\n'
        else:
            # 不支持数组的数组
            raise(f"unspported type in arr {key}")
        return line
    
    def handle_json(self):
        for key, value in self.data.items():
            if type(key) is str:
                if type(value) is dict:
                    self.global_config.add_line(f'    {key.title()} {key.title()}ConfigS `json:"{key.lower()}"`')
                    structure = f'type {key.title()}ConfigS struct {{\n'
                    structure += self.handle_dict(key, value)
                    structure += '}'
                    self.structures.append(structure)
                elif type(value) is list:
                    obj:str = key
                    arr:str = key
                    if key.endswith('s'):
                        obj = key[:-1]
                    else:
                        arr = key+'s'
                    self.global_config.add_line(self.gen_value_for_arr(obj, arr, value))
                    self.handle_arr(key, value)
                else:
                    self.global_config.add_line(self.gen_value(key, value))
                
            else:
                raise 'in config file, key must be string'
            
    def write(self, f:str) -> None:
        with open(f, 'w+') as fp:
            fp.write(head)
            fp.write('\n'.join(self.structures))
            fp.write('\n')
            fp.write(self.global_config.get_struct_str())
            fp.write('\n')
            fp.write(ParseConfigFile)
            
    
    def handle_dict(self, parent:str, data:dict) -> str:
        result = ''
        for key, value in data.items():
            if type(key) is str:
                if type(value) is dict:
                    result += (f'    {key.title()} {key.title()}ConfigS `json:"{key.lower()}"`\n')
                    structure = f'type {key.title()}ConfigS struct {{\n'
                    structure += self.handle_dict(key, value)
                    structure += '}'
                    self.structures.append(structure)
                elif type(value) is list:
                    obj:str = key
                    arr:str = key
                    if key.endswith('s'):
                        obj = key[:-1]
                    else:
                        arr = key+'s'
                    result += f'    {arr.title()} []{obj.title()}ConfigS `json:"{key}"`'
                    self.handle_arr('', key, value)
                else:
                    result += self.gen_value(key, value)
        return result
    
    def handle_arr(self, parent:str, arr1:[]) ->str:
        if not all_same_type(arr1):
            raise 'all elements should be the same type in a list'
        item = arr1[0]
        obj:str = parent
        arr:str = parent
        if parent.endswith('s'):
            obj = parent[:-1]
        else:
            arr = parent+'s'
        if type(item) is dict:
            result = f'type {obj.title()}ConfigS struct {{\n'
            result += self.handle_dict(obj, item)
            result += '}'
            self.structures.append(result)
        

class GlobalConfig:
    def __init__(self) -> None:
        self.head = 'type ConfigS struct {'
        self.tail = '}\n'
        self.variable = 'var Config ConfigS'
        self.lines = []
        
    def add_line(self, line: str) -> None:
        self.lines.append(line)
    
    def get_struct_str(self) -> str:
        members = '\n'.join(self.lines)
        return '\n'.join([self.head, members, self.tail, self.variable])
    
ParseConfigFile = '''func ParseConfigFile(file string) {
    // 读取配置文件内容  
    config, err := os.ReadFile(file)
    if err != nil {  
        panic(err)  
    }  
    
    // 解析JSON配置文件  
    err = json.Unmarshal(config, &Config)  
    if err != nil {  
        panic(err)
    }
}'''
    
        
if __name__ == '__main__':
    c = {
	"DBs": [
			{
				"use": "mysql",
				"host": "127.0.0.1",
				"port": 33306,
				"user": "root",
				"password": "root",
				"database": "sss",
				"sqlitedbpath": ""
			}
    	],
	"EMAIL": {
		"from": "",
		"smtpsrv": "",
		"smtpsrvwithport": "",
		"username": "",
		"password": ""
	},
    "SMS": {
		"Use": "",
		"Ali": {
            "secretid": "",
            "secretapp": "",
        },
        "Huawei": {
            "secretid": "",
            "secretapp": "",
        }
	},
	"Pagenation": {
		"maxpagesize": "100",
		"defaultpagesize": "10"
	},
	"Site": {
		"domain": "",
		"name": "",
        "istrue": True,
		"reset_password_time": "",
		"gen_file_path": "",
		"log_file": "",
		"file_root": ""
	}
}

    j = Json2GoLangStruct(c)
    j.write('./output.go')
# // Don't support two or more demension array
# // The item in a array must have the same type