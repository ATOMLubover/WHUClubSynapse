package main

import (
	"log/slog"
	"whuclubsynapse-server/internal/auth_server/authconfig"
	"whuclubsynapse-server/internal/auth_server/handler"
	"whuclubsynapse-server/internal/shared/config"
	"whuclubsynapse-server/internal/shared/logger"

	"github.com/kataras/iris/v12"
	"github.com/kataras/iris/v12/mvc"
	"gorm.io/driver/postgres"
	"gorm.io/gorm"
)

func main() {
	app := iris.New()
	globalController := mvc.New(app.Party("/"))

	config := LoadConfig("../config/auth_config.yaml")
	logger := CreateLogger(config)
	database := ConnectDatabase(config)

	globalController.Register(
		config,
		logger,
		database,
	)

	{
		authController := globalController.Party("/auth")
		authController.Handle(new(handler.UserHandler))
	}
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
