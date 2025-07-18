package baseconfig

type Config struct {
	EnvLevel string `mapstructure:"env_level"`

	ServerPort string `mapstructure:"server_port"`

	DatabaseDsn string `mapstructure:"database_dsn"`

	RedisHost       string `mapstructure:"redis_host"`
	RedisPort       uint16 `mapstructure:"redis_port"`
	RedisPassword   string `mapstructure:"redis_password"`
	RedisDb         int    `mapstructure:"redis_db"`
	RedisMaxConn    int    `mapstructure:"redis_max_conn"`
	RedisMinIdle    int    `mapstructure:"redis_min_idle"`
	RedisMaxRetries int    `mapstructure:"redis_max_retries"`

	GrpcHost        string `mapstructure:"grpc_host"`
	GrpcPort        uint16 `mapstructure:"grpc_port"`
	GrpcMaxConn     int    `mapstructure:"grpc_max_conn"`
	GrpcMinConn     int    `mapstructure:"grpc_min_conn"`
	GrpcIdleTimeout int    `mapstructure:"grpc_idle_timeout"`

	JwtExpirationTime uint64 `mapstructure:"jwt_expiration_time"`
	JwtSecretKey      string `mapstructure:"jwt_secret_key"`

	LlmAddr string `mapstructure:"llm_addr"`
	RagAddr string `mapstructure:"rag_addr"`
}
