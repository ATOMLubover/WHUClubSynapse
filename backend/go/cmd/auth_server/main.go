package main

import (
	"log/slog"
	"strconv"
	"whuclubsynapse-server/internal/auth_server/authconfig"
	"whuclubsynapse-server/internal/auth_server/grpcimpl"
	"whuclubsynapse-server/internal/auth_server/handler"
	"whuclubsynapse-server/internal/auth_server/redisimpl"
	"whuclubsynapse-server/internal/auth_server/repo"
	"whuclubsynapse-server/internal/auth_server/service"
	"whuclubsynapse-server/internal/shared/config"
	"whuclubsynapse-server/internal/shared/logger"
	"whuclubsynapse-server/internal/shared/rediscli"

	"github.com/kataras/iris/v12"
	"github.com/kataras/iris/v12/mvc"
	"gorm.io/driver/postgres"
	"gorm.io/gorm"
)

func main() {
	app := iris.Default()
	globalController := mvc.New(app.Party("/"))

	config := LoadConfig("../config/auth_config.yaml")

	logger := CreateLogger(config)
	database := ConnectDatabase(config)

	redisService := redisimpl.NewRedisClientService(config, logger)

	userRepo := repo.CreateUserRepo(database, logger)

	userService := service.NewUserService(userRepo)
	mailvrfService := grpcimpl.NewMailvrfClientService(config, logger)

	globalController.Register(
		config,

		logger,
		database,

		userRepo,

		redisService,
		userService,
		mailvrfService,
	)

	{
		authController := globalController.Party("/user")
		authController.Handle(new(handler.UserHandler))
	}

	app.Listen(":8080")
}

func LoadConfig(relPath string) *authconfig.Config {
	var cfg authconfig.Config
	if err := config.LoadConfig(&cfg, relPath); err != nil {
		panic(err.Error())
	}

	return &cfg
}

func CreateLogger(cfg *authconfig.Config) *slog.Logger {
	return logger.CreateLogger(nil)
}

func ConnectDatabase(cfg *authconfig.Config) *gorm.DB {
	db, err := gorm.Open(
		postgres.Open(cfg.Database.Dsn),
		&gorm.Config{},
	)
	if err != nil {
		panic(err.Error())
	}

	return db
}

func ConnectRedis(cfg *authconfig.Config) rediscli.RedisClient {
	return *rediscli.NewRedisClient(
		cfg.Redis.Host+":"+strconv.FormatUint(uint64(cfg.Redis.Port), 10),
		cfg.Redis.Password,
		cfg.Redis.MaxConn,
		cfg.Redis.MinIdle,
		cfg.Redis.MaxRetries,
	)
}
