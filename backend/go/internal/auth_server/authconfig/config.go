package authconfig

type Config struct {
	Env struct {
		Level string `yaml:"level"`
	} `yaml:"env"`
	Database struct {
		Dsn string `yaml:"dsn"`
	} `yaml:"database"`
}
