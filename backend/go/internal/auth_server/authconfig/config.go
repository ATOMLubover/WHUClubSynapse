package authconfig

type Config struct {
	Env struct {
		Level string `yaml:"level"`
	} `yaml:"env"`

	Database struct {
		Dsn string `yaml:"dsn"`
	} `yaml:"database"`

	Redis struct {
		Host       string `yaml:"host"`
		Port       uint16 `yaml:"port"`
		Password   string `yaml:"password"`
		Db         int    `yaml:"db"`
		MaxConn    int    `yaml:"max_conn"`
		MinIdle    int    `yaml:"min_idle"`
		MaxRetries int    `yaml:"max_retries"`
	} `yaml:"redis"`

	Grpc struct {
		Host        string `yaml:"host"`
		Port        uint16 `yaml:"port"`
		MaxConn     int    `yaml:"max_conn"`
		MinConn     int    `yaml:"min_conn"`
		IdleTimeout int    `yaml:"idle_timeout"`
	} `yaml:"grpc"`
}
